# Plan v2: ukemotoren

Skrevet 16. november 2026 av Claude (Fable 5.2), før noen kode i `samarbeid/motor/` og før noen måling av poengsettene.
Kravene i del C er forhåndsregistrert her og endres ikke etter at tallene er sett.

## Hvorfor

1. Ukeberegningen er et engangsskript Codex skriver om hver uke (238 linjer i gw08, 696 i gw10). Det er aldri testet mot
   historiske sesonger, og Codex har gått tom for kvote midt i analysen fem ganger på to uker.
2. De to poengsettene (`codex` og `repo_hybrid`) er uenige om toppspillere (Haaland 5,4 mot 7,4 i R10) og vektes likt uten måling.
3. Små forbedringer av repo-modellen (P1, P2) ga 0,2 % lavere feil. Beslutningene avgjøres ofte av under ett poeng, så
   gevinsten ligger i et fast, etterprøvbart verktøy og en målt vekting, ikke i flere små modelljusteringer.

Målet er ett fast verktøy som Opus og Codex kan kjøre resten av sesongen uten å skrive modellkode. Codex' ukeoppdrag blir da
«kjør motoren, kontroller resultatet, test innvendinger», ikke «skriv modellen på nytt».

## A. Arkitektur

Mappe `samarbeid/motor/`. Python 3.8 (Anaconda), numpy, numba, pulp. Ingen nett, ingen skriving utenfor ukens `motor/`-mappe.
All logikk er flyttet fra `samarbeid/gw10/codex/modell.py` og `modell_r2.py`; formlene er uendret.

| Fil | Innhold | Flyttet fra gw10 |
|---|---|---|
| `uke.py` | Leser ukens `data/`, oppsett og frosne repo-filer til ett `Uke`-objekt. Ingen globale variabler. | linje 22–30, 121–125 |
| `poeng.py` | Lagstyrke, roller, minuttabell med overstyringer, rater, `codex`-poeng, `repo_hybrid`, P(spiller). | linje 32–149 |
| `lag.py` | Eksakte autobytter (oppslagstabell), kaptein/vise, valg av ellever og benk. Rene numba-funksjoner. | linje 151–290 |
| `motor.py` | Klassen `Motor`: byttesøk, rullerende byttepolitikk, Free Hit-tropp, heltallsforslag, eierbane, kapteintabell. | linje 292–475, 537–548 |
| `skadesim.py` | Parede skadeverdener (samme fravær i alle alternativer og begge poengsett). | linje 577–594, r2 linje 83–106 |
| `kjor.py` | Kommandolinje: `python samarbeid/motor/kjor.py samarbeid/gwNN`. Skriver alle utdata. | `main()` i begge |
| `historikk.py` | Bygger motorens inndata fra historiske sesonger (del C). | ny |
| `tester/` | Akseptansetester mot gw10, syntetiske tester, uavhengig fasit for autobytter. | ny |

### Inndata

- `gwNN/data/`: `bootstrap.json`, `fixtures.json`, `salgspriser.json`, `entry.json`, `element_summary/` (som i dag).
- `gwNN/motor/input/player_matches.csv` og `expected_points.csv`: frosne kopier av repoets `data/derived/`. `kjor.py --frys`
  lager kopiene og nekter å overskrive.
- `gwNN/motor/oppsett.json` (Claude skriver): runde, horisont, **antall gratisbytter**, bank, **chipstatus** (lovlige runder for
  BB og FH; tom liste = ikke tilgjengelig), vekt på `codex`, egne alternativer (ut/inn med spiller-ID), felles chipdatoer for
  sammenligning, skadesimulering (antall verdener, rater, frø).
- `gwNN/claude/minutter_overstyring.csv` (Claude skriver): `id` eller `lag`, `gw_fra`, `gw_til`, og enten `faktor`
  (ganges inn i startandel og minutter) eller `p_start`/`forventede_min` (settes). Kolonnen `kilde` er påkrevd. Radene brukes i
  filrekkefølge oppå motorens grunntabell. Alternativt en hel frossen minuttabell (`minuttabell` i oppsettet).

