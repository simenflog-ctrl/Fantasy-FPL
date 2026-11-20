# Prognoseevaluering

Skrevet av `oppdater.py` fra `logg.csv`; ikke rediger for hånd.

Runder i loggen: R8, R9, R10 (3 runde(r), 841 rader).

Skjevhet = snitt av faktisk − forventet poeng (positiv = modellen undervurderer). SE = standardfeil (sd/√n).
Tydelig skjevhet krever |skjevhet| > 2 SE, samme fortegn i minst fire runder og minst fire runder (RUTINE steg 2.4).
Svakere mønstre noteres, men brukes ikke.

## Totalt og per runde

| Utvalg | n | Codex skjevhet | Codex SE | Repo skjevhet | Repo SE |
|---|---|---|---|---|---|
| Alle | 841 | +0,37 | 0,10 | +0,13 | 0,10 |
| R8 | 301 | +0,52 | 0,17 | +0,27 | 0,17 |
| R9 | 267 | +0,18 | 0,16 | -0,05 | 0,16 |
| R10 | 273 | +0,37 | 0,17 | +0,13 | 0,17 |

## Posisjon × prisklasse, codex

| Posisjon | Prisklasse | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |
|---|---|---|---|---|---|---|---|---|
| GKP | < 5,0 | 34 | 3 | 2,56 | 3,41 | +0,85 | 0,51 |  |
| GKP | 5,0–7,4 | 27 | 3 | 3,11 | 3,78 | +0,67 | 0,51 |  |
| DEF | < 5,0 | 189 | 3 | 2,25 | 2,59 | +0,34 | 0,19 |  |
| DEF | 5,0–7,4 | 114 | 3 | 2,69 | 3,00 | +0,31 | 0,30 |  |
| DEF | 7,5–9,9 | 3 | 3 | 4,87 | 10,33 | +5,47 | 3,44 |  |
| MID | < 5,0 | 64 | 3 | 1,75 | 2,20 | +0,45 | 0,32 |  |
| MID | 5,0–7,4 | 297 | 3 | 2,34 | 2,63 | +0,29 | 0,14 | > 2 SE, men 3 runde(r) / 3 med samme fortegn |
| MID | 7,5–9,9 | 25 | 3 | 3,62 | 2,84 | -0,78 | 0,59 |  |
| MID | ≥ 10,0 | 3 | 3 | 4,35 | 4,00 | -0,35 | 3,06 |  |
| FWD | < 5,0 | 1 | 1 | 0,75 | 0,00 | -0,75 | – |  |
| FWD | 5,0–7,4 | 72 | 3 | 2,41 | 3,11 | +0,70 | 0,40 |  |
| FWD | 7,5–9,9 | 9 | 3 | 3,89 | 4,56 | +0,67 | 1,48 |  |
| FWD | ≥ 10,0 | 3 | 3 | 6,08 | 4,00 | -2,08 | 2,03 |  |

## Posisjon × prisklasse, repo_hybrid

| Posisjon | Prisklasse | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |
|---|---|---|---|---|---|---|---|---|
| GKP | < 5,0 | 34 | 3 | 2,69 | 3,41 | +0,73 | 0,52 |  |
| GKP | 5,0–7,4 | 27 | 3 | 3,29 | 3,78 | +0,49 | 0,52 |  |
| DEF | < 5,0 | 189 | 3 | 2,45 | 2,59 | +0,15 | 0,19 |  |
| DEF | 5,0–7,4 | 114 | 3 | 2,90 | 3,00 | +0,10 | 0,30 |  |
| DEF | 7,5–9,9 | 3 | 3 | 5,99 | 10,33 | +4,34 | 3,46 |  |
| MID | < 5,0 | 64 | 3 | 1,98 | 2,20 | +0,22 | 0,32 |  |
| MID | 5,0–7,4 | 297 | 3 | 2,59 | 2,63 | +0,04 | 0,14 |  |
| MID | 7,5–9,9 | 25 | 3 | 4,06 | 2,84 | -1,22 | 0,60 | > 2 SE, men 3 runde(r) / 3 med samme fortegn |
| MID | ≥ 10,0 | 3 | 3 | 6,00 | 4,00 | -2,00 | 3,26 |  |
| FWD | < 5,0 | 1 | 1 | 1,09 | 0,00 | -1,09 | – |  |
| FWD | 5,0–7,4 | 72 | 3 | 2,63 | 3,11 | +0,48 | 0,39 |  |
| FWD | 7,5–9,9 | 9 | 3 | 3,82 | 4,56 | +0,73 | 1,56 |  |
| FWD | ≥ 10,0 | 3 | 3 | 8,24 | 4,00 | -4,24 | 1,96 | > 2 SE, men 3 runde(r) / 3 med samme fortegn |

## Topp ti forventet per runde (kapteinskandidatene)

Topp ti velges separat for hvert poengsett.

| Poengsett | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |
|---|---|---|---|---|---|---|---|
| codex | 30 | 3 | 4,73 | 5,13 | +0,40 | 0,85 |  |
| repo_hybrid | 30 | 3 | 5,69 | 4,53 | -1,16 | 0,83 |  |

### Topp ti codex, siste runde (R10)

| Spiller | Pos | Pris | Forventet | Faktisk | Min |
|---|---|---|---|---|---|
| Mbeumo | MID | 7,9 | 5,53 | 2 | 82 |
| Haaland | FWD | 15,8 | 5,39 | 2 | 90 |
| Gabriel | DEF | 8,0 | 5,39 | 8 | 90 |
| Isak | FWD | 9,2 | 4,86 | 8 | 90 |
| Barry | FWD | 5,6 | 4,75 | 16 | 90 |
| Tavernier | MID | 6,6 | 4,72 | 3 | 90 |
| B.Fernandes | MID | 11,7 | 4,49 | 10 | 90 |
| Ødegaard | MID | 6,7 | 4,42 | 11 | 90 |
| Tarkowski | DEF | 6,2 | 4,40 | 2 | 90 |
| De Cuyper | DEF | 5,4 | 4,36 | 6 | 81 |

### Topp ti repo_hybrid, siste runde (R10)

| Spiller | Pos | Pris | Forventet | Faktisk | Min |
|---|---|---|---|---|---|
| Haaland | FWD | 15,8 | 7,44 | 2 | 90 |
| Gabriel | DEF | 8,0 | 6,72 | 8 | 90 |
| B.Fernandes | MID | 11,7 | 6,01 | 10 | 90 |
| Mbeumo | MID | 7,9 | 5,99 | 2 | 82 |
| Dewsbury-Hall | MID | 6,6 | 5,50 | 9 | 90 |
| Rogers | MID | 8,2 | 5,28 | 2 | 90 |
| Palmer | MID | 9,8 | 5,27 | 2 | 90 |
| Tavernier | MID | 6,6 | 5,26 | 3 | 90 |
| Iwobi | MID | 5,4 | 5,19 | 2 | 90 |
| Raya | GKP | 6,2 | 4,97 | 6 | 90 |

## Konklusjon

Ingen tydelige skjevheter ennå (3 runde(r)). Kriteriet kan tidligst slå inn etter fire runder.
