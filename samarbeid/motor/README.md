# Ukemotoren

Ett fast, testet verktøy for den ukentlige FPL-beregningen. Erstatter engangsskriptene `gwNN/codex/modell*.py`.
Logikken er flyttet uendret fra `samarbeid/gw10/codex/modell.py` og `modell_r2.py`; plan og begrunnelse står i
`samarbeid/modell/plan-v2.md`, status i `samarbeid/modell/STATUS.md`.

Motoren regner. Den skriver ingen anbefaling: tolkning og beslutning er Claudes jobb, kontroll er Codex' jobb.

## Kjøre

```bash
export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH PYTHONDONTWRITEBYTECODE=1
python samarbeid/motor/kjor.py samarbeid/gwNN --frys         # én gang: frys repoets poengfiler i gwNN/motor/input/
python samarbeid/motor/kjor.py samarbeid/gwNN --bare-poeng   # sekunder: minutter.csv og spillerpoeng.csv
python samarbeid/motor/kjor.py samarbeid/gwNN                # alt: ca. 1 min + skadesimulering (200 verdener x 2 rater x 5 alternativer = ca. 7 min)
```

Krever `gwNN/data/` som i dag (med `element_summary/`, som ikke ligger i git) og `gwNN/motor/oppsett.json`.
Python 3.8 med numpy, numba og pulp (finnes i Anaconda). Ingen nett. Skriver bare i `gwNN/motor/`.

## Oppsett: `gwNN/motor/oppsett.json`

Mal: `tester/gw10_oppsett.json`. Feltene:

| Felt | Betydning |
|---|---|
| `runde` | Runden det tas beslutning for. Påkrevd. |
| `gratisbytter` | Gratisbytter tilgjengelig nå (1–5). Påkrevd. |
| `horisont_til` | Siste runde som regnes. Standard: 9 runder fram, men ikke forbi chipvinduet (19, senere 38). |
| `bank` | Millioner i banken. Standard: `last_deadline_bank` i `entry.json`. Oppgi den hvis Simen har byttet etter forrige frist. |
| `chips` | `{"BB": [runder], "FH": [runder]}`: runder der chipen lovlig kan brukes, alle innenfor horisonten. Tom liste = ikke tilgjengelig. FH kan ikke stå i inneværende runde. |
| `fh_start` | FH-runden som antas mens byttekandidater lages. Rutenettet finner den beste etterpå. Standard: første lovlige. |
| `maks_bytter` | Søket lager beste plan med 0, 1, …, så mange bytter (A, B, C, D3, D4). Standard 4. |
| `vekt_codex` | Vekt på `codex` i blandingen. Standard 0,5. Endres bare etter regelen i `plan-v2.md` del C. |
| `overstyringer` | Claudes minuttoverstyringer. Standard `claude/minutter_overstyring.csv` hvis filen finnes. |
| `minuttabell` | Alternativt: en hel frossen minuttabell (da brukes ikke overstyringene). |
| `alternativer` | Claudes egne forslag: `[{"navn": "...", "ut": [id, ...], "inn": [id, ...]}]`. Bruk spiller-ID; navn godtas bare når de er entydige. |
| `felles_chip` | `{"BB": runde, "FH": runde}` som alle alternativer sammenlignes på. Standard: beste fra rutenettet. |
| `ft_folsomhet` | Liste over andre antall gratisbytter som skal testes, f.eks. `[1, 2, 3]`. |
| `skadesim` | `{"trekk": 200, "rater": [0.01, 0.02], "fro": 7089878}`. `trekk: 0` slår den av. |
| `input_mappe`, `sesong` | Bare for tester og historiske kjøringer. |

`kjor.py` stopper med en feilmelding (og `Motor` med en `AssertionError`) i stedet for å regne på ugyldige verdier:
gratisbytter og `ft_folsomhet` som ikke er heltall 0–5, vekt utenfor [0, 1], chiprunder utenfor horisonten
(de ble før filtrert bort uten melding), `fh_start` som ikke er en tilgjengelig FH-runde, horisont forbi chipvinduet,
og WC/TC eller FH i inneværende runde.

## Minuttoverstyringer: `gwNN/claude/minutter_overstyring.csv`

Motoren lager selv en grunntabell (vektede starter, egne minutter per start, API-flagg). Claude legger nyheter oppå:

```csv
id,lag,gw_fra,gw_til,faktor,p_start,forventede_min,kilde
,BHA,10,10,0.95,,,torsdag Europa/søndag liga (antakelse)
124,,10,10,0.85,,,fot-smell; diagnose ukjent
238,,10,10,0,,,ute R10 (pressekonferanse 5. nov)
301,,12,19,,0.8,70,tilbake fra skade R12 (klubbens nettside)
```

- Enten `id` eller `lag` (kortnavn). Enten `faktor` eller `p_start`/`forventede_min`. `kilde` er påkrevd.
- Hver rad kontrolleres før den brukes: hele runder med `gw_fra` ≤ `gw_til`, **helt** innenfor horisonten (en rad som bare
  delvis ligger der, stopper kjøringen; den ble før klippet uten melding), og tall ≥ 0. Gjelder et fravær lenger enn
  horisonten, settes `gw_til` til horisontens siste runde. En rad som gir minutter uten sannsynlighet for å spille
  (p_start 0 for en spiller uten innhopp), stopper kjøringen.
- Radene brukes i filrekkefølge. `faktor` ganger både startandel og minutter. Verdiene gjelder per kamp.
- Spillere med status u/n/i/s eller 0 % er ute i hele horisonten. En rad som **setter** verdier for en slik spiller,
  gjør ham tilgjengelig i de rundene (kjent returdato). Han kan fortsatt ikke kjøpes av søket.
