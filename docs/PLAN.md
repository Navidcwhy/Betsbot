# Betsbot – Plan

Status: planering inför Fas 0 · Uppdaterad: 2026-11-18

## 1. Mål och avgränsning

**Mål:** ett system som dygnet runt hittar spel med positivt förväntat värde (value) hos svensklicensierade spelbolag och skickar färdiga spelförslag till mobilen. Du lägger spelet med några tryck.

**Utanför scope:**

- **Automatisk placering hos spelbolag.** Det bryter mot bolagens villkor (se §3).
- **Betting exchange.** Den är i praktiken referenspriset och ger sällan value med vår metod.
- **Livespel.** Det kräver placering inom sekunder och går inte att göra manuellt.
- **Kombinationsspel.** Bolagets marginal multipliceras för varje led, så vi spelar bara singlar.

## 2. Beslut

| Område | Beslut | Status |
|---|---|---|
| Spelbolag | Svensklicensierade. Vilka avgörs av data i Fas 0. | Taget |
| Automatik | Halvautomatik: systemet föreslår, du placerar. Ingen exchange. | Taget |
| Kassa | 1 000–2 000 kr, max 1 unit per spel | Taget |
| Unit-storlek | 2 % av aktuell kassa (i stället för 10 %) | Föreslaget, väntar på OK |
| Databudget | 0 kr under bygget, sedan en betald mätmånad (≈300–600 kr) | Föreslaget, väntar på OK |
| Sporter | Fotboll först. Därefter ishockey, basket och tennis, en i taget. | Taget |
| Drift | Egen server med befintlig vakthund, alternativt VPS för ~50 kr/mån | Taget |

## 3. Ramvillkor (kontrollerat 2026-11-18)

| Fakta | Konsekvens |
|---|---|
| bet365:s villkor, även de svenska, förbjuder bots, AI, hjälpprogram och scraping. Följden kan bli fryst konto, ogiltiga spel, innehållna vinster eller stängt konto. | Ingen automatisk placering och ingen scraping. Odds köps från leverantör. |
| Inget svensklicensierat sportbolag med öppet API för att lägga spel har hittats. Pinnacle stängde sitt publika API den 23 juli 2025. | Halvautomatik. |
| Pinnacle har svensk licens (pinnacle.se, PinBet (Sverige) Ltd). | Pinnacle används som referens för rättvisa odds. Vi spelar inte där. |
| Bolag begränsar konton som vinner över tid. | Logga begränsningar per konto och ha 1–2 reservbolag. |
| Vinster hos svensklicensierade bolag är skattefria. Insättningsgräns är obligatorisk. | Spela bara hos svensklicensierade bolag. Sätt insättningsgränsen lika med kassan. |

Övriga bolags villkor är inte genomlästa ord för ord. Det görs innan något konto öppnas.

## 4. Metod: value mot skarp marknad

1. Hämta odds från den skarpa marknaden: Pinnacle, som har låg marginal och tar emot professionella spelare.
2. Räkna bort marginalen. Det ger en rättvis sannolikhet *p* per utfall.
3. Jämför med de svenska bolagens odds: **EV = p × odds − 1**.
4. Skicka signal om EV ≥ tröskeln (start: 3 %) och alla kontroller passerar.
5. Mät **CLV** (closing line value): fick vi bättre odds än stängningsoddset? Det är det tidigaste beviset på att systemet fungerar.

Vi analyserar inte lagen själva. Den skarpa marknaden har redan prisat in statistik, matchfakta och lagnyheter. Vår fördel är att vissa bolag uppdaterar sina odds långsammare.

## 5. Agenter

Allt som rör pengar är deterministisk kod. En AI-modell används bara för text och bedömningar, och först i Fas 3.

