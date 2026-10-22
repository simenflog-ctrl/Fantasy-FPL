# Beslutning runde 8 (2026/27)

Tatt av Claude 2026-10-22 ca. 16:00 UTC, etter tre runder med Codex (analyse, to kritikkrunder).
Prognosen er frosset i `prognose/prognose_R8.json` (sjekksummer i `prognose/SHA256SUMS`) og skal ikke endres etter fristen.

## Handling nå

| | |
|---|---|
| Bytte | **Szoboszlai (salg £6,8m) → Tavernier (£6,2m)** |
| Poengtrekk | 0 |
| Bank etter bytte | £1,6m |
| Gratisbytter til R9 | 2 (ett rulles) |
| Wildcard | **Holdes.** Foreløpig plan: R11 |
| Andre chips | Ingen nå |

**Startellever (3-5-2):** Verbruggen; Calafiori, Konsa, N.Williams; B.Fernandes, Mbeumo, Tavernier, Le Fée, Groß; Haaland, Thiago.
**Kaptein:** Haaland. **Visekaptein:** B.Fernandes.
**Benk:** Steele (GK); 1. Maguire, 2. van Ewijk, 3. Kusi-Asare.

## Rullerende plan R8–R15 (alt etter R8 er foreløpig)

| Runde | Frist (UTC) | Plan |
|---|---|---|
| R8 | 23. okt 17:30 | Szoboszlai → Tavernier. Rull ett gratisbytte. |
| R9 | 31. okt 11:00 | *Foreløpig:* bruk gratisbytter bare på akutte fravær. Ellers rull; spillere som kjøpes nå, kan uansett byttes ut med WC i R11. |
| R10 | – | *Foreløpig:* som R9. |
| R11 | – | *Foreløpig:* **Wildcard.** Bygg for R11–R19: lettere program for BRE, LIV, LEE fra R14; tyngre for COV, IPS, TOT. Bygg en spillende benk for Bench Boost. |
| R12–R14 | – | *Foreløpig:* gratisbytter etter behov. |
| R15 | 12. des | *Foreløpig:* **Bench Boost** (før juleperioden; modellene valgte R15 eller R19). |
| R13 eller R17–R19 | – | *Foreløpig:* **Free Hit** holdes som beredskap til juleperioden eller en blank runde; senest R19. |

WC1, FH1 og BB1 utløper etter R19 og skal brukes innen da.

## Hvorfor

**Byttet:** Szoboszlai er ute i flere uker (FPL: 0 %; Sports Mole 19. okt). Byttet er positivt i begge poengmodellene og i
alle testede scenarioer bortsett fra et der Tavernier mister halve spilletiden. Dewsbury-Hall er nesten likeverdig (−1 til −5 poeng R8–19)
og er reserven hvis Tavernier får skadeflagg før fristen.

**Spare begge byttene (referansen):** gir 1,4–1,7 poeng mindre i R8 og 7–10 mindre i R8–R11 med samme ellever,
fordi Maguire (≈ 3 xP) må starte i stedet for Tavernier (≈ 5 xP).

**Andre bytte nå (Thiago → João Pedro / Calvert-Lewin):** +7–10 poeng i en statisk modell, men Thiago har 3,69 xG på 18 poeng og sikker spilletid,
og byttet ville trolig blitt reversert eller overflødig med WC i R11. Rullet gratisbytte holder fleksibiliteten.

**Wildcard nå (beste alternativ):** Leder i alle Codex' tester, men lite: +2 til +7 poeng over R8–R19 med like chipdatoer, og bare
+1 til +4 for en konkret tropp som må fungere i begge poengmodellene. Den troppen som var best i Codex' modell, tapte 12,5 poeng i repoets.
Skadesimuleringen (300 trekk) ga ingen fordel ved å vente; der tok Claude feil. Forskjellen er mindre enn usikkerheten i én spillerrolle
(João Pedro var ute i R5; Thomas-Asante har p_start 0,61). Ved så små marginer foretrekkes muligheten til å velge troppen med tre runder mer informasjon.
**Dette er en skjønnsmessig avveining, ikke et beregnet resultat**: modellene sier at å holde koster 2–7 forventede poeng.

## Forventning (modellresultater, ikke observasjoner)

| | Codex-modell | Repo-hybrid |
|---|---|---|
| R8, anbefalt | 52,3 | 64,0 |
| R8, referanse uten bytter | 50,9 | 62,3 |
| R8–R11, anbefalt minus referanse (samme ellever) | +6,9 | +9,9 |
| R8–R19, hele planen (WC11, BB, FH) | ≈ 695–698 | ≈ 764–766 |

Forskjellen mellom modellene (≈ 12 poeng per runde) skyldes særlig bonus og toppspillernes rater. Sannheten ligger trolig imellom.

## Usikkerheter

1. **Bonus og toppspillere**: de to modellene er uenige om Haaland (6,1 mot 8,4 per runde) og Fernandes (4,8 mot 7,3).
2. **Taverniers spilletid**: synkende minutter og skadehistorikk. Med halv spilletid er byttet verdt omtrent null.
3. **Pressekonferanser før R8** var ikke holdt da beslutningen ble tatt.
4. **Gratisbytter ved WC/FH**: ikke verifisert i API-et. Testet; endrer ikke konklusjonen.
5. **Ingen blanke eller doble runder** før R19 i dagens oppsett. Cupkamper kan endre det.

## Før fristen

- Byttet kan gjøres **i kveld før prisjusteringen 23:00 UTC (01:00 norsk tid)**. Tavernier stiger trolig (≈ 240 000 kjøp denne runden),
  Szoboszlai faller trolig. Å vente koster trolig £0,1–0,2m.
- Hvis Tavernier får skadeflagg før fristen: ta **Dewsbury-Hall (£6,6m)** i stedet (bank £1,2m).
- Hvis Calafiori eller Konsa er ute: Maguire kommer inn automatisk fra benken. Ingen endring nødvendig.
- Hvis Haaland er tvilsom: gjør Fernandes til kaptein og Mbeumo til visekaptein.

## Uenighet mellom agentene

Codex anbefalte først å holde, deretter en svak WC nå (runde 1), og til slutt å holde (runde 2).
Claude var for å holde hele veien, men to av Claudes argumenter falt: chipdatoene forklarer bare en del av WC-fordelen, og skader gjør
ikke ventingen mer verdt. Sluttbeslutningen er felles, men begrunnet med skjønn ved liten margin, ikke med at modellene favoriserer å holde.
