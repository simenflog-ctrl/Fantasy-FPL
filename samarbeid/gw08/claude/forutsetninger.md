# Forutsetninger fra Claude (oppgave 2)

Skrevet 2026-10-22 15:06 UTC, før Codex' resultater ble lest.

## Kilder og hvor mye de er verdt

| Kilde | Hva den gir | Pålitelighet |
|---|---|---|
| FPL-API `bootstrap-static` (hentet 15:01 UTC) | Skadeflagg, sjanse for å spille, nyhetstekst med dato | Høy for status; FPL oppdaterer etter pressekonferanser |
| FPL-API `element-summary` | Minutter og poeng per runde | Høy (observert) |
| Repoets `minutes.csv` (generert 11:00 UTC) | p_start, forventede minutter | Modell, ikke observasjon |
| [Sports Mole, 19. okt 2026](https://www.sportsmole.co.uk/football/liverpool/injury-news/injuries-and-suspensions/will-szoboszlai-frimpong-play-liverpool-injury-suspension-list-vs-villarreal_607197.html) | Szoboszlai | Middels; én kilde |
| Nettsøk etter pressekonferanser for R8 | Ingen treff fra 2026/27 | Svakhet: pressekonferansene før R8 er stort sett ikke holdt ennå (torsdag/fredag) |

## Egen tropp

| Spiller | Vurdering | Grunnlag |
|---|---|---|
| Szoboszlai | **Ute flere uker.** Forverret hamstringskaden mot Brentford, tatt av i første omgang. Treneren: borte «en tid». Regnes som 0 minutter minst R8–R11. | FPL: i / 0 % (17. okt); Sports Mole 19. okt |
| Kusi-Asare | **Død plass.** 0 minutter i alle 7 runder. Kan ikke regnes som innbytter. | element-summary |
| Steele | Reservekeeper, 0 minutter. Bare relevant om Verbruggen faller ut (samme lag, BHA). | element-summary |
| Haaland | Spilt 619 av 630 min. Sikker starter. | element-summary, flagg 100 % |
| B.Fernandes | 90 min alle runder, men 1–2 poeng i 5 av 7 runder etter 23 i R2. Repoets modell gir ham 7,2 xP per runde, mens FPL-form er 1,0. **Mulig overvurdering i modellen**, se under. | element-summary, xGI/90 0,59 |
| Mbeumo, Groß, Le Fée, Thiago, Verbruggen, N.Williams, Maguire | 90 min nesten hver runde. Sikre startere. | element-summary |
| Thiago | 18 poeng på 3,69 xG. Underpresterer kraftig mot xG; spilletiden er sikker. Ingen grunn til å selge på form alene. | player_matches |
| Calafiori | Roteres litt (66, 80, 81 min). p_start 0,89. | element-summary |
| Konsa | 90 min de fem siste rundene etter en treg start. p_start 0,83. | element-summary |
| van Ewijk | 0 min i R5, ellers 90. COV har lett program (snitt FDR 2,75). | element-summary |
| Maguire | 90 min hver runde, men lavt tak (snitt 2,3 poeng). Svakeste startende forsvarer. | element-summary |

## Aktuelle kjøp

| Spiller | Vurdering | Grunnlag |
|---|---|---|
| Tavernier (BOU, 6.2) | Høyest xP R8–R13 blant midtbanespillere ≤ 7.8 utenom MUN/BHA. **Risiko:** tre hamstringskader forrige sesong, og minuttene synker (90, 90, 88, 82, 74, 72, 78). Ser ut som styrt belastning. Ingen skadeflagg nå. | element-summary, nettsøk om 2025/26 |
| Dewsbury-Hall (EVE, 6.6) | 90 min i alle 7 runder. Litt lavere xP, men tryggere minutter. Tøff R8 (ARS borte). | element-summary |
| João Pedro (CHE, 7.9) | 3,05 xG; benket/0 min i R5, 71 i R6. p_start 0,82. | element-summary |
| Rogers (CHE, 8.0) | Høyest xP i prisklassen, men krever 8,0 og er utenfor budsjett i ett bytte (7,8 tilgjengelig). | |

## Kampprogram R8–R15 (FPL-FDR, snitt)

Lettest: COV, AVL, IPS, TOT (2,75). Tyngst: BRE, LIV (3,38). Av våre lag har BHA tøffe R8–R9 (liv borte, mci borte),
MUN tung R9 og R11 (che borte, liv borte), MCI lett R11 (FUL hjemme). Ingen blanke eller doble runder er satt opp.

## Usikkerheter modellen bør tåle

1. **Rotasjon etter europacup midt i uken.** LIV spiller Villarreal i Champions League (bekreftet, Sports Mole). Hvilke andre av lagene våre som spiller i Europa denne uken er ikke verifisert (antakelse: ARS, MCI og CHE). Rammer Calafiori/Konsa (allerede p_start ≈ 0,83–0,89) og kan ramme João Pedro.
2. **Pressekonferanser før R8** kommer torsdag og fredag. Endringer i FPL-flagg før fristen fredag 17:30 UTC kan endre bytte 1.
3. **Fernandes-modellen:** ser ut til å vekte straffer og xGI tungt. Følsomhetstest: Fernandes 5,0 xP i stedet for 7,2.
4. **Tavernier-minutter:** følsomhetstest med p_start 0,75 og 70 min.
5. **Szoboszlai-comeback:** hvis han er tilbake fra R12, er salgsverdien 6,8 uansett (ingen gevinst å tape ved å selge).

## Tillegg 15:25 UTC: kampprogram R14–R19 og wildcardtidspunkt

Gjennomsnittlig FDR R8–13 mot R14–19 (fra `fixtures.json`):

- **Blir lettere etter R13:** BRE og LIV (−0,67), LEE (−0,50), BHA, NEW og MCI (−0,33).
- **Blir tyngre etter R13:** COV og IPS (+1,00), TOT (+0,83), CHE og CRY (+0,33).
- Juleperioden: R17 26. des, R18 29. des, R19 1. jan. Tre runder på sju dager gir mer rotasjon og flere skader.

Konsekvens for strategi (vurdering, ikke beregning):

1. En wildcard nå vil hente COV-spillere (Thomas, van Ewijk-typen) og TOT/IPS-forsvarere for R8–13, som blir dårlige kjøp fra R14.
   En wildcard rundt **R13–R14** treffer skiftet i kampprogrammet og kan bygge troppen for julen.
2. **Free Hit** er mest verdifull i juleperioden (R17–R19) hvis skader og rotasjon tømmer troppen. Den er også forsikring mot blanke runder.
3. **Bench Boost** i en julerunde er risikabelt på grunn av rotasjon. Bedre i en vanlig runde rett etter wildcard (R14–R16), med en benk bygd for det.
