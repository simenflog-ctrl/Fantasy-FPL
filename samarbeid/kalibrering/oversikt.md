# Prognoseevaluering

Skrevet av `oppdater.py` fra `logg.csv`; ikke rediger for hånd.

Runder i loggen: R8 (1 runde(r), 301 rader).

Skjevhet = snitt av faktisk − forventet poeng (positiv = modellen undervurderer). SE = standardfeil (sd/√n).
Tydelig skjevhet krever |skjevhet| > 2 SE, samme fortegn i minst fire runder og minst fire runder (RUTINE steg 2.4).
Svakere mønstre noteres, men brukes ikke.

## Totalt og per runde

| Utvalg | n | Codex skjevhet | Codex SE | Repo skjevhet | Repo SE |
|---|---|---|---|---|---|
| Alle | 301 | +0,52 | 0,17 | +0,27 | 0,17 |
| R8 | 301 | +0,52 | 0,17 | +0,27 | 0,17 |

## Posisjon × prisklasse, codex

| Posisjon | Prisklasse | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |
|---|---|---|---|---|---|---|---|---|
| GKP | < 5,0 | 11 | 1 | 2,51 | 4,09 | +1,58 | 1,02 |  |
| GKP | 5,0–7,4 | 9 | 1 | 3,04 | 4,56 | +1,52 | 1,06 |  |
| DEF | < 5,0 | 66 | 1 | 2,14 | 2,70 | +0,56 | 0,34 |  |
| DEF | 5,0–7,4 | 39 | 1 | 2,69 | 3,38 | +0,70 | 0,60 |  |
| DEF | 7,5–9,9 | 1 | 1 | 4,68 | 17,00 | +12,32 | – |  |
| MID | < 5,0 | 23 | 1 | 1,59 | 1,70 | +0,10 | 0,26 |  |
| MID | 5,0–7,4 | 106 | 1 | 2,13 | 2,65 | +0,52 | 0,24 | > 2 SE, men 1 runde(r) / 1 med samme fortegn |
| MID | 7,5–9,9 | 9 | 1 | 3,51 | 1,44 | -2,07 | 0,86 | > 2 SE, men 1 runde(r) / 1 med samme fortegn |
| MID | ≥ 10,0 | 1 | 1 | 4,83 | 0,00 | -4,83 | – |  |
| FWD | < 5,0 | 1 | 1 | 0,75 | 0,00 | -0,75 | – |  |
| FWD | 5,0–7,4 | 30 | 1 | 1,96 | 2,43 | +0,47 | 0,55 |  |
| FWD | 7,5–9,9 | 4 | 1 | 3,94 | 3,75 | -0,19 | 1,96 |  |
| FWD | ≥ 10,0 | 1 | 1 | 6,09 | 8,00 | +1,91 | – |  |

## Posisjon × prisklasse, repo_hybrid

| Posisjon | Prisklasse | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |
|---|---|---|---|---|---|---|---|---|
| GKP | < 5,0 | 11 | 1 | 2,61 | 4,09 | +1,48 | 1,00 |  |
| GKP | 5,0–7,4 | 9 | 1 | 3,18 | 4,56 | +1,38 | 1,11 |  |
| DEF | < 5,0 | 66 | 1 | 2,30 | 2,70 | +0,40 | 0,33 |  |
| DEF | 5,0–7,4 | 39 | 1 | 2,81 | 3,38 | +0,57 | 0,60 |  |
| DEF | 7,5–9,9 | 1 | 1 | 5,75 | 17,00 | +11,25 | – |  |
| MID | < 5,0 | 23 | 1 | 1,85 | 1,70 | -0,16 | 0,27 |  |
| MID | 5,0–7,4 | 106 | 1 | 2,42 | 2,65 | +0,23 | 0,25 |  |
| MID | 7,5–9,9 | 9 | 1 | 3,94 | 1,44 | -2,50 | 0,91 | > 2 SE, men 1 runde(r) / 1 med samme fortegn |
| MID | ≥ 10,0 | 1 | 1 | 7,23 | 0,00 | -7,23 | – |  |
| FWD | < 5,0 | 1 | 1 | 1,09 | 0,00 | -1,09 | – |  |
| FWD | 5,0–7,4 | 30 | 1 | 2,27 | 2,43 | +0,16 | 0,53 |  |
| FWD | 7,5–9,9 | 4 | 1 | 4,03 | 3,75 | -0,28 | 2,44 |  |
| FWD | ≥ 10,0 | 1 | 1 | 8,41 | 8,00 | -0,41 | – |  |

## Topp ti forventet per runde (kapteinskandidatene)

Topp ti velges separat for hvert poengsett.

| Poengsett | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |
|---|---|---|---|---|---|---|---|
| codex | 10 | 1 | 4,73 | 5,10 | +0,37 | 1,79 |  |
| repo_hybrid | 10 | 1 | 5,80 | 3,10 | -2,70 | 1,67 |  |

### Topp ti codex, siste runde (R8)

| Spiller | Pos | Pris | Forventet | Faktisk | Min |
|---|---|---|---|---|---|
| Haaland | FWD | 15,7 | 6,09 | 8 | 90 |
| Mbeumo | MID | 7,8 | 5,23 | 2 | 90 |
| B.Fernandes | MID | 11,8 | 4,83 | 0 | 0 |
| Gabriel | DEF | 7,9 | 4,68 | 17 | 90 |
| Calafiori | DEF | 6,0 | 4,49 | 1 | 22 |
| Isak | FWD | 9,0 | 4,49 | 9 | 76 |
| Palmer | MID | 9,7 | 4,48 | -1 | 79 |
| Tavernier | MID | 6,2 | 4,39 | 10 | 86 |
| Ødegaard | MID | 6,8 | 4,32 | 3 | 90 |
| Calvert-Lewin | FWD | 6,1 | 4,28 | 2 | 84 |

### Topp ti repo_hybrid, siste runde (R8)

| Spiller | Pos | Pris | Forventet | Faktisk | Min |
|---|---|---|---|---|---|
| Haaland | FWD | 15,7 | 8,41 | 8 | 90 |
| B.Fernandes | MID | 11,8 | 7,23 | 0 | 0 |
| Rogers | MID | 8,0 | 5,85 | 1 | 90 |
| Gabriel | DEF | 7,9 | 5,75 | 17 | 90 |
| João Pedro | FWD | 7,9 | 5,56 | 0 | 0 |
| Mbeumo | MID | 7,8 | 5,48 | 2 | 90 |
| Palmer | MID | 9,7 | 5,06 | -1 | 79 |
| E.Le Fée | MID | 5,7 | 4,92 | 3 | 78 |
| Groß | MID | 6,2 | 4,84 | 0 | 90 |
| Calafiori | DEF | 6,0 | 4,83 | 1 | 22 |

## Konklusjon

Ingen tydelige skjevheter ennå (1 runde(r)). Kriteriet kan tidligst slå inn etter fire runder.
