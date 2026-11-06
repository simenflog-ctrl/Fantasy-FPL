# Prognoseevaluering

Skrevet av `oppdater.py` fra `logg.csv`; ikke rediger for hånd.

Runder i loggen: R8, R9 (2 runde(r), 568 rader).

Skjevhet = snitt av faktisk − forventet poeng (positiv = modellen undervurderer). SE = standardfeil (sd/√n).
Tydelig skjevhet krever |skjevhet| > 2 SE, samme fortegn i minst fire runder og minst fire runder (RUTINE steg 2.4).
Svakere mønstre noteres, men brukes ikke.

## Totalt og per runde

| Utvalg | n | Codex skjevhet | Codex SE | Repo skjevhet | Repo SE |
|---|---|---|---|---|---|
| Alle | 568 | +0,36 | 0,12 | +0,12 | 0,12 |
| R8 | 301 | +0,52 | 0,17 | +0,27 | 0,17 |
| R9 | 267 | +0,18 | 0,16 | -0,05 | 0,16 |

## Posisjon × prisklasse, codex

| Posisjon | Prisklasse | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |
|---|---|---|---|---|---|---|---|---|
| GKP | < 5,0 | 23 | 2 | 2,53 | 3,52 | +0,99 | 0,68 |  |
| GKP | 5,0–7,4 | 18 | 2 | 3,08 | 3,94 | +0,86 | 0,66 |  |
| DEF | < 5,0 | 126 | 2 | 2,24 | 2,67 | +0,44 | 0,24 |  |
| DEF | 5,0–7,4 | 77 | 2 | 2,70 | 3,03 | +0,33 | 0,39 |  |
| DEF | 7,5–9,9 | 2 | 2 | 4,61 | 11,50 | +6,89 | 5,43 |  |
| MID | < 5,0 | 43 | 2 | 1,73 | 2,02 | +0,29 | 0,30 |  |
| MID | 5,0–7,4 | 199 | 2 | 2,28 | 2,58 | +0,29 | 0,16 |  |
| MID | 7,5–9,9 | 17 | 2 | 3,54 | 2,29 | -1,24 | 0,71 |  |
| MID | ≥ 10,0 | 2 | 2 | 4,28 | 1,00 | -3,28 | 1,55 | > 2 SE, men 2 runde(r) / 2 med samme fortegn |
| FWD | < 5,0 | 1 | 1 | 0,75 | 0,00 | -0,75 | – |  |
| FWD | 5,0–7,4 | 51 | 2 | 2,26 | 2,76 | +0,50 | 0,45 |  |
| FWD | 7,5–9,9 | 7 | 2 | 3,77 | 5,00 | +1,23 | 1,61 |  |
| FWD | ≥ 10,0 | 2 | 2 | 6,42 | 5,00 | -1,42 | 3,34 |  |

## Posisjon × prisklasse, repo_hybrid

| Posisjon | Prisklasse | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |
|---|---|---|---|---|---|---|---|---|
| GKP | < 5,0 | 23 | 2 | 2,66 | 3,52 | +0,86 | 0,68 |  |
| GKP | 5,0–7,4 | 18 | 2 | 3,23 | 3,94 | +0,72 | 0,67 |  |
| DEF | < 5,0 | 126 | 2 | 2,44 | 2,67 | +0,24 | 0,24 |  |
| DEF | 5,0–7,4 | 77 | 2 | 2,85 | 3,03 | +0,18 | 0,39 |  |
| DEF | 7,5–9,9 | 2 | 2 | 5,63 | 11,50 | +5,87 | 5,37 |  |
| MID | < 5,0 | 43 | 2 | 1,99 | 2,02 | +0,03 | 0,30 |  |
| MID | 5,0–7,4 | 199 | 2 | 2,55 | 2,58 | +0,03 | 0,16 |  |
| MID | 7,5–9,9 | 17 | 2 | 3,96 | 2,29 | -1,66 | 0,69 | > 2 SE, men 2 runde(r) / 2 med samme fortegn |
| MID | ≥ 10,0 | 2 | 2 | 6,00 | 1,00 | -5,00 | 2,23 | > 2 SE, men 2 runde(r) / 2 med samme fortegn |
| FWD | < 5,0 | 1 | 1 | 1,09 | 0,00 | -1,09 | – |  |
| FWD | 5,0–7,4 | 51 | 2 | 2,52 | 2,76 | +0,24 | 0,42 |  |
| FWD | 7,5–9,9 | 7 | 2 | 3,74 | 5,00 | +1,26 | 1,71 |  |
| FWD | ≥ 10,0 | 2 | 2 | 8,65 | 5,00 | -3,65 | 3,24 |  |

## Topp ti forventet per runde (kapteinskandidatene)

Topp ti velges separat for hvert poengsett.

| Poengsett | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |
|---|---|---|---|---|---|---|---|
| codex | 20 | 2 | 4,68 | 4,30 | -0,38 | 1,00 |  |
| repo_hybrid | 20 | 2 | 5,66 | 4,50 | -1,16 | 1,15 |  |

### Topp ti codex, siste runde (R9)

| Spiller | Pos | Pris | Forventet | Faktisk | Min |
|---|---|---|---|---|---|
| Haaland | FWD | 15,8 | 6,76 | 2 | 90 |
| Mbeumo | MID | 7,9 | 4,91 | 1 | 90 |
| Tavernier | MID | 6,4 | 4,67 | 3 | 90 |
| Silva | DEF | 5,0 | 4,57 | 8 | 90 |
| Gabriel | DEF | 7,9 | 4,54 | 6 | 90 |
| Palmer | MID | 9,8 | 4,26 | 8 | 90 |
| Isak | FWD | 9,1 | 4,24 | 2 | 90 |
| Barnes | MID | 6,1 | 4,17 | 2 | 90 |
| Tzolakis | GKP | 4,7 | 4,13 | 1 | 90 |
| Hall | DEF | 5,3 | 4,13 | 2 | 90 |

### Topp ti repo_hybrid, siste runde (R9)

| Spiller | Pos | Pris | Forventet | Faktisk | Min |
|---|---|---|---|---|---|
| Haaland | FWD | 15,8 | 8,88 | 2 | 90 |
| Gabriel | DEF | 7,9 | 5,50 | 6 | 90 |
| Tavernier | MID | 6,4 | 5,29 | 3 | 90 |
| Dewsbury-Hall | MID | 6,6 | 5,25 | 4 | 90 |
| Rogers | MID | 8,0 | 5,24 | 9 | 90 |
| Mbeumo | MID | 7,9 | 5,16 | 1 | 90 |
| Palmer | MID | 9,8 | 5,13 | 8 | 90 |
| Van Hecke | DEF | 4,9 | 4,96 | 15 | 90 |
| Rayan | MID | 6,3 | 4,95 | 3 | 87 |
| Silva | DEF | 5,0 | 4,87 | 8 | 90 |

## Konklusjon

Ingen tydelige skjevheter ennå (2 runde(r)). Kriteriet kan tidligst slå inn etter fire runder.
