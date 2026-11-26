# Evaluering av prognosen for runde 11

Skrevet 2026-11-26 av agenten `fpl-datagrunnlag`. Faktiske poeng kommer fra `data/live_gw11.json` (hentet 2026-11-26 07:44 UTC),
og lagets resultat fra `data/picks_gw11.json`. Prognosen er `gw11/prognose/prognose_R11.json`
(frosset 2026-11-20 11:08 UTC, committet 11:19 UTC, fristen var 21. nov 11:00 UTC). Runden er ferdigspilt og `data_checked`.

## Sjekksum

`shasum -a 256 -c prognose/SHA256SUMS` i `samarbeid/gw11`: alle fem OK (`prognose/prognose_R11.json`, `codex/spillerpoeng.csv`,
`motor/spillerpoeng.csv`, `data/bootstrap.json`, `data/fixtures.json`). Eneste usporede innhold i gw11 er `codex/checkpoints/`,
som ikke inngår i prognosen.

## Hva Simen faktisk gjorde

- **Som anbefalt:** Muharemović → Van Hecke (1 gratisbytte, 0 i trekk), Bench Boost og kaptein Haaland.
- **Avvik:** oppstillingen var R10-oppstillingen med Van Hecke for Muharemović (Trafford i mål, Barry i stedet for Rudoni, 3-4-3), og
  visekapteinen var Isak i stedet for Gabriel.
- Avvikene ga ingen poengforskjell: med Bench Boost teller alle 15, og Haaland spilte 90 minutter, så visekapteinen ble ikke brukt.
- Offisielt resultat: **67 poeng** (snitt 35, høyest 106), rundens rank 29 427, ingen autobytter. Totalrank gikk fra 1 122 827 til 403 909.

## Anbefalt mot referanse og alternativ (faktiske poeng)

Alle tre frosne planer har Bench Boost i R11, så alle 15 teller. Autobytter spiller da ingen rolle; «fast» og «med autobytter» er like.
Dasilva (0 minutter) står i anbefalt plan og i rull og gir 0 der.

| Plan | Forventet codex | Forventet repo_hybrid | Faktisk |
|---|---|---|---|
| **Anbefalt:** Muharemović → Van Hecke, BB, C Haaland | 74,3 | 84,1 | **67** |
| Referanse: rull (ingen bytter), BB | 73,4 | 82,7 | **63** |
| Alternativ C: Dasilva, Mbeumo → Van Hecke, Le Fée, BB | 74,8 | 84,8 | **71** |
| **Anbefalt − referanse** | +0,9 | +1,4 | **+4** |
| **Anbefalt − alternativ C** | −0,5 | −0,7 | **−4** |

- Mot referansen: Van Hecke 6 (nullet) mot Muharemović 2.
- Mot C: Le Fée 3 (90 min) mot Mbeumo 1 (21 min), og Muharemović 2 mot Dasilva 0.
- C var forventet 0,5 / 0,7 bedre i R11, men forventet 2,1 / 0,5 dårligere over R11–R14 med samme ellever. Det faktiske utfallet i R11
  (−4) har samme fortegn som forventningen i R11, men er ett utfall av tre spillere.

Spillere i anbefalt plan (faktisk / forventet codex / forventet repo_hybrid):
Tzolakis 10 / 3,82 / 3,56; Gabriel 1 / 4,93 / 6,26; Van Hecke 6 / 4,84 / 5,52; De Cuyper 1 / 4,57 / 5,14; Ødegaard 5 / 4,49 / 5,20;
Tavernier 8 / 4,83 / 5,49; Groß 4 / 4,21 / 4,91; Rudoni 10 / 4,47 / 5,33; Mbeumo 1 (21 min) / 4,47 / 4,67; Isak 5 (84 min) / 5,23 / 4,82;
Haaland (C) 2×2 / 6,18×2 / 8,33×2; Trafford 2 / 3,80 / 3,55; Barry 2 (68 min) / 4,51 / 4,61; Silva 8 / 4,35 / 4,50; Dasilva 0 (0 min) / 3,42 / 3,90.

