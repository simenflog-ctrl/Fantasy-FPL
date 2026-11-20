# Evaluering av prognosen for runde 10

Skrevet 2026-11-19 av agenten `fpl-datagrunnlag`. Faktiske poeng kommer fra `data/live_gw10.json` (hentet 2026-11-19 16:30 UTC),
og lagets resultat fra `data/picks_gw10.json`. Prognosen er `gw10/prognose/prognose_R10.json`
(frosset 2026-11-06 13:33 UTC, committet 13:34 UTC, fristen var 18:30 UTC).

## Sjekksum

`shasum -a 256 -c prognose/SHA256SUMS` for `samarbeid/gw10` (kjørt med absolutte stier i stedet for `cd`): alle fire OK
(`prognose/prognose_R10.json`, `codex/spillerpoeng.csv`, `data/bootstrap.json`, `data/fixtures.json`). gw10-mappen har ingen
uforpliktede endringer i git.

## Hva Simen faktisk gjorde

Nøyaktig som anbefalt: ingen bytter (event_transfers 0, ingen nye rader i `transfers.json`), ingen chip, samme ellever,
kaptein Haaland, visekaptein Gabriel og benkrekkefølge Tzolakis, Silva, Rudoni, Dasilva. **Ingen avvik.**
Offisielt resultat: **88 poeng** (snitt 55, høyest 139), rundens rank 79 055, 12 poeng på benken, ingen autobytter
(alle elleve spilte). Totalrank gikk fra 2 209 960 til 1 122 827.

## Anbefalt mot alternativ (faktiske poeng)

Anbefalt plan var å rulle, så den er også referansen uten bytter. Det frosne alternativet er Codex' knappe førstevalg
(`alternativ_codex`: Ødegaard, Dasilva → Iwobi, Van Hecke). Prognosen regnet med faste ellever uten autobytter. Ingen av elleverne
hadde spillere med 0 minutter, så autobytter endrer ingenting.

| Plan | Forventet codex | Forventet repo_hybrid | Faktisk (fast = med autobytter) |
|---|---|---|---|
| Anbefalt: rull (= referanse uten bytter) | 56,3 | 64,7 | **88** |
| Alternativ_codex: Ødegaard, Dasilva → Iwobi, Van Hecke | 56,2 | 65,0 | **79** |
| **Anbefalt − alternativ** | +0,1 | −0,3 | **+9** |

Hele forskjellen i ellever er Ødegaard 11 poeng mot Iwobi 2 (begge 90 minutter). På benken ville Van Hecke (4) ha stått i stedet
for Dasilva (1), men benken telte ikke. Forventet gevinst for rull over R10–R13 var +1,2 (codex) og +1,6 (repo_hybrid); R10 sto for
+0,1 og −0,3 av den. Resten (R11–R13) kan ikke måles direkte, fordi planene forutsatte samme ellever, og laget kan endres i R11.
Valget mellom planene var uavgjort i forventning (`gw10/beslutning.md`). At rull vant med 9 poeng, er utfallet av én spiller i én runde
og sier ikke at valget var bedre.

Spillere i anbefalt ellever (faktisk / forventet codex / forventet repo_hybrid):
Trafford 10 / 4,0 / 4,2; Gabriel 8 / 5,4 / 6,7; De Cuyper 6 (81 min) / 4,4 / 4,9; Muharemović 10 / 4,1 / 4,7; Ødegaard 11 / 4,4 / 4,9;
Tavernier 3 / 4,7 / 5,3; Groß 10 / 3,3 / 4,0; Mbeumo 2 (82 min) / 5,5 / 6,0; Barry 16 / 4,8 / 4,8; Isak 8 / 4,9 / 4,5;
Haaland (C) 2×2 / 5,4×2 / 7,4×2. Benk: Tzolakis 6, Silva 3, Rudoni 2 (85 min), Dasilva 1.
Alternativets to spillere: Iwobi 2 / 4,35 / 5,19; Van Hecke 4 / 4,07 / 4,62.

## Mot de to poengsettene

- **Codex:** anbefalt 88 er 31,7 over prognosen på 56,3, og alternativet 79 er 22,8 over prognosen på 56,2.
- **Repo-hybrid:** anbefalt 88 er 23,3 over prognosen på 64,7, og alternativet 79 er 14,0 over prognosen på 65,0.
- Overskuddet kom fra Barry 16 (+11,3 i begge poengsett), Groß 10, Ødegaard 11, Trafford 10 og Muharemović 10 (hver +5 til +7).
  Haaland som kaptein trakk ned: 4 poeng mot forventet 10,8 (codex) og 14,9 (repo_hybrid), andre runde på rad med 2 poeng.
  Mbeumo (2) og Tavernier (3) lå også under.