| Agent | Jobb | Typ | Fas |
|---|---|---|---|
| Sökagent | Hämtar odds (svenska bolag och Pinnacle). Matchar event och marknader mellan källorna. | Kod | 0 |
| Value-beräknare | Räknar bort marginalen, räknar EV och sätter lägsta godtagbara odds. | Kod | 0 |
| Regelkontroll | Spärrar marknader där reglerna skiljer sig mellan bolag. Flaggar EV > 15 % som troligt datafel. | Kod (regeltabell) | 1 |
| Riskagent | Insats, gränser, exponering och nödstopp. Har veto över allt. | Kod | 1 |
| Signalagent | Telegram-meddelande med knapparna Lagt/Missat. | Kod | 1 |
| Uppföljningsagent | Stängningsodds, CLV, resultat, saldo, begränsningar och dagsrapport. | Kod | 1 |
| Samordnare | Schemaläggning, hälsosignal (heartbeat), larm och loggning. | Kod | 0 |
| Analysagent | Nyheter, skador och laguppställningar som extra spärr. | Lokal AI-modell | 3 |
| Statistikagent | Egna modeller som andra åsikt. Justerar trösklar per sport. | Kod/ML | 3 |

### Exempel på signal

```
Arsenal – Chelsea · Premier League · lör 18:30
Marknad: Över 2,5 mål
Spela hos: Unibet @ 2,10 (lägsta OK: 2,02)
Rättvist odds: 1,98 → value +6,1 %
Insats: 40 kr (1 unit)
[Lagt]  [Missat]
```

Undersöks i Fas 0: om bolagen stöder länkar som lägger spelet direkt i kupongen. Då räcker ett tryck.

## 6. Riskregler

| Regel | Värde | Varför |
|---|---|---|
| 1 unit | 2 % av aktuell kassa, räknas om varje måndag | Se tabellen nedan |
| Max insats per spel | 1 unit (½ unit vid odds > 4,0) | Variansen ökar med oddset |
| Spel per match | Max 1 | Undviker korrelerade spel |
| Signaler per dag | Max 15 | Skydd mot buggar och felaktig data |
| Öppen exponering | Max 10 units | Samma skäl |
| Kassan −30 % från start | Systemet pausar och vi granskar | Nödstopp |

Risk att någon gång förlora hela kassan, givet platta insatser, odds runt 2,0 och att systemet verkligen har 3 % edge:

| Unit | Insats vid 1 000 kr | Insats vid 2 000 kr | Risk att förlora allt |
|---|---|---|---|
| 10 % | 100 kr | 200 kr | ~55 % |
| 5 % | 50 kr | 100 kr | ~30 % |
| **2 % (förslag)** | **20 kr** | **40 kr** | **~5 %** |
| 1 % | 10 kr | 20 kr | < 1 % |

Om systemet saknar edge tar kassan förr eller senare slut, oavsett unit. Med en liten unit hinner CLV visa det innan pengarna är borta.

## 7. Sporter

Bara spel före matchstart (pre-match).

| Sport | Start | Regelfälla att hantera |
|---|---|---|
| Fotboll | Signaler från Fas 1 | Asiatiskt handikapp jämfört med vanligt handikapp. Regler för ogiltiga spel. |
| Ishockey | Loggas från Fas 0. Signaler när datan håller. | Ordinarie tid (60 min) jämfört med inklusive förlängning och straffar. |
| Basket | Som ishockey | Oftast inklusive förlängning. Kontrolleras per bolag. |
| Tennis | Som ishockey | Olika regler när en spelare bryter matchen. Tunna marknader i lägre serier. |

En sport får signaler först när två villkor är uppfyllda: reglerna är mappade, och Fas 1-kriteriet är uppfyllt för just den sporten.

## 8. Data

| Alternativ | Pris | Kommentar |
|---|---|---|
| The Odds API, gratis | 0 kr, 500 krediter/mån | Räcker för att bygga, men inte för att fånga value i tid. |
| The Odds API, betald | $30 (20k krediter) eller $59 (100k krediter) per mån | EU-regionen har Pinnacle (hämtas från den publika sajten, viss fördröjning) och Unibet. Betsson, NordicBet m.fl. är inte verifierade. |
| Andra (OddsPapi, odds-api.io m.fl.) | Varierar, vissa har gratisnivå | Jämförs i Fas 0. |

