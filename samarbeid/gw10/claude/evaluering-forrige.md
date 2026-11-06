# Evaluering av prognosen for runde 9

Skrevet 2026-11-06 av agenten `fpl-datagrunnlag`. Faktiske poeng kommer fra `data/live_gw9.json` (hentet 2026-11-06 06:38 UTC),
og lagets resultat fra `data/picks_gw9.json`. Prognosen er `gw09/prognose/prognose_R9.json`.

## Sjekksum

`cd samarbeid/gw09 && shasum -a 256 -c prognose/SHA256SUMS`: alle fire OK
(`prognose/prognose_R9.json`, `codex/spillerpoeng_r2.csv`, `data/bootstrap.json`, `data/fixtures.json`).

## Hva Simen faktisk gjorde

Simen brukte wildcard i R9 (aktivert 2026-10-30 06:53 UTC, elleve bytter 06:57 UTC). Inn og ut var nøyaktig som anbefalt. Bank
£0,4m. Ellever, benkerekkefølge og kaptein (Haaland) var som anbefalt. **Eneste avvik: visekaptein Ødegaard i stedet for Mbeumo.**
Det betydde ingenting, fordi Haaland spilte 90 minutter. Offisielt resultat: **48 poeng**, 16 på benken, ingen autobytter
(alle 22 spillerne i de to elleverne spilte; bare Steele og Kusi-Asare på referansebenken fikk 0 minutter).

## Anbefalt mot referanse (faktiske poeng)

Prognosen regnet med faste ellever uten autobytter. Alle elleve i begge planene spilte, så autobytter endrer ikke noe.

| Plan | Forventet codex | Forventet repo_hybrid | Faktisk (fast = med autobytter) |
|---|---|---|---|
| Anbefalt (wildcard) | 56,0 | 62,8 | **48** |
| Referanse uten bytter (gammel tropp) | 48,0 | 55,4 | **57** |
| **Anbefalt − referanse** | +8,0 | +7,4 | **−9** |

Felles i begge elleverne var Haaland (C) med 2×2, Mbeumo 1 og Tavernier 3. Forskjellen kom fra de åtte andre plassene:
anbefalt 40 poeng (Tzolakis 1, Gabriel 6, Silva 8, Dasilva 2, Ødegaard 3, Rudoni 9, Barry 9, Isak 2) mot referansens 49
(Verbruggen 11, Konsa 10, Calafiori 6, N.Williams 1, B.Fernandes 2, Le Fée 8, Groß 2, Thiago 9). Keeperbyttet alene utgjorde
−10 (Tzolakis 1 mot Verbruggen 11).

Spillere i anbefalt ellever (faktisk / forventet codex / forventet repo_hybrid):
Tzolakis 1 / 4,1 / 4,3; Gabriel 6 / 4,5 / 5,5; Silva 8 / 4,6 / 4,9; Dasilva 2 / 3,4 / 3,8; Ødegaard 3 / 3,9 / 4,2;
Tavernier 3 / 4,7 / 5,3; Rudoni 9 / 4,1 / 4,4; Mbeumo 1 / 4,9 / 5,2; Barry 9 / 4,0 / 4,4; Isak 2 / 4,2 / 3,1;
Haaland (C) 2×2 / 6,8×2 / 8,9×2. Benk: Trafford 2, Groß 2, De Cuyper 9, Muharemović 3.

## Mot de to poengsettene

- **Codex:** anbefalt 48 er 8,0 under prognosen på 56,0, og referansen 57 er 9,0 over prognosen på 48,0.
- **Repo-hybrid:** anbefalt 48 er 14,8 under prognosen på 62,8, og referansen 57 er 1,6 over prognosen på 55,4.
- Haaland som kaptein (4 poeng mot forventet 13,5 og 17,8) forklarer 9,5 og 13,8 av underskuddet i anbefalt plan, men gjaldt begge
  planene likt.
- Gevinsten fra wildcarden var forventet over R9–R12 (+17,9 codex, +7,7 repo_hybrid). R9 er én av fire runder i den perioden,
  og ett utfall på −9 ligger godt innenfor den tilfeldige variasjonen fra én runde.

## Løpende tabell

| Runde | Handling | Anbefalt faktisk | Referanse faktisk (fast / autobytter) | Forventet gevinst (codex / repo) | Faktisk gevinst (fast / autobytter) | Lagets poeng (offisielt) |
|---|---|---|---|---|---|---|
| R8 | Szoboszlai → Tavernier, WC holdt | 61 | 51 / 53 | +1,4 / +1,7 | +10 / +8 | 61 |
| R9 | Wildcard (11 inn) | 48 | 57 / 57 | +8,0 / +7,4 | −9 / −9 | 48 |
| **Sum** | | 109 | 108 / 110 | +9,4 / +9,1 | +1 / −1 | 109 |

Ett utfall beviser lite, og to utfall beviser heller ikke mye. Summen over R8–R9 er omtrent null mot forventet +9.

## Prognoseevaluering (spillernivå)

R9 er lagt inn i `samarbeid/kalibrering/logg.csv` med `oppdater.py`: 267 spillere med forventet ≥ 1 i minst ett poengsett,
39 av dem med 0 minutter. Kilden er den frosne `gw09/codex/spillerpoeng_r2.csv` (gw == 9; sjekksummen er kontrollert av skriptet),
og prisene er fra `gw09/data/bootstrap.json`. Oversikten står i `samarbeid/kalibrering/oversikt.md`.

| Utvalg | Codex skjevhet (SE) | Repo_hybrid skjevhet (SE) |
|---|---|---|
| R9 alle | +0,18 (0,16) | −0,05 (0,16) |
| R8 + R9 alle | +0,36 (0,12) | +0,12 (0,12) |
| Topp ti forventet, R8 + R9 | −0,38 (1,00) | −1,16 (1,15) |

Svakere mønstre (over 2 SE, men bare to runder): MID ≥ 10,0 overvurdert i begge poengsettene (n = 2, bare B.Fernandes), og
MID 7,5–9,9 overvurdert i repo_hybrid (−1,66, SE 0,69, n = 17). Disse noteres, men brukes ikke.
**Ingen tydelige skjevheter ennå (2 runder).** Kriteriet krever minst fire runder.