### Bench Boost

Med den anbefalte oppstillingen var benken Trafford 2, Barry 2, Silva 8 og Dasilva 0: **12 poeng** fra Bench Boost (forventet 16,1 / 16,6).
Uten chipen ville den anbefalte elleveren gitt 55. Simens egen oppstilling hadde Tzolakis 10, Silva 8, Rudoni 10 og Dasilva 0 på benken
(28), så uten Bench Boost ville den gitt 39. Med chipen er summen 67 i begge oppstillingene. BB11 ble valgt framfor BB18/BB19 med en
forventet fordel på 0,3–1,2 poeng i skadetesten; om den var riktig, kan først vurderes når R18–R19 er spilt, og bare grovt.

## Mot de to poengsettene

- **Codex:** anbefalt 67 er 7,3 under prognosen på 74,3; referansen 63 er 10,4 under 73,4; C 71 er 3,8 under 74,8.
- **Repo-hybrid:** anbefalt 67 er 17,1 under prognosen på 84,1; referansen 63 er 19,7 under 82,7; C 71 er 13,8 under 84,8.
- Underskuddet kom fra Haaland som kaptein (4 mot forventet 12,4 / 16,7; tredje runde på rad med 2 poeng), Gabriel og De Cuyper
  (1 hver, forventet 4,6–6,3) og Mbeumo (21 min). Tzolakis 10, Rudoni 10, Silva 8 og Tavernier 8 lå over.
- Runden var lavt scorende for alle (snitt 35 mot 55 i R10), så noe av underskuddet er felles. Laget var likevel topp 1 % i runden.

## Løpende tabell

| Runde | Handling | Anbefalt faktisk | Referanse faktisk (fast / autobytter) | Forventet gevinst (codex / repo) | Faktisk gevinst (fast / autobytter) | Lagets poeng (offisielt) |
|---|---|---|---|---|---|---|
| R8 | Szoboszlai → Tavernier, WC holdt | 61 | 51 / 53 | +1,4 / +1,7 | +10 / +8 | 61 |
| R9 | Wildcard (11 inn) | 48 | 57 / 57 | +8,0 / +7,4 | −9 / −9 | 48 |
| R10 | Rull (ingen bytter), ikke BB | 88 | 88 / 88 (= anbefalt) | 0 / 0 | 0 / 0 | 88 |
| R11 | Muharemović → Van Hecke, Bench Boost (referanse: rull med BB) | 67 | 63 / 63 | +0,9 / +1,4 | +4 / +4 | 67 |
| **Sum** | | 264 | 259 / 261 | +10,3 / +10,5 | +5 / +3 | 264 |

Anbefalt mot frosset alternativ (bare runder der alternativet ikke er referansen):

| Runde | Alternativ | Alternativ faktisk | Forventet gevinst for anbefalt (codex / repo) | Faktisk gevinst |
|---|---|---|---|---|
| R10 | Ødegaard, Dasilva → Iwobi, Van Hecke | 79 | +0,1 / −0,3 i R10 (R10–R13: +1,2 / +1,6) | +9 |
| R11 | C: Dasilva, Mbeumo → Van Hecke, Le Fée (BB) | 71 | −0,5 / −0,7 i R11 (R11–R14: +2,1 / +0,5) | −4 |

Anbefalt plan, forventet mot faktisk (fast ellever; R11 med Bench Boost, alle 15 teller):

| Runde | Forventet codex | Forventet repo_hybrid | Faktisk | Faktisk − codex | Faktisk − repo_hybrid |
|---|---|---|---|---|---|
| R8 | 52,3 | 64,0 | 61 | +8,7 | −3,0 |
| R9 | 56,0 | 62,8 | 48 | −8,0 | −14,8 |
| R10 | 56,3 | 64,7 | 88 | +31,7 | +23,3 |
| R11 | 74,3 | 84,1 | 67 | −7,3 | −17,1 |
| **Sum** | 238,9 | 275,6 | 264 | +25,1 | −11,6 |