En kredit motsvarar ett anrop för en sport eller liga, en marknad och en region. Leverantörens täckning avgör vilka bolag vi kan leta value hos.

## 9. Faser och beslutspunkter

| Fas | Innehåll | Kriterium för att gå vidare |
|---|---|---|
| 0: Bygg och mät (2–3 v) | Repo, datainsamling, value-motor, databas. Fotboll, plus loggning av övriga sporter om kvoten räcker. | Vi vet hur många value-tillfällen med EV ≥ 3 % som finns per dag och vilka bolag som oftast har value. Tillfällena måste stå öppna länge nog för manuell placering (startkrav: median ≥ 5 min). |
| 1: Papper (3–4 v) | Signaler till Telegram, inga pengar. | Snitt-CLV ≥ +1,5 % över minst 300 signaler. |
| 2: Skarpt (4–8 v) | 2 % unit, manuell placering, 1–2 bolag. | CLV håller på riktiga spel. Slippage under 30 % (startvärde). |
| 3: Utöka | Fler sporter och bolag, analys- och statistikagent. | Per sport enligt §7. |

**Stoppregel:** om CLV ≤ 0 efter 300 signaler stoppar vi eller byter metod, innan några riktiga pengar satsas.

## 10. Ekonomi med vald kassa

Antaganden: 3 % edge i snitt, ~10 spel per dag, ~300 spel per månad.

| Kassa | Insats | Omsättning/mån | Förväntad vinst/mån |
|---|---|---|---|
| 1 000 kr | 20 kr | ~6 000 kr | ~+180 kr |
| 2 000 kr | 40 kr | ~12 000 kr | ~+360 kr |

Betald oddsdata (≈300–600 kr/mån) äter i stort sett hela den förväntade vinsten. Testperioden går alltså i bästa fall ungefär jämnt ut. Det är priset för att få veta om systemet fungerar. En större kassa först när CLV är bevisad.

## 11. Teknik och drift

- Python (asyncio), PostgreSQL för oddshistorik, Telegram-bot och Docker Compose.
- Ingen AI-modell i MVP:n, så det räcker med 1 vCPU, ~1 GB RAM och en server som alltid är på. Egen server eller VPS.
- Körs det på samma server som tradingboten får det en egen container med minnestak och egna nycklar. Ett fel här får aldrig påverka tradingen. Hälsosignal som den befintliga vakthunden kan övervaka, plus automatisk omstart i Docker.
- Hemligheter (API-nycklar, Telegram-token) ligger i `.env` och checkas aldrig in i git.
- Allt loggas: odds vid signal, vid placering och vid stängning. Den datan är den verkliga tillgången.

## 12. KPI:er

- CLV: snitt, och andel spel som slår stängningsoddset. Primärt mått.
- Snitt-EV vid signal.
- Slippage: andel signaler där oddset hunnit ändras före placering.
- Tid från signal till placering.
- Avkastning och största nedgång (släpande mått).
- Antal dagar innan ett konto begränsas.
- Datakostnad i förhållande till förväntad vinst.

## Källor

- bet365 villkor (Sverige): https://help.bet365.com/s/en-se/terms-and-conditions
- Pinnacle, publikt API stängt 2025-07-23: https://github.com/pinnacleapi/pinnacleapi-documentation
- Pinnacle tillbaka i Sverige med licens: https://igamingbusiness.com/sports-betting/pinnacle-relaunches-in-sweden-after-two-year-absence/
- Spelinspektionen, anmärkning för PinBet (Sverige) Ltd 2025: https://www.spelinspektionen.se/globalassets/dokument/tillsynsbeslut/varning-anmarkning/pinbet---beslut-om-anmarkning-251512.pdf
- The Odds API (planer och bolag): https://the-odds-api.com/
