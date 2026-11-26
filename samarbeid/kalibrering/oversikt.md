# Prognoseevaluering

Skrevet av `oppdater.py` fra `logg.csv`; ikke rediger for hånd.

Runder i loggen: R8, R9, R10, R11 (4 runde(r), 1118 rader).

Skjevhet = snitt av faktisk − forventet poeng (positiv = modellen undervurderer). SE = standardfeil (sd/√n).
Tydelig skjevhet krever |skjevhet| > 2 SE, samme fortegn i minst fire runder og minst fire runder (RUTINE steg 2.4).
Svakere mønstre noteres, men brukes ikke.

## Totalt og per runde

| Utvalg | n | Codex skjevhet | Codex SE | Repo skjevhet | Repo SE |
|---|---|---|---|---|---|
| Alle | 1118 | +0,34 | 0,09 | +0,10 | 0,09 |
| R8 | 301 | +0,52 | 0,17 | +0,27 | 0,17 |
| R9 | 267 | +0,18 | 0,16 | -0,05 | 0,16 |
| R10 | 273 | +0,37 | 0,17 | +0,13 | 0,17 |
| R11 | 277 | +0,28 | 0,18 | +0,04 | 0,19 |

## Posisjon × prisklasse, codex

| Posisjon | Prisklasse | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |
|---|---|---|---|---|---|---|---|---|
| GKP | < 5,0 | 47 | 4 | 2,52 | 3,49 | +0,97 | 0,44 | **tydelig** |
| GKP | 5,0–7,4 | 36 | 4 | 3,12 | 3,61 | +0,49 | 0,44 |  |
| DEF | < 5,0 | 254 | 4 | 2,26 | 2,47 | +0,21 | 0,16 |  |
| DEF | 5,0–7,4 | 150 | 4 | 2,71 | 2,91 | +0,20 | 0,26 |  |
| DEF | 7,5–9,9 | 4 | 4 | 4,88 | 8,00 | +3,12 | 3,38 |  |
| MID | < 5,0 | 88 | 4 | 1,79 | 2,26 | +0,47 | 0,26 |  |
| MID | 5,0–7,4 | 394 | 4 | 2,37 | 2,76 | +0,39 | 0,14 | **tydelig** |
| MID | 7,5–9,9 | 34 | 4 | 3,65 | 2,74 | -0,92 | 0,46 |  |
| MID | ≥ 10,0 | 4 | 4 | 4,26 | 3,50 | -0,76 | 2,21 |  |
| FWD | < 5,0 | 1 | 1 | 0,75 | 0,00 | -0,75 | – |  |
| FWD | 5,0–7,4 | 92 | 4 | 2,52 | 3,26 | +0,74 | 0,36 | **tydelig** |
| FWD | 7,5–9,9 | 10 | 4 | 4,02 | 4,60 | +0,58 | 1,33 |  |
| FWD | ≥ 10,0 | 4 | 4 | 6,10 | 3,50 | -2,60 | 1,53 |  |

## Posisjon × prisklasse, repo_hybrid

| Posisjon | Prisklasse | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |
|---|---|---|---|---|---|---|---|---|
| GKP | < 5,0 | 47 | 4 | 2,65 | 3,49 | +0,84 | 0,44 |  |
| GKP | 5,0–7,4 | 36 | 4 | 3,31 | 3,61 | +0,30 | 0,44 |  |
| DEF | < 5,0 | 254 | 4 | 2,46 | 2,47 | +0,01 | 0,16 |  |
| DEF | 5,0–7,4 | 150 | 4 | 2,94 | 2,91 | -0,03 | 0,27 |  |
| DEF | 7,5–9,9 | 4 | 4 | 6,06 | 8,00 | +1,94 | 3,43 |  |
| MID | < 5,0 | 88 | 4 | 2,01 | 2,26 | +0,25 | 0,25 |  |
| MID | 5,0–7,4 | 394 | 4 | 2,61 | 2,76 | +0,15 | 0,14 |  |
| MID | 7,5–9,9 | 34 | 4 | 4,13 | 2,74 | -1,40 | 0,46 | **tydelig** |
| MID | ≥ 10,0 | 4 | 4 | 5,90 | 3,50 | -2,40 | 2,34 |  |
| FWD | < 5,0 | 1 | 1 | 1,09 | 0,00 | -1,09 | – |  |
| FWD | 5,0–7,4 | 92 | 4 | 2,72 | 3,26 | +0,54 | 0,35 |  |
| FWD | 7,5–9,9 | 10 | 4 | 3,92 | 4,60 | +0,68 | 1,40 |  |
| FWD | ≥ 10,0 | 4 | 4 | 8,26 | 3,50 | -4,76 | 1,48 | **tydelig** |

## Topp ti forventet per runde (kapteinskandidatene)

Topp ti velges separat for hvert poengsett.

| Poengsett | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |
|---|---|---|---|---|---|---|---|
| codex | 40 | 4 | 4,76 | 4,70 | -0,06 | 0,68 |  |
| repo_hybrid | 40 | 4 | 5,71 | 4,42 | -1,29 | 0,68 |  |

### Topp ti codex, siste runde (R11)

| Spiller | Pos | Pris | Forventet | Faktisk | Min |
|---|---|---|---|---|---|
| Haaland | FWD | 15,8 | 6,18 | 2 | 90 |
| Isak | FWD | 9,3 | 5,23 | 5 | 84 |
| Gabriel | DEF | 8,1 | 4,93 | 1 | 90 |
| Van Hecke | DEF | 5,1 | 4,84 | 6 | 90 |
| Tavernier | MID | 6,7 | 4,83 | 8 | 90 |
| De Cuyper | DEF | 5,5 | 4,57 | 1 | 90 |
| Barry | FWD | 5,7 | 4,51 | 2 | 68 |
| Ødegaard | MID | 6,7 | 4,49 | 5 | 90 |
| Mbeumo | MID | 7,9 | 4,47 | 1 | 21 |
| E.Le Fée | MID | 5,7 | 4,47 | 3 | 90 |

### Topp ti repo_hybrid, siste runde (R11)

| Spiller | Pos | Pris | Forventet | Faktisk | Min |
|---|---|---|---|---|---|
| Haaland | FWD | 15,8 | 8,33 | 2 | 90 |
| Gabriel | DEF | 8,1 | 6,26 | 1 | 90 |
| B.Fernandes | MID | 11,6 | 5,58 | 2 | 90 |
| Van Hecke | DEF | 5,1 | 5,52 | 6 | 90 |
| Tavernier | MID | 6,7 | 5,49 | 8 | 90 |
| Rogers | MID | 8,2 | 5,37 | 5 | 90 |
| Palmer | MID | 9,8 | 5,34 | 2 | 90 |
| Rudoni | MID | 4,9 | 5,33 | 10 | 90 |
| N.Jackson | FWD | 7,1 | 5,28 | 2 | 72 |
| E.Le Fée | MID | 5,7 | 5,22 | 3 | 90 |

## Konklusjon

Tydelige skjevheter:

- codex: GKP < 5,0: +0,97 (SE 0,44, 4 runder)
- codex: MID 5,0–7,4: +0,39 (SE 0,14, 4 runder)
- codex: FWD 5,0–7,4: +0,74 (SE 0,36, 4 runder)
- repo_hybrid: MID 7,5–9,9: -1,40 (SE 0,46, 4 runder)
- repo_hybrid: FWD ≥ 10,0: -4,76 (SE 1,48, 4 runder)
