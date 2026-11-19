#!/usr/bin/env python3
"""Snabbtest av gratis oddsdata från The Odds API.

Visar för en liga:
  1. vilka bolag gratisnivån ger,
  2. om Pinnacle (referenspriset) finns med,
  3. eventuella value-spel just nu: EV >= tröskeln mot Pinnacles rättvisa odds.

Kostar 1 av 500 gratiskrediter per körning. Med --ligor listas tillgängliga
ligor; det anropet räknas inte mot kvoten enligt The Odds API:s dokumentation.

Användning:
  1. Skapa en gratisnyckel på https://the-odds-api.com
  2. Lägg den i filen .env i repots rot:  ODDS_API_KEY=din_nyckel
  3. Kör:
       python3 scripts/check_free_data.py --ligor
       python3 scripts/check_free_data.py [liga] [min_ev]
     Exempel: python3 scripts/check_free_data.py soccer_epl 0.03

Skriptet skriver aldrig ut nyckeln. Utskriften går att dela.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from email.message import Message
from pathlib import Path

API_BASE = "https://api.the-odds-api.com/v4"
SHARP_BOOK = "pinnacle"
DEFAULT_SPORT = "soccer_epl"
DEFAULT_MIN_EV = 0.03
MAX_SANE_EV = 0.15  # Högre än så är oftast datafel eller regelskillnad.
OUR_SPORT_GROUPS = {"Soccer", "Ice Hockey", "Basketball", "Tennis"}


def load_api_key() -> str:
    key = os.environ.get("ODDS_API_KEY", "").strip()
    if key:
        return key
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            name, sep, value = line.partition("=")
            if sep and name.strip() == "ODDS_API_KEY":
                return value.strip().strip('"').strip("'")
    sys.exit("Ingen nyckel hittad. Lägg ODDS_API_KEY=... i filen .env i repots rot.")


def fetch(path: str, params: dict) -> tuple[object, Message]:
    url = f"{API_BASE}{path}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response), response.headers
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="replace")
        sys.exit(f"API-fel {err.code}: {body}")
    except urllib.error.URLError as err:
        sys.exit(f"Nätverksfel: {err.reason}")


def devig(prices: dict[str, float]) -> dict[str, float]:
    """Rättvisa sannolikheter: marginalen tas bort proportionellt (multiplikativ metod)."""
    implied = {name: 1.0 / price for name, price in prices.items()}
    total = sum(implied.values())
    return {name: p / total for name, p in implied.items()}


def h2h_prices(bookmaker: dict) -> dict[str, float]:
    for market in bookmaker.get("markets", []):
        if market.get("key") == "h2h":
            return {o["name"]: float(o["price"]) for o in market.get("outcomes", [])}
    return {}


def scan_event(event: dict, min_ev: float) -> list[dict]:
    """Jämför varje bolags pris mot Pinnacles rättvisa odds för en match."""
    books = {b["key"]: b for b in event.get("bookmakers", [])}
    sharp = books.get(SHARP_BOOK)
    if not sharp:
        return []
    sharp_prices = h2h_prices(sharp)
    if len(sharp_prices) < 2:
        return []
    fair = devig(sharp_prices)

    candidates = []
    for key, book in books.items():
        if key == SHARP_BOOK:
            continue
        prices = h2h_prices(book)
        # Samma utfall krävs, annars är det inte samma marknad (t.ex. utan oavgjort).
        if set(prices) != set(fair):
            continue
        for outcome, price in prices.items():
            ev = fair[outcome] * price - 1.0
            if ev >= min_ev:
                candidates.append({
                    "match": f"{event.get('home_team')} – {event.get('away_team')}",
                    "start": event.get("commence_time", ""),
                    "outcome": outcome,
                    "book": book.get("title", key),
                    "price": price,
                    "fair_odds": 1.0 / fair[outcome],
                    "ev": ev,
                    "suspect": ev > MAX_SANE_EV,
                })
    return candidates


def local_time(iso_utc: str) -> str:
    try:
        from zoneinfo import ZoneInfo

        moment = datetime.fromisoformat(iso_utc.replace("Z", "+00:00"))
        local = moment.astimezone(ZoneInfo("Europe/Stockholm"))
        weekday = ["mån", "tis", "ons", "tor", "fre", "lör", "sön"][local.weekday()]
        return f"{weekday} {local:%d/%m %H:%M}"
    except Exception:
        return iso_utc


def sv_number(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


def list_leagues(key: str) -> None:
    sports, _ = fetch("/sports/", {"apiKey": key})
    ours = [s for s in sports if s.get("group") in OUR_SPORT_GROUPS and s.get("active")]
    print(f"Aktiva ligor i våra sporter ({len(ours)}):")
    for sport in sorted(ours, key=lambda s: (s["group"], s["key"])):
        print(f"  {sport['key']:<45} {sport['group']}: {sport['title']}")


def check_league(key: str, sport: str, min_ev: float) -> None:
    events, headers = fetch(f"/sports/{sport}/odds/", {
        "apiKey": key,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal",
    })
    print(f"Liga: {sport} · {len(events)} kommande matcher")
    print(f"Krediter kvar denna månad: {headers.get('x-requests-remaining', '?')}")

    seen: dict[str, str] = {}
    with_sharp = 0
    for event in events:
        keys = {b["key"] for b in event.get("bookmakers", [])}
        with_sharp += SHARP_BOOK in keys
        for book in event.get("bookmakers", []):
            seen[book["key"]] = book.get("title", book["key"])

    print(f"\nBolag i gratisdatan ({len(seen)}):")
    for book_key in sorted(seen):
        print(f"  {book_key:<22} {seen[book_key]}")

    if SHARP_BOOK not in seen:
        print("\nPinnacle saknas. Referenspriset finns inte i gratisdatan för den här ligan.")
        return
    print(f"\nMatcher med Pinnacle-pris: {with_sharp} av {len(events)}")

    candidates = sorted(
        (c for event in events for c in scan_event(event, min_ev)),
        key=lambda c: c["ev"],
        reverse=True,
    )
    print(f"\nValue just nu (EV ≥ {sv_number(min_ev * 100, 1)} %): {len(candidates)} st")
    print("Spela bara hos bolag med svensk licens. Listan visar alla bolag i datan.")
    for c in candidates:
        flag = "  ← trolig felkälla, kontrollera" if c["suspect"] else ""
        print(
            f"  {local_time(c['start'])}  {c['match']}  ·  {c['outcome']}  ·  "
            f"{c['book']} @ {sv_number(c['price'])}  "
            f"(rättvist {sv_number(c['fair_odds'])}, value {sv_number(c['ev'] * 100, 1)} %){flag}"
        )


def main() -> None:
    args = sys.argv[1:]
    key = load_api_key()
    if args and args[0] == "--ligor":
        list_leagues(key)
        return
    sport = args[0] if args else DEFAULT_SPORT
    min_ev = float(args[1]) if len(args) > 1 else DEFAULT_MIN_EV
    check_league(key, sport, min_ev)


if __name__ == "__main__":
    main()
