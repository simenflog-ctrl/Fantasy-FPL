# Evaluering av prognosen for runde 8

Skrevet 2026-10-29 av agenten `fpl-datagrunnlag`. Faktiske poeng fra `data/live_gw8.json` (hentet 2026-10-29 06:37 UTC),
lagets resultat fra `data/picks_gw8.json`. Prognosen er `gw08/prognose/prognose_R8.json`.

## Sjekksum

`cd samarbeid/gw08 && shasum -a 256 -c prognose/SHA256SUMS`: alle fire OK
(`prognose/prognose_R8.json`, `codex/spillerpoeng_r2.csv`, `data/bootstrap.json`, `data/fixtures.json`).

## Hva Simen faktisk gjorde

Nøyaktig anbefalt plan: Szoboszlai → Tavernier (1 gratisbytte, 0 trekk, bank £1,6m), samme ellever, benkerekkefølge,
kaptein Haaland og visekaptein B.Fernandes (verifisert i `transfers.json` og `picks_gw8.json`). Offisielt resultat: **61 poeng**.

## Anbefalt mot referanse (faktiske poeng)

Prognosen forutsatte faste ellever uten autobytter. Begge tellingene vises.

| Plan | Forventet codex | Forventet repo_hybrid | Faktisk, fast ellever | Faktisk med autobytter |
|---|---|---|---|---|
| Anbefalt (Tavernier inn) | 52,3 | 64,0 | **61** | **61** (Maguire 0 inn for Fernandes 0) |
| Referanse uten bytter | 50,9 | 62,3 | 51 | 53 (van Ewijk 2 inn for Fernandes 0) |
| **Anbefalt − referanse** | +1,4 | +1,7 | **+10** | **+8** |

Forskjellen kommer bare fra Tavernier (10 poeng, 86 min) mot Maguire (0 poeng, 90 min) i ellever, og fra benken ved autobytte.

Spillere i anbefalt ellever (faktisk / forventet codex / forventet repo_hybrid):
Verbruggen 2 / 2,6 / 3,1; Calafiori 1 (22 min) / 4,5 / 4,8; Konsa 14 / 3,5 / 4,0; N.Williams 8 / 3,5 / 4,0;
B.Fernandes 0 (0 min) / 4,8 / 7,2; Mbeumo 2 / 5,2 / 5,5; Tavernier 10 / 4,4 / 4,7; Le Fée 3 / 4,1 / 4,9; Groß 0 / 4,0 / 4,8;
Haaland (C) 8×2 / 6,1×2 / 8,4×2; Thiago 5 / 3,5 / 4,1. Benk: Steele 0, Maguire 0, van Ewijk 2, Kusi-Asare 0.

## Mot de to poengsettene

- **Codex (52,3):** faktisk 61 er 8,7 over. Konsa (+10,5) og Tavernier (+5,6) trakk opp; Fernandes (0 min) og Groß trakk ned.
- **Repo-hybrid (64,0):** faktisk 61 er 3,0 under. Fernandes (−7,2) og Groß (−4,8) er de største avvikene.
- Én runde sier lite om hvilket poengsett som er best; avviket mellom dem (≈ 12 poeng) er like stort som rundens tilfeldige utslag.

## Løpende tabell

| Runde | Handling | Anbefalt faktisk | Referanse faktisk (fast / autobytter) | Forventet gevinst (codex / repo) | Faktisk gevinst (fast / autobytter) | Lagets poeng (offisielt) |
|---|---|---|---|---|---|---|
| R8 | Szoboszlai → Tavernier, WC holdt | 61 | 51 / 53 | +1,4 / +1,7 | +10 / +8 | 61 |

Ett utfall beviser lite. Gevinsten i R8 var større enn forventet fordi Tavernier fikk 10 poeng; retningen stemte.

## Prognoseevaluering (spillernivå)

R8 er lagt inn i `samarbeid/kalibrering/logg.csv` (301 spillere med forventet ≥ 1 i minst ett poengsett; 47 av dem med 0 minutter),
fra den frosne `gw08/codex/spillerpoeng_r2.csv` (gw == 8). Oversikt i `samarbeid/kalibrering/oversikt.md`.

Samlet skjevhet R8: codex +0,52 (SE 0,17), repo_hybrid +0,27 (SE 0,17) poeng per spiller.
Topp ti forventet: codex +0,37 (SE 1,79), repo_hybrid −2,70 (SE 1,67).
**Ingen tydelige skjevheter ennå (1 runde).** Kriteriet krever minst fire runder.