Fire utfall beviser lite. Summen over R8–R11 ligger mellom de to poengsettene (over codex, under repo_hybrid), og spriket fra runde
til runde (−17 til +32) er mye større enn forskjellen mellom poengsettene og mellom planene.

## Prognoseevaluering (spillernivå)

R11 er lagt inn i `samarbeid/kalibrering/logg.csv` med `oppdater.py`: 277 spillere med forventet ≥ 1 i minst ett poengsett,
36 av dem med 0 minutter. Kilden er den frosne `gw11/codex/spillerpoeng.csv` (gw == 11; sjekksummen er kontrollert av skriptet; filen er
identisk med `motor/spillerpoeng.csv` ifølge `gw11/oppgaver.md`), og prisene er fra `gw11/data/bootstrap.json`.
Oversikten står i `samarbeid/kalibrering/oversikt.md`.

| Utvalg | Codex skjevhet (SE) | Repo_hybrid skjevhet (SE) |
|---|---|---|
| R11 alle | +0,28 (0,18) | +0,04 (0,19) |
| R8–R11 alle | +0,34 (0,09) | +0,10 (0,09) |
| Topp ti forventet, R8–R11 | −0,06 (0,68) | −1,29 (0,68) |

**Tydelige skjevheter etter kriteriet** (> 2 SE, samme fortegn i alle fire rundene, fire runder). Første gang kriteriet kan slå inn:

| Poengsett | Gruppe | Skjevhet (SE) | n | Per runde R8 / R9 / R10 / R11 |
|---|---|---|---|---|
| codex | GKP < 5,0 | +0,97 (0,44) | 47 | +1,58 / +0,44 / +0,57 / +1,29 |
| codex | MID 5,0–7,4 | +0,39 (0,14) | 394 | +0,52 / +0,03 / +0,28 / +0,71 |
| codex | FWD 5,0–7,4 | +0,74 (0,36) | 92 | +0,47 / +0,54 / +1,19 / +0,90 |
| repo_hybrid | MID 7,5–9,9 | −1,40 (0,46) | 34 | −2,50 / −0,73 / −0,27 / −1,89 |
| repo_hybrid | FWD ≥ 10,0 | −4,76 (1,48) | 4 | −0,41 / −6,88 / −5,44 / −6,33 |

Forbehold som hovedagenten bør vurdere før noe brukes (kriteriet er oppfylt, men):
- **repo_hybrid FWD ≥ 10,0 er bare Haaland**, én observasjon per runde (forventet 8,4 / 8,9 / 7,4 / 8,3, faktisk 8 / 2 / 2 / 2).
  Kriteriet har ikke noe krav til antall spillere. Codex har samme fortegn i R9–R11, men ikke i R8 (−2,60, SE 1,53; ikke tydelig).
  Måling over tre sesonger (`gw11/beslutning.md`) ga +1,2 per runde i overvurdering for repo, altså mye mindre enn −4,8.
- Det er 26 grupper (13 per poengsett) som testes; med 2 SE ventes omtrent én falsk treff av ren tilfeldighet, men kravet om samme
  fortegn i fire runder demper det.
- Codex-skjevhetene for billige keepere, MID 5,0–7,4 og FWD 5,0–7,4 er positive (codex undervurderer), i tråd med codex-totalen
  (+0,34, SE 0,09, positiv alle fire rundene). Repo_hybrid har ingen av disse.
- Skjevhetene sier noe om nivået i gruppen, ikke om hvilke spillere innen gruppen som er feilvurdert.

Svakere mønstre (noteres, brukes ikke): repo_hybrid GKP < 5,0 +0,84 (SE 0,44, under 2 SE); topp ti repo_hybrid −1,29 (SE 0,68,
per runde −2,70 / +0,38 / −1,16 / −1,67, ikke samme fortegn); codex MID 7,5–9,9 −0,92 (SE 0,46, akkurat under 2 SE).