- Hele spillet hadde en høy runde (snitt 55 mot 45 og 47 i R8 og R9), så noe av overskuddet er felles for alle lag.

## Løpende tabell

| Runde | Handling | Anbefalt faktisk | Referanse faktisk (fast / autobytter) | Forventet gevinst (codex / repo) | Faktisk gevinst (fast / autobytter) | Lagets poeng (offisielt) |
|---|---|---|---|---|---|---|
| R8 | Szoboszlai → Tavernier, WC holdt | 61 | 51 / 53 | +1,4 / +1,7 | +10 / +8 | 61 |
| R9 | Wildcard (11 inn) | 48 | 57 / 57 | +8,0 / +7,4 | −9 / −9 | 48 |
| R10 | Rull (ingen bytter), ikke BB | 88 | 88 / 88 (= anbefalt) | 0 / 0 | 0 / 0 | 88 |
| **Sum** | | 197 | 196 / 198 | +9,4 / +9,1 | +1 / −1 | 197 |

Anbefalt mot frosset alternativ (bare runder der alternativet ikke er referansen):

| Runde | Alternativ | Alternativ faktisk | Forventet gevinst for anbefalt (codex / repo) | Faktisk gevinst |
|---|---|---|---|---|
| R10 | Ødegaard, Dasilva → Iwobi, Van Hecke | 79 | +0,1 / −0,3 i R10 (R10–R13: +1,2 / +1,6) | +9 |

Anbefalt plan, forventet mot faktisk (fast ellever):

| Runde | Forventet codex | Forventet repo_hybrid | Faktisk | Faktisk − codex | Faktisk − repo_hybrid |
|---|---|---|---|---|---|
| R8 | 52,3 | 64,0 | 61 | +8,7 | −3,0 |
| R9 | 56,0 | 62,8 | 48 | −8,0 | −14,8 |
| R10 | 56,3 | 64,7 | 88 | +31,7 | +23,3 |
| **Sum** | 164,6 | 191,5 | 197 | +32,4 | +5,5 |

Ett utfall beviser lite, og tre gjør det heller ikke. Summen over R8–R10 ligger nær repo_hybrid og over codex, men spriket fra runde
til runde (−15 til +32) er mye større enn forskjellen mellom poengsettene.

## Prognoseevaluering (spillernivå)

R10 er lagt inn i `samarbeid/kalibrering/logg.csv` med `oppdater.py`: 273 spillere med forventet ≥ 1 i minst ett poengsett,
30 av dem med 0 minutter. Kilden er den frosne `gw10/codex/spillerpoeng.csv` (gw == 10; sjekksummen er kontrollert av skriptet),
og prisene er fra `gw10/data/bootstrap.json`. Oversikten står i `samarbeid/kalibrering/oversikt.md`.

| Utvalg | Codex skjevhet (SE) | Repo_hybrid skjevhet (SE) |
|---|---|---|
| R10 alle | +0,37 (0,17) | +0,13 (0,17) |
| R8–R10 alle | +0,37 (0,10) | +0,13 (0,10) |
| Topp ti forventet, R8–R10 | +0,40 (0,85) | −1,16 (0,83) |

Svakere mønstre (over 2 SE og samme fortegn i alle tre rundene, men bare tre runder):
- Codex, MID 5,0–7,4: +0,29 (SE 0,14, n = 297); per runde +0,52, +0,03, +0,28.
- Repo_hybrid, MID 7,5–9,9: −1,22 (SE 0,60, n = 25); per runde −2,50, −0,73, −0,27 (avtagende).
- Repo_hybrid, FWD ≥ 10,0: −4,24 (SE 1,96, n = 3, bare Haaland: forventet 8,4 / 8,9 / 7,4, faktisk 8 / 2 / 2).
- Codex totalt: +0,37 (SE 0,10), positiv i alle tre rundene. Totalen er ikke en av gruppene i kriteriet, så den noteres bare.

Mønsteret fra forrige uke for MID ≥ 10,0 (bare B.Fernandes) er ikke lenger over 2 SE etter 10 poeng i R10.
Disse noteres, men brukes ikke. **Ingen tydelige skjevheter ennå (3 runder).** Kriteriet krever minst fire runder, så tidligst etter R11.