- `minutter.csv` i utmappen viser tabellen som faktisk ble brukt, med kilde per rad.

## Utdata i `gwNN/motor/`

| Fil | Innhold |
|---|---|
| `spillerpoeng.csv` | Alle spillere × runder: `codex`, `repo_hybrid`, `blend`, `p_start`, `p_spiller`, antall kamper. **Fryses av prognoseskriptet i rutinens steg 5 (`prognose/SHA256SUMS`); motoren skriver ikke den filen selv, og skriver spillerpoengene på nytt ved hver kjøring.** |
| `minutter.csv`, `lagstyrke.csv` | Antakelsene bak poengene. `retur` = 1 der en spiller som er ute, regnes likevel (kjent returdato), så tabellen kan brukes som `minuttabell` og gi de samme poengene. |
| `alternativer.csv` | A (rull), B, C, D3, D4 = søkets beste med 0–4 bytter, hver med sin beste BB-runde. E = valgt handling med hver BB-runde. F = med hver FH-runde. G = kapteinsvalg. |
| `alternativer_felles.csv` | A–D og Claudes egne alternativer på **samme** BB- og FH-runde. Dette er tabellen å sammenligne i. |
| `chiprutenett.csv` | Alle lovlige par av BB- og FH-runde for hvert antall bytter. |
| `chiprutenett_egne.csv` | Det samme for hvert av Claudes egne alternativer, så de også får sin egen beste chipdato. |
| `ft_folsomhet.csv` | A–D og Claudes egne alternativer regnet med hvert antall gratisbytter i `ft_folsomhet`, på de felles chipdatoene. Brukes til søkestøyen S i beslutningsregelen (`RUTINE.md` steg 5). |
| `kapteiner.csv` | De fire beste kapteinene med vise, spillerpoeng og verdien av ekstrakopien, begge poengsett. |
| `byttesok.csv` | Alle kandidater søket vurderte, med poengsum. |
| `planer.json` | Hele eierbanen per alternativ: tropp, ellever, benk, kaptein og vekter per runde. |
| `skadesim.csv`, `parvise.csv`, `skadetrekk.csv` | Paret skadesimulering: nivå, paret forskjell mot A, og rådata per verden. Uten tilgjengelig Bench Boost sammenlignes totalene uten BB. `kontroll.json` sier om simuleringen ble kjørt. |
| `kontroll.json` | Status, doble/blanke runder i horisonten, inndata-hasher, største avvik ved gjenregning. |

Kolonner: `_runde` = første runde, `_4r` = de fire første, `_horisont` = hele horisonten. Poeng er etter trekk.

## Slik leses tallene

- To poengsett vises alltid side om side. `blend` er vektet med `vekt_codex`. Er de uenige om rekkefølgen, er forskjellen ikke avgjort.
- Forskjeller under ca. ett poeng over horisonten er innenfor søkets og modellens støy.
- «Beste» betyr beste i et avgrenset søk, ikke bevist optimum.
- Skadesimuleringen måler spredning i *forventede* poeng mellom skadeverdener. Kampflaks og modellfeil er ikke med.

## Filene

| Fil | Innhold |
|---|---|
| `uke.py` | Innlesing av ukens data til ett `Uke`-objekt. |
| `poeng.py` | Lagstyrke, roller, minuttabell, rater, `codex`, `repo_hybrid`, P(spiller). |
| `lag.py` | Eksakte autobytter, kaptein/vise, valg av ellever (numba). |
| `motor.py` | Byttesøk, byttepolitikk, Free Hit, eierbane, alternativtabeller. |
| `skadesim.py` | Parede skadeverdener. |
| `kjor.py` | Kommandolinjen. |
| `historikk.py` | Historisk måling av poengsettene (plan-v2 del C). |
| `tester/` | Akseptansetester mot runde 10 og syntetiske tester. |

## Tester

```bash
cd samarbeid/motor
python -m pytest tester -q -p no:cacheprovider              # ca. 1,5 min
python -m pytest tester -q -p no:cacheprovider --langsom    # + ca. 4 min
```

- `test_gw10.py`: motoren gjenskaper Codex' tall for runde 10 (spillerpoeng, minuttabell, `alternativer.csv`,
  `alternativer_r2.csv`, chiprutenett, kapteiner, skadeverdener). Krever `samarbeid/gw10/data/element_summary/`
  (kopier fra en mappe som har den; den ligger ikke i git). Uten den hoppes testene over.
- `test_syntetisk.py`: liten liga med dobbeltrunde og blank runde. Autobyttene sammenlignes med
  `fasit_autobytter.py`, som går gjennom alle utfall med FPL-reglene skrevet rett fram.

**Endrer du noe i `poeng.py`, `lag.py` eller `motor.py`, skal `test_gw10.py` fortsatt bestå.** Skal tallene endres med vilje
(en modellendring), krever det forhåndsregistrering i `samarbeid/modell/`, og fasiten byttes da til en ny frossen uke.

## Kjente begrensninger

- Free Hit i inneværende runde er ikke bygget (trengs før R15, se `samarbeid/modell/STATUS.md` punkt 4). Wildcard og
  Triple Captain er heller ikke bygget (trengs før R20, se `plan-v2.md`).
- Minutter gjelder per kamp og er like for begge kampene i en dobbeltrunde.
- Horisonten stopper ved chipvinduet; ingen verdi av tropp, bank og gratisbytter etter siste runde.
- Prisendringer er ikke modellert. Søket er avgrenset (12 beste + 4 billigste per posisjon, enkeltbytter og par).
- Heltallsløseren (CBC) har 8 sekunders tidsgrense per forslag. På en mye tregere maskin kan forslagene bli andre.
