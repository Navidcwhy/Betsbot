"""Tester för value-matematiken i scripts/check_free_data.py (inget nätverk)."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_free_data.py"
spec = importlib.util.spec_from_file_location("check_free_data", SCRIPT)
cfd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cfd)


def book(key, prices):
    return {
        "key": key,
        "title": key.capitalize(),
        "markets": [{
            "key": "h2h",
            "outcomes": [{"name": n, "price": p} for n, p in prices.items()],
        }],
    }


EVENT = {
    "home_team": "Hemma",
    "away_team": "Borta",
    "commence_time": "2026-11-21T15:00:00Z",
    "bookmakers": [
        book("pinnacle", {"Hemma": 2.00, "Draw": 3.60, "Borta": 4.00}),
        book("unibet_eu", {"Hemma": 2.15, "Draw": 3.40, "Borta": 3.90}),
        book("softbook", {"Hemma": 1.90, "Draw": 3.50, "Borta": 5.00}),
        book("twoway", {"Hemma": 2.50, "Borta": 4.50}),
    ],
}


class DevigTest(unittest.TestCase):
    def test_fair_probabilities_sum_to_one(self):
        fair = cfd.devig({"Hemma": 2.00, "Draw": 3.60, "Borta": 4.00})
        self.assertAlmostEqual(sum(fair.values()), 1.0)

    def test_margin_removed_proportionally(self):
        fair = cfd.devig({"Hemma": 2.00, "Draw": 3.60, "Borta": 4.00})
        total = 1 / 2.00 + 1 / 3.60 + 1 / 4.00
        self.assertAlmostEqual(fair["Hemma"], (1 / 2.00) / total)


class ScanEventTest(unittest.TestCase):
    def test_finds_value_and_flags_suspect(self):
        found = {(c["book"], c["outcome"]): c for c in cfd.scan_event(EVENT, 0.03)}
        self.assertEqual(set(found), {("Unibet_eu", "Hemma"), ("Softbook", "Borta")})
        self.assertAlmostEqual(found[("Unibet_eu", "Hemma")]["ev"], 0.0459, places=3)
        self.assertFalse(found[("Unibet_eu", "Hemma")]["suspect"])
        self.assertTrue(found[("Softbook", "Borta")]["suspect"])

    def test_skips_market_with_other_outcomes(self):
        books = {c["book"] for c in cfd.scan_event(EVENT, 0.0)}
        self.assertNotIn("Twoway", books)

    def test_no_reference_no_signals(self):
        event = dict(EVENT, bookmakers=EVENT["bookmakers"][1:])
        self.assertEqual(cfd.scan_event(event, 0.0), [])


if __name__ == "__main__":
    unittest.main()