### Utdata (i `gwNN/motor/`)

| Fil | Innhold |
|---|---|
| `spillerpoeng.csv` | Alle spillere × alle runder i horisonten: `codex`, `repo_hybrid`, `p_start`, `p_spiller`. Fryses i `prognose/SHA256SUMS`. |
| `minutter.csv` | Minuttabellen som faktisk ble brukt, med kilde per rad. |
| `alternativer.csv` | Rangerte alternativer: rull, beste 1/2/3/4 bytter fra søket og Claudes egne, i begge poengsett og blanding, med trekk og bank. |
| `chiprutenett.csv` | Alle lovlige par av BB-runde og FH-runde per alternativ, i begge poengsett. |
| `kapteiner.csv` | Kaptein og vise: spillerpoeng og verdien av ekstrakopien, i begge poengsett. |
| `planer.json` | Hele eierbanen per alternativ: tropp, ellever, benk, kaptein, vekter per runde (gjør hvert tall etterprøvbart). |
| `skadesim.csv`, `parvise.csv`, `skadetrekk.csv` | Paret skadesimulering: nivå per alternativ og paret forskjell mot rull. |
| `kontroll.json` | Automatiske kontroller: budsjett, posisjoner, klubbgrense, gjenregning fra spillerfil og vekter. |

Motoren skriver ingen anbefaling og ingen rapporttekst. Tolkning og beslutning er Claudes jobb.

### Dobbeltrunder og blanke runder

gw10-skriptet hadde ingen i horisonten, og er ikke testet for dem. Motoren regner slik:

- `codex`: summen over rundens kamper (to kamper teller to ganger; ingen kamp gir 0).
- `repo_hybrid`: summen av repoets rader for runden, hver skalert med motorens minutter. (gw10-skriptet ville beholdt bare én rad.)
- P(spiller) i runden: 1 − (1 − p)^antall kamper; 0 uten kamp. En spiller uten kamp utløser autobytte som en som ikke spiller.
- Minutter gis per kamp og gjelder begge kampene i en dobbeltrunde. Egne minutter per kamp er ikke støttet (se del D).

## B. Akseptansetester

Kjøres med `python -m pytest samarbeid/motor/tester`. Resultatet føres i `STATUS.md`.

1. **Spillerpoeng**: alle 670 spillere × R10–R19 i `gw10/codex/spillerpoeng.csv` og `spillerpoeng_R18_R19.csv`, begge poengsett,
   avvik < 0,000001. P(spiller) mot `p_play.csv`, lagstyrke mot `lagstyrke.csv`.
2. **Minuttabell**: grunntabell + en overstyringsfil som uttrykker gw10-antakelsene (Europa-lagene ×0,95, Groß ×0,85,
   Grealish/Crooks 0 i R10, Morita/Toth 0) skal gi `minutter_antatt.csv` eksakt.
3. **`alternativer_r2.csv`**: de fem planene (A, B, C, Claude_Iwobi, Claude_Evanilson) med BB12/FH13, alle seks poengkolonner,
   bank og trekk: avvik ≤ 0,05 poeng.
4. **`alternativer.csv`**: alle 29 rader (A–D4, E, F, G), alle seks poengkolonner, BB/FH-valg, ut/inn, bank og trekk: avvik ≤ 0,05.
   Kolonnene `skade_p10_blend`/`skade_p90_blend` (100 verdener, 2 %) testes i en egen langsom test.
5. **Paret skadesimulering**: de første 20 verdenene ved 2 % for A og B skal gi tallene i `skadetrekk_r2.csv` innen 0,05.
6. **Syntetisk liga** (6 lag, dobbeltrunde og blank runde):
   - spiller med to like kamper får nøyaktig 2 × enkeltkamp; spiller uten kamp får 0 poeng og P(spiller) 0;
   - `repo_hybrid` summerer to rader i en dobbeltrunde;
   - autobytter: forventet lagpoeng fra motoren = uavhengig fasit som går gjennom alle 2^15 utfall av hvem som spiller, med
     FPL-reglene skrevet rett fram (keeper mot keeper, benkerekkefølge, minst 3 forsvar / 2 midtbane / 1 spiss), også når en
     startspiller har blank runde;
   - Bench Boost: alle 15 teller, pluss kaptein;
   - kaptein uten kamp: visekapteinen får doblingen;
   - eierbanen: budsjett, klubbgrense og gratisbytter holder gjennom en horisont med dobbel og blank runde.

