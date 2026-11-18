# Betsbot – Plan

Status: planering inför Fas 0 · Uppdaterad: 2026-11-18

## 1. Mål och avgränsning

**Mål:** ett system som dygnet runt hittar spel med positivt förväntat värde (value) hos svensklicensierade spelbolag och skickar färdiga spelförslag till mobilen. Du lägger spelet med några tryck.

**Utanför scope:**

- **Automatisk placering hos spelbolag.** Det bryter mot bolagens villkor (se §3).
- **Spel på betting exchange.** Börsen är i praktiken referenspriset och ger sällan value med vår metod. Den används bara som datakälla.
- **Livespel.** Det kräver placering inom sekunder och går inte att göra manuellt.
- **Kombinationsspel.** Bolagets marginal multipliceras för varje led, så vi spelar bara singlar.

## 2. Beslut

| Område | Beslut | Status |
|---|---|---|
| Spelbolag | Svensklicensierade. Vilka avgörs av data i Fas 0. | Taget |
| Automatik | Halvautomatik: systemet föreslår, du placerar. Ingen exchange. | Taget |
| Kassa | 1 000–2 000 kr (rekommenderat: 2 000 kr), max 1 unit per spel | Taget |
| Unit-storlek | 50 kr fast | Taget |
| Databudget | 0 kr. Bara gratis och tillåtna källor (se §8). | Taget |
| Sporter | Fotboll först. Därefter ishockey, basket och tennis, en i taget. | Taget |
| Drift | Egen server med befintlig vakthund, alternativt VPS för ~50 kr/mån | Taget |

## 3. Ramvillkor (kontrollerat 2026-11-18)

| Fakta | Konsekvens |
|---|---|
| bet365:s villkor, även de svenska, förbjuder bots, AI, hjälpprogram och scraping. Följden kan bli fryst konto, ogiltiga spel, innehållna vinster eller stängt konto. | Ingen automatisk placering och ingen scraping. Odds köps från leverantör. |
| Inget svensklicensierat sportbolag med öppet API för att lägga spel har hittats. Pinnacle stängde sitt publika API den 23 juli 2025. | Halvautomatik. |
| Pinnacle har svensk licens (pinnacle.se, PinBet (Sverige) Ltd). | Pinnacle används som referens för rättvisa odds. Vi spelar inte där. |
| Oddsaggregatorer skrapar bolagens interna gränssnitt och sprider anropen över tusentals roterande IP-adresser (proxies) för att inte bli blockerade. | Görs inte här. Det bryter bolagens villkor och innebär att kringgå deras blockering. Ett test mot sådana gränssnitt stoppades av utvecklingsmiljön som obehörig åtkomst. |
| Bolag begränsar konton som vinner över tid. | Logga begränsningar per konto och ha 1–2 reservbolag. |
| Vinster hos svensklicensierade bolag är skattefria. Insättningsgräns är obligatorisk. | Spela bara hos svensklicensierade bolag. Sätt insättningsgränsen lika med kassan. |

Övriga bolags villkor är inte genomlästa ord för ord. Det görs innan något konto öppnas.

## 4. Metod: value mot skarp marknad

1. Hämta odds från den skarpa marknaden: Betfair-börsen och Pinnacle, som har låg marginal och tar emot professionella spelare.
2. Räkna bort marginalen. Det ger en rättvis sannolikhet *p* per utfall.
3. Jämför med de svenska bolagens odds: **EV = p × odds − 1**.
4. Skicka signal om EV ≥ tröskeln (start: 3 %) och alla kontroller passerar.
5. Mät **CLV** (closing line value): fick vi bättre odds än stängningsoddset? Det är det tidigaste beviset på att systemet fungerar.

Vi analyserar inte lagen själva. Den skarpa marknaden har redan prisat in statistik, matchfakta och lagnyheter. Vår fördel är att vissa bolag uppdaterar sina odds långsammare.

## 5. Agenter

Allt som rör pengar är deterministisk kod. En AI-modell används bara för text och bedömningar, och först i Fas 3.

| Agent | Jobb | Typ | Fas |
|---|---|---|---|
| Sökagent | Bevakar Betfair-priser löpande. När den skarpa marknaden rör sig hämtas den ligans odds från gratis-API:erna. Matchar event och marknader mellan källorna. | Kod | 0 |
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
| 1 unit | 50 kr (fast) | Ditt beslut. Se risktabellen nedan. |
| Max insats per spel | 1 unit (½ unit vid odds > 4,0) | Variansen ökar med oddset |
| Spel per match | Max 1 | Undviker korrelerade spel |
| Signaler per dag | Max 15 | Skydd mot buggar och felaktig data |
| Öppen exponering | Max 10 units | Samma skäl |
| Kassan −30 % från start | Systemet pausar och vi granskar | Nödstopp |

Risk att någon gång förlora hela kassan med 50 kr per spel, givet odds runt 2,0 och att systemet verkligen har 3 % edge:

| Kassa | 50 kr som andel av kassan | Risk att förlora allt |
|---|---|---|
| 1 000 kr | 5 % | ~30 % |
| **2 000 kr (rekommenderat)** | **2,5 %** | **~9 %** |

Som jämförelse ger 2 % av kassan ungefär 5 % risk och 10 % av kassan ungefär 55 % risk.

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

## 8. Data (0 kr)

### Hur aggregatorerna gör