Tallene i gw10 er fasit for *flyttingen*, ikke for fotballen: testene viser at motoren regner det samme som skriptet Codex og
Claude kontrollerte, ikke at prognosen er riktig. Det siste er del C.

## C. Forhåndsregistrert måling av poengsettene

### Kan ukemodellen kjøres historisk?

Ja, med forbehold. `codex`-settet er en ren funksjon av: sesongtall per spiller til og med forrige runde, kamphistorikk per
spiller, sesongtotaler fra tidligere år, kampprogram og poengregler. Alt dette kan bygges fra den lokale kopien av vaastav-dataene
(`data/cache/vaastav`, 2022/23–2025/26), slik `src/eval_engine.py` allerede gjør for repo-modellen. `historikk.py` bygger disse
inndataene og kaller de samme funksjonene i `poeng.py` som ukekjøringen bruker.

Det som **ikke** kan gjenskapes historisk, og derfor ikke måles:

- API-flagg (skade, prosent) og Claudes minuttoverstyringer. Alle settes tilgjengelige, som i P0–P2. Målingen gjelder
  ratemodellen og grunnminuttene, ikke hele ukekjeden.
- Defensive bidrag finnes først i 2025/26. For 2023/24 og 2024/25 settes de poengene til 0 i begge sett.
- 2023/24 har bare én tidligere sesong (2022/23) som prior; ukemodellen bruker to.
- Repo-modellen er tidligere justert på nettopp disse tre sesongene; `codex`-konstantene (540/270, 7 kamper, 1,1/0,9) er ikke det.
  Sammenligningen er derfor skjev **i repo-modellens favør**.

Den eneste målingen av hele ukekjeden er den løpende loggen `samarbeid/kalibrering/logg.csv` (3 runder nå). Den brukes som
supplement, se «Nest beste» under.

### Oppsett (låst)

- Sesonger 2023/24, 2024/25, 2025/26. Runder 8–38. Én runde fram (prognose for runde t laget med data til og med t−1).
- Enhet: spiller–runde (dobbeltrunder summert), alle spillere som har prognose i begge sett, også de med 0 minutter.
- Kandidater: `repo` (repoets egne minutter), `repo_hybrid` (repo skalert med motorens minutter), `codex`, og blandingene
  w·`codex` + (1−w)·`repo_hybrid` for w ∈ {0,25, 0,50, 0,75}. Dagens praksis er w = 0,50.
- Mål: MSE mot faktiske poeng (hovedmål). Topp 10 og topp 20 (snitt av faktiske poeng for de høyest rangerte per runde).
  Skjevhet (prognose − faktisk) per posisjon × prisklasse, særlig spisser og midtbane ≥ 10,0. Spearman blant dem som spilte.
- Usikkerhet: fire-runders blokker innen sesong (8 per sesong, 24 samlet), parede forskjeller, som i P1/P2-målingen.
- Poengregler per sesong: keepermål 6 før 2026/27, defensive bidrag 0 før 2025/26. Ellers reglene i `gw10/data/bootstrap.json`.

### Valg av vekt (låst)

1. w velges blant {0, 0,25, 0,50, 0,75, 1} som lavest samlet MSE på **2023/24 + 2024/25**. 2025/26 er kontrollår og brukes ikke i valget.
2. Vekten endres fra 0,50 til den valgte w* bare hvis **alle** kravene holder:
   - samlet MSE (tre sesonger) er minst **0,5 % lavere** enn ved w = 0,50, og forskjellen er minst **3 blokk-SE**;
   - samme fortegn i alle tre sesonger, også kontrollåret alene;
   - topp 10 er ikke dårligere enn ved w = 0,50 med mer enn 2 blokk-SE.
3. Holder ikke kravene: vekten blir stående på 0,50 og resultatet føres som **UAVKLART**. Ingen ny runde med andre vekter,
   andre runder eller andre mål på de samme sesongene.
4. Uansett utfall rapporteres: skjevhet for spisser og midtbane ≥ 10,0 i hvert sett, og om `repo_hybrid` er bedre enn `repo`.
   Det er diagnoser. En nivåjustering av toppspillere krever egen forhåndsregistrering.

Fordi sammenligningen er skjev i repo-modellens favør, tolkes «`codex` like god eller bedre» som et reelt funn, mens
«`repo_hybrid` litt bedre» ikke alene er grunn til å senke `codex`-vekten. Kravene over tar hånd om det.

### Nest beste (hvis den historiske kjøringen ikke lar seg gjennomføre, og som supplement ellers)

Den løpende loggen måler hele ukekjeden, men vokser med én runde i uka. Regel, låst nå: når loggen har minst **8 runder**
(tidligst etter R17), sammenlignes MSE for `xp_codex`, `xp_repo` og 50/50 på radene med forventet poeng ≥ 1, med runden som
klynge. Vekten flyttes ett trinn (0,25) mot det beste settet bare hvis forskjellen er over 2 runde-SE og har samme fortegn i
minst 6 av 8 runder. Inntil da: 0,50, og begge poengsett vises alltid side om side i alle tabeller.

## D. Hva som bevisst ikke gjøres

- **Ingen endring av formlene nå.** `max(0, …)`, 540/270-krympingen, 7-kampersprioren og 1,1/0,9 for hjemmebane flyttes uendret.
  Først et testet verktøy som gir samme tall, deretter eventuelle endringer én om gangen med forhåndsregistrering.
- **Ingen nivåjustering av toppspillere** (Haaland). Skjevheten rapporteres; justering krever egen registrering.
- **Ingen rapporttekst eller anbefaling fra motoren.** gw10-skriptenes `report()` (store f-strenger) flyttes ikke. Claude skriver beslutningen.
- **Ingen engangsfølsomheter** (Groß-testen). Én spillers minutter testes ved å kjøre motoren med en annen overstyringsfil.
- **Ingen endring i `src/`, `config/`, `tests/`, `data/`**, og ingen sammenslåing med repoets optimizer. Motoren leser repoets
  frosne poengfil som det ene poengsettet, mer ikke.
- **Wildcard, Triple Captain og Free Hit i inneværende runde** bygges ikke nå: WC1 og TC1 er brukt, og begge kommer tilbake
  først fra R20. Det må inn før analysen for R20 (se rekkefølgen under). Minutter per kamp i dobbeltrunder venter til den første dobbeltrunden er annonsert.
- **Ikke lengre horisont enn chipvinduet** (til R19 nå, R20–R38 senere) og ingen terminalverdi. Kjent begrensning fra gw10.
- **Ingen ny måling av P1/P2** og ingen bonusmodell. Lite å hente (0,2 %).
- **Rutinen endres ikke i denne økten.** `main` og analysen for R11 (frist 21. november) kjøres på gammel måte. Motoren tas i
  bruk først når Codex har kontrollert den og Simen har sagt ja til fletting.

## Rekkefølge

1. `uke.py`, `poeng.py`, `lag.py` + akseptansetest 1–2 og syntetiske tester for dobbel/blank runde og autobytter.
2. `motor.py` + akseptansetest 3–4 (alternativene).
3. `skadesim.py` + akseptansetest 5.
4. `kjor.py` (kommandolinje og utdatafiler) + `README.md`.
5. `historikk.py` og målingen i del C. Resultat i `samarbeid/modell/maling-poengsett.md`.
6. Codex kontrollerer motoren uavhengig (egen økt, ikke i dag).
7. Etter Simens ja: flett til `main`, oppdater `RUTINE.md` (steg 3: Codex kjører motoren; steg 4: kritikk mot motorens tall).
8. Før R20: Wildcard, Triple Captain, Free Hit i inneværende runde og andre halvdels chipsett, med egne tester.