1. De läser samma data som bolagens egna sajter laddar, via bolagens interna gränssnitt.
2. Bolagen blockerar det aktivt, så anropen sprids över tusentals roterande IP-adresser (proxies).
3. Ett team lagar skraparna varje gång en sajt ändras.

Det man betalar för i ett oddsflöde är alltså döljandet och underhållet, inte själva oddsen. Vi kopierar inte det upplägget (se §3).

### Gratis och tillåtna källor

| Källa | Vad den ger | Kostnad | Begränsning |
|---|---|---|---|
| Betfair Exchange API, fördröjd nyckel | Skarpa back- och lay-priser för hela marknaden, fördröjda 1–180 s | 0 kr | Kräver Betfair-konto, men bara för data och inget spel där. Endast personligt bruk. Ger inte omsatt volym, så likviditeten bedöms via skillnaden mellan back- och lay-pris. |
| The Odds API, gratisnivå | Odds per liga från EU-bolag, bland annat Pinnacle och Unibet | 0 kr | 500 krediter/mån, ungefär 16 anrop per dag. En kredit = en liga, en marknad, en region. |
| OddsPapi, gratisnivå | Enligt leverantören 350+ bolag, inklusive Pinnacle | 0 kr | Ungefär 250 anrop/mån enligt uppgift. Täckningen av svenska bolag är inte verifierad. |

### Upplägg: följ den skarpa marknaden och fråga riktat

- Betfair bevakas hela tiden, gratis.
- När ett skarpt pris rör sig tydligt läggs ett av de få gratisanropen på just den ligan, för att se om de svenska bolagen ligger efter. Det är då value uppstår.
- Det ger runt 25 riktade kontroller per dag i stället för blinda anrop.

### Kontrolleras i Fas 0

- Att Betfair tar emot kunder från Sverige i dag och att API-villkoren tillåter vårt användningssätt (personligt bruk).
- Att Unibets odds i The Odds API (EU) stämmer med unibet.se.
- Vilka svenska bolag OddsPapi faktiskt täcker.
- Om gratisdatan ger tillräckligt många signaler (se §9).

## 9. Faser och beslutspunkter

| Fas | Innehåll | Kriterium för att gå vidare |
|---|---|---|
| 0: Bygg och mät (2–3 v) | Repo, Betfair-bevakning, riktade anrop, value-motor, databas. Fotboll, plus loggning av övriga sporter om kvoten räcker. | Vi vet hur många value-tillfällen med EV ≥ 3 % gratisdatan ger per dag och vilka bolag som oftast har value. Tillfällena måste stå öppna länge nog för manuell placering (startkrav: median ≥ 5 min). Under 2 signaler per dag: nytt beslut om datan. |
| 1: Papper (3–4 v) | Signaler till Telegram, inga pengar. | Snitt-CLV ≥ +1,5 % över minst 300 signaler. |
| 2: Skarpt (4–8 v) | 2 % unit, manuell placering, 1–2 bolag. | CLV håller på riktiga spel. Slippage under 30 % (startvärde). |
| 3: Utöka | Fler sporter och bolag, analys- och statistikagent. | Per sport enligt §7. |

**Stoppregel:** om CLV ≤ 0 efter 300 signaler stoppar vi eller byter metod, innan några riktiga pengar satsas.

## 10. Ekonomi

Antaganden: 50 kr per spel, 3 % edge i snitt och 0 kr i datakostnad. Hur många signaler gratisdatan ger mäts i Fas 0.

| Signaler per dag | Spel per mån | Omsättning per mån | Förväntad vinst per mån |
|---|---|---|---|
| 3 | ~90 | ~4 500 kr | ~+135 kr |
| 5 | ~150 | ~7 500 kr | ~+225 kr |
| 10 | ~300 | ~15 000 kr | ~+450 kr |

Ingen datakostnad äter av vinsten. Svängningarna från månad till månad är ändå större än den förväntade vinsten, så resultatet bedöms på CLV och inte på saldot.

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
- Signaler per gratisanrop, det vill säga hur väl Betfair-bevakningen träffar.

## 13. Att göra (du)

1. Öppna ett Betfair-konto och skapa en fördröjd applikationsnyckel. Kontot används bara för data.
2. Registrera en gratisnyckel hos The Odds API.
3. Senare: skapa en Telegram-bot via BotFather.

Nycklarna läggs i `.env` på servern och skickas aldrig i chatten.

## Källor

- bet365 villkor (Sverige): https://help.bet365.com/s/en-se/terms-and-conditions
- Pinnacle, publikt API stängt 2025-07-23: https://github.com/pinnacleapi/pinnacleapi-documentation
- Pinnacle tillbaka i Sverige med licens: https://igamingbusiness.com/sports-betting/pinnacle-relaunches-in-sweden-after-two-year-absence/
- Spelinspektionen, anmärkning för PinBet (Sverige) Ltd 2025: https://www.spelinspektionen.se/globalassets/dokument/tillsynsbeslut/varning-anmarkning/pinbet---beslut-om-anmarkning-251512.pdf
- The Odds API (planer och bolag): https://the-odds-api.com/
- Betfair, applikationsnycklar (fördröjd nyckel): https://betfair-developer-docs.atlassian.net/wiki/x/URAp
- The Odds API, gratisnivåns gränser: https://oddspapi.io/blog/the-odds-api-free-tier-limits
- OddsPapi, gratisnivå: https://oddspapi.io/blog/?p=144
- Proxies och skrapning av odds: https://databay.com/blog/proxies-for-sports-betting-odds
