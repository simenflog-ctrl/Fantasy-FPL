# Status modellarbeid (27. november 2026)

To spor. **Ukemotoren** (nytt, øverst) er det som gjelder nå. Repo-modellens P1/P2 (nederst) er parkert.

Motoren, denne mappen og ny `RUTINE.md` ble flettet til `main` 27. november, etter R12-fristen. Fra R13 regnes uken med
motoren. Utviklingsgrenen `ukemotor-fletting` har i tillegg `modellforbedring` (endringer i `src/`), som ikke er flettet.
R11 og R12 ble regnet på gammel måte fra `main`, R11 med motoren som prøvekjøring ved siden av (`samarbeid/gw11/motor/`).

## Ukemotoren (`samarbeid/motor/`)

Plan og forhåndsregistrering: `plan-v2.md`. Bruksanvisning: `samarbeid/motor/README.md`.

### Ferdig

| Del | Hva | Test |
|---|---|---|
| `uke.py`, `poeng.py` | Innlesing, lagstyrke, minuttabell med overstyringsfil, `codex` og `repo_hybrid`. Dobbel og blank runde håndtert. | bestått |
| `lag.py` | Eksakte autobytter, kaptein/vise, valg av ellever. | bestått |
| `motor.py` | Byttesøk, byttepolitikk, Free Hit, eierbane, rutenett BB × FH, kapteintabell, felles chipdatoer. | bestått |
| `skadesim.py` | Paret skadesimulering. | bestått |
| `kjor.py` | Kommandolinje som skriver alle utdatafiler. | bestått |
| `historikk.py` | Historisk måling av poengsettene. | kjørt, se under |

### Akseptansetester (kjørt 16. november, alle bestått; sist kjørt 21. november)

`cd samarbeid/motor && python -m pytest tester -q -p no:cacheprovider --langsom`: **25 av 25 bestått**
(23 i standardkjøringen på 72 s, pluss 2 langsomme på til sammen ca. 4 min).
21. november, etter rettingene i 4ed2cbc: **62 av 62 bestått** med `--langsom` (251 s; standardkjøringen 60 bestått, 2 hoppet over,
75 s; logg `claude/pytest-langsom-4ed2cbc.log`). Tallene under er uendret: rettingene stopper bare ugyldige oppsett.
23. november, etter F3 og F7 i d428750: **66 av 66 bestått** med `--langsom` (245 s; standardkjøringen 64 bestått, 2 hoppet
over; logg `claude/pytest-langsom-d428750.log`).

| Krav i plan-v2 del B | Resultat |
|---|---|
| 1. Spillerpoeng, 670 spillere × R10–R19, begge sett | Største avvik 0,0000005 (avrunding i CSV). P(spiller) og lagstyrke eksakt. |
| 2. Minuttabell fra grunntabell + overstyringsfil | Eksakt lik `minutter_antatt.csv` (alle 6700 rader). |
| 3. `alternativer_r2.csv` (5 planer, BB12/FH13) | Avvik 0,00 på alle poengkolonner, bank og trekk. Krav: 0,05. |
| 4. `alternativer.csv` (29 rader: A–D4, E, F, G) | Avvik under 0,05 på alle rader; samme valg (B), BB12, FH13, samme ut/inn. Chiprutenettet (alle celler) og kapteintabellen stemmer. |
| 4b. `skade_p10/p90_blend` (100 verdener, 2 %) | Innen 0,05 for A–D4 (langsom test). |
| 5. Skadeverdener mot `skadetrekk_r2.csv` | De 10 første verdenene for A og B innen 0,05. |
| 6. Syntetisk liga med dobbel og blank runde | To like kamper = nøyaktig 2 ×; ingen kamp = 0 poeng og P(spiller) 0; `repo_hybrid` summerer to rader. Autobyttene er lik en uavhengig gjennomgang av alle 2^15 utfall (avvik < 0,000000001), også med blank runde i elleveren. Bench Boost teller alle 15. Visekapteinen arver. Eierbanen holder budsjett, klubbgrense og gratisbytter. |
| Ende til ende | `kjor.py` med gw10-oppsettet skriver alle filer og gjenskaper `alternativer_r2.csv` (langsom test). |

I tillegg kjørt uendret på gw09-dataene (63 s, kontroll OK) for å vise at ingenting er låst til runde 10.

Planen sa «26 rader» i `alternativer.csv`; filen har 29. Rettet i planen før testen ble kjørt ferdig. Ellers ingen avvik fra planen.

### Måling av poengsettene (plan-v2 del C)

Kjørt 16. november etter at kravene var låst (commit a7cf667). Fullt resultat: `maling-poengsett.md`.

**UAVKLART etter den låste regelen: vekten blir stående på 0,50.** 70 899 spiller-runder, 2023/24–2025/26, runde 8–38.

- Blandingen 50/50 er bedre enn hvert sett alene i alle tre sesonger (MSE 4,110 mot 4,132 for `repo_hybrid` og 4,116 for
  `codex`; topp 10: 5,53 mot 5,48 og 5,32). Dagens praksis er altså støttet av måling.
- Utviklingsårene pekte på w = 0,75, men ingen av de fire kravene holdt (0,02 % lavere MSE, og topp 10 ble 0,17 dårligere).
- `codex` treffer bredden litt bedre, `repo_hybrid` rangerer toppen bedre.
- Spisser ≥ 10,0: `repo_hybrid` overvurderer med 1,2 poeng per runde (alle tre sesonger), `codex` med 0,4, blandingen med 0,8.
  `codex` undervurderer midtbane 7,5–9,9 med 0,4. Dette er diagnoser; en nivåjustering krever egen forhåndsregistrering.
- Ikke målt: API-flagg og Claudes overstyringer. Den løpende loggen i `samarbeid/kalibrering/` er eneste måling av hele kjeden.

### R11-lærdom: beslutningsregel og søkestøy (regelen gjelder fra 27. november)

Kilder på `main`: `samarbeid/gw11/beslutning.md`, `gw11/codex/kontroll.md` og `gw11/codex/ft_sensitivitet.csv` (Codex' tall, BB11/FH15).

**Uenigheten.** Codex valgte C (Dasilva, Mbeumo → Van Hecke, Le Fée) fordi C har høyest 50/50-blanding. Claude valgte B
(Muharemović → Van Hecke) fordi B er positiv mot rull i begge poengsett, mens C er negativ mot rull i `codex` ved 3 og 4 FT.
Prisen var ca. 1,1 poeng i blandingen (C − B ved 2 % nye fravær: −1,44 / +3,70, blanding +1,13). Uenigheten gjaldt regelen, ikke
tallene. Regelen står nå i `RUTINE.md` steg 5.

**Søkestøyen.** Med en optimal byttepolitikk kan et ekstra gratisbytte aldri gi lavere total: de samme senere byttene kan alltid
gjøres med like mange eller færre trekk. Cs totaler faller likevel (codex / repo_hybrid, R11–R19):

| Plan | 2 FT | 3 FT | 4 FT |
|---|---|---|---|
| A (rull) | 567,69 / 621,18 | 567,96 / 621,53 | 568,62 / 621,70 |
| B | 568,60 / 622,63 | 568,62 / 622,64 | 568,89 / 623,00 |
| C | 569,08 / 623,33 | **566,59** / 628,31 | 566,93 / **626,48** |
| C − B, blanding | +0,59 | +1,82 | +0,76 |

C faller 2,49 i `codex` fra 2 til 3 FT og 1,83 i `repo_hybrid` fra 3 til 4 FT. Det kan ikke være reelt: byttepolitikken finner ulike
senere baner for C (Mbeumo tilbake, Isak → N.Jackson). A og B stiger jevnt. Ved 2 FT er C foran B i begge poengsett.
Søket har en støykilde til: `fh_start` avgjør hvilken kandidat som blir «C» (punkt 2 under: D3 med FH13, C med FH16).

**Beslutningsregel** (i `RUTINE.md` steg 5 fra 27. november; Simen valgte ikke en av de andre variantene, så forslaget gjelder
til han bestemmer noe annet):

1. Førstevalget X er planen med høyest blanding (`vekt_codex` 0,5) på felles chipdatoer, med den parede skadetesten når den finnes.
2. R er den beste planen i blandingen som ikke er dårligere enn rull i noe poengsett. Rull oppfyller kravet selv.
3. Velg R i stedet for X bare når **begge** vilkår holder:
   a. poengsettene er uenige om fortegnet på X − R;
   b. blandingsfordelen X − R er mindre enn ukens søkestøy S.
   Forventningstapet oppgis da i `beslutning.md`.
4. S måles, ikke skjønnes: det største fallet i totalen til X eller R, i ett av poengsettene, når antall gratisbytter øker med én
   (FT−1, FT og FT+1 i `ft_folsomhet`). Minst 1,0, som er README-grensen for støy. S er et nedre anslag: bare støy som bryter
   kravet om stigende totaler, blir målt.

Utfall i R11 med de tre regelvariantene:

| Regel | 3 FT (faktisk) | 2 FT |
|---|---|---|
| Ren blanding (Codex) | C (+1,13) | C |
| Enighet kreves alltid når settene er uenige om fortegnet (Claudes R11-praksis) | B | C (enige) |
| **Forslaget**: enighet kreves bare når fordelen er under S | **B** (+1,13 < S = 2,49) | C (enige) |

Forslaget gir samme valg som Claude i R11, men bare fordi fordelen var mindre enn den målte støyen. Hadde C vært foran med mer enn
2,49, ville C blitt valgt. Når søkestøyen reduseres (tiltak 3 under), blir S oftere gulvet på 1,0, og blandingen avgjør oftere.

**Forslag til tiltak mot søkestøyen.** Codex mener (motorkontrollen 21. november) at `fh_start`-avhengigheten kan håndteres i
rutinen for R12 og ikke krever en ny søkealgoritme først. Derfor i tre trinn:

1. *Fra R13, i rutinen* (står i steg 4; ingen kodeendring): er rutenettets beste FH-runde en annen enn `fh_start`, kjøres motoren på nytt med
   `fh_start` lik den før beslutningen. `ft_folsomhet` med FT−1 og FT+1 står fast i oppsettet, så S kan regnes.
2. *Før motoren går uten tilsyn, uten å endre tallene for en gitt plan* (ingen forhåndsregistrering; av/på i `oppsett.json`, så
   gw10-fasiten fortsatt gjelder): søket rangerer de tre beste kandidatene per antall bytter på nytt over alle lovlige FH-datoer og
   bruker den beste datoen for hver kandidat. FH-datoen er et valg vi tar senere, så det beste er riktig mål. Motoren skriver S og
   fortegnssjekken i `kontroll.json`. Antall gratisbytter brukes til å måle støyen, ikke til å rangere: det er en tilstand, ikke et
   valg. Kostnaden (omtrent 3 × 5 × antall FH-datoer ekstra eierbaner) må måles før det slås på.
3. *Senere, endrer tallene* (krever forhåndsregistrering etter `plan-v2.md` del D): hver plan regnes med det samme settet av senere
   baner (dem politikken finner ved 1–5 FT), og den beste beholdes. Da stiger totalene med antall gratisbytter per konstruksjon.
   Måles mot dagens politikk på gw09–gw11 før det tas i bruk.

### Gjenstår, i denne rekkefølgen

1. **Codex kontrollerer motoren uavhengig.** *Ferdig 23. november: «klar til bruk fra R12» (6e0cafa).*
   - 19. november (`codex/oppdrag-motorkontroll.md`): Codex stoppet på bruksgrensen etter ca. 8 minutter. Fem funn ble rettet i
     e5cde2e (WC/TC og felles BB/FH stoppes, horisont over chipvinduet, manglende overstyringsfil, G-radenes `modellspredning`,
     `--frys` fra ukemappens repo).
   - 21. november (`codex/oppdrag-motorkontroll-2.md`, ny tråd fra `ukemotor-fletting`): Codex fullførte steg 1–4 og stoppet på
     bruksgrensen i steg 5 (rapport `codex/motorkontroll.md`, skript `codex/motorkontroll_*.py`, logger i `codex/motorkontroll-data/`;
     commit 65dc803). **Ekvivalens mot gw10-skriptene: OK** for regnelogikken fasiten dekker (`lag.py` AST-identisk; samme
     formler i `poeng.py`, `motor.py`, `skadesim.py`; de 20 første skadeverdenene avviker 0,0). F4, F8 og F10 rettet, F5 akseptert.
     **Codex' dom** (siste melding før stoppen, `claude/codex-motorkontroll-2-utdata.log`): «klar etter disse rettingene», og
     «søkets avhengighet av en lovlig `fh_start` kan håndteres i R12-rutinen; den krever ikke en ny søkealgoritme først».
   - **Rettet av Claude i 4ed2cbc** (23 nye tester; 60 bestått, 2 hoppet over; gw10-fasiten uendret): F1 `fh_start`/FH som ikke er
     tilgjengelig, F2 ikke-heltallige gratisbytter, FT-følsomhet og vekt, F3 overstyringsrader med omvendt intervall eller tekst
     som tall, **F6 skadesimuleringen ble hoppet over uten BB** (ville rammet R12, siden BB ble brukt i R11), F7 horisont over
     chipvinduet ved direkte bruk av `Motor`, F9 minutter med P(spiller) = 0, F11 chiprutenett for egne alternativer
     (`chiprutenett_egne.csv`), F12 frossen minuttabell mistet kjente returdatoer (ny kolonne `retur`).
   - 23. november (`codex/oppdrag-motorkontroll-3.md`, samme tråd 01a1fd50; commit 0dea5a7): Codex skrev steg 5 og kontrollerte
     4ed2cbc. F1, F2, F6, F9, F11 og F12 **RETTET** (F4, F5, F8 og F10 fra før), standardtestene bestått, tallene for gyldige
     planer uendret, og R12-tilfellet (skadesimulering uten BB) dekket. **Sluttdom: «klar etter disse rettingene»** med to
     kanttilfeller: F7 (`Motor` filtrerte bort oppgitte chiprunder utenfor horisonten uten melding) og F3 (en overstyringsrad som
     bare delvis lå i horisonten, ble klippet uten melding). Om `fh_start`: bruk samme lovlige verdi i begge analyser i R12.
   - **Rettet av Claude i d428750:** begge avvises nå i stedet for å filtreres eller klippes; `kjor.py` krever chiprunder i
     horisonten, ikke bare i chipvinduet. Fire nye testtilfeller; gw10- og gw11-oppsettene har alt innenfor horisonten.
   - **Endelig dom 23. november (`codex/oppdrag-motorkontroll-4.md`, samme tråd; commit 6e0cafa): «klar til bruk fra R12».**
     F3 og F7 RETTET; reproduksjonene stopper nå med melding. gw10-, gw11- og et typisk R12-oppsett (horisont 12–19, BB tom,
     FH 13–19, `fh_start` 13) godtas, og tallene for gyldige planer er uendret (standardtestene 64 bestått, 2 hoppet over).
     Alle funn F1–F12 er dermed rettet eller akseptert (F5).
   - Slik ble Codex kjørt 23. november: `--resume-last` fant ikke tråden (pluginens jobbliste tømmes når Claude-økten avsluttes,
     og reservesøket finner bare tråder med kilden «appServer»), så tråden ble fortsatt direkte med ID gjennom pluginens
     `runAppServerTurn`, det samme kallet `task --resume-last --write` bruker. Modellen `gpt-6-astra` (standard i
     `~/.codex/config.toml`) var da ikke tilgjengelig for ChatGPT-kontoen, så kontrollen 23. november (steg 5 og kontrollen av
     4ed2cbc og d428750) ble kjørt med `gpt-6-luna`; steg 1–4 21. november ble kjørt med `gpt-6-astra`. Se punkt 3.
2. **Prøvekjøring ved siden av R11-analysen.** *Gjort 19.–20. november* (motor 0ed2ecb, kjøring 2 med Simens Ødegaard-opplysning: 894 s).
   Codex oppdaterte sine egne gw10-skript til gw11 uten å se motorens tall. Resultat:
   - **Spillerpoeng identiske**: 672 spillere × R11–R19, begge poengsett, største avvik 0,000000.
   - **Lagtall identiske** der plan og chipdatoer er like: A med BB18/FH12 568,33 / 622,21; D3 med BB11/FH13 568,05 / 626,85;
     Muharemović → Van Hecke med BB11/FH13 568,41 / 622,95 (codex / repo_hybrid) i begge.
   - Forskjell bare i søket: motoren rangerte kandidater med `fh_start` 13 (satt av Claude) og fant D3; Codex rangerte med FH16
     og fant C (Dasilva, Mbeumo → Van Hecke, Le Fée). Begge «beste» planer har blanding 597,45 og gevinst bare i repo_hybrid,
     altså innenfor søkets og modellenes usikkerhet.
   - Lærdom til rutinen: `fh_start` påvirker hvilke kandidater søket finner. Se «R11-lærdom» over (beslutningsregel og tre tiltak).
3. **Flettet til `main` 27. november**, etter R12-fristen, på Simens ja («Ja, flett», gitt i hovedchatten). Bare
   `samarbeid/motor/`, `samarbeid/modell/`, `samarbeid/RUTINE.md` og fire linjer i `.gitignore` (`data/cache/`, de store
   `samarbeid/modell/**/*.csv.gz` og `motorkontroll-data/*/`). Ny `RUTINE.md`: motoren fra R13; steg 3 «Claude skriver
   `oppsett.json` og `minutter_overstyring.csv`, Codex kjører motoren og kontrollerer»; steg 4 kritikk mot motorens tall og ny
   kjøring når rutenettets beste FH-runde er en annen enn `fh_start`; steg 5 beslutningsregelen og frysing av
   `motor/spillerpoeng.csv` i `prognose/SHA256SUMS` (`kalibrering/oppdater.py --spillerfil motor/spillerpoeng.csv`; ingen
   kodeendring). **Reserveløsning** under «Faste rammer»: kan motoren ikke kjøres, eller stopper den med en feil som ikke kan
   rettes raskt, regner Codex med sine egne skript fra forrige uke (siste: `gw12/codex/`), og det noteres i `oppgaver.md`;
   motoren rettes ikke midt i en runde.
   **Codex-modellen:** 27. november virker `gpt-6-astra` (standard i `~/.codex/config.toml`) igjen, og Simen vil ikke at
   `gpt-6-luna` brukes. Rutinens steg 0: Codex bruker modellen i `config.toml`, uten `--model`. Feiler første kall fordi
   modellen ikke støttes, byttes ikke modell på egen hånd; det sies fra til Simen øverst i svaret og noteres i `oppgaver.md`.
   `config.toml` er ikke endret. Steg 4 sier hva som gjøres når `--resume-last` ikke finner tråden etter en omstart.
   **Merk:** `ukemotor-fletting` inneholder også `modellforbedring` (endringer i `src/`, bak flagg som står av), som ikke skal til
   `main`. Motoren selv bruker ikke `src/`; bare `historikk.py` (`src/eval_engine.py`) og P1/P2-skriptene i `modell/codex/` gjør det,
   så de virker ikke fra `main` før `modellforbedring` eventuelt flettes.
4. **Free Hit i inneværende runde haster mer enn resten av chipene.** Free Hit 1 kan brukes til og med R19, og planleggingsdatoen er
   R15. Verken gw10-, gw11-skriptene eller motoren regner FH i den runden beslutningen gjelder, så motoren må kunne det **før
   analysen for den runden FH faktisk vurderes nå** (senest R15, torsdag 10. desember). Wildcard og Triple Captain trengs
   **før R20** (nytt chipsett). Hver med egen syntetisk test. `ny_tropp(fh=False)` er wildcard-grenen fra gw09/gw10; den er
   flyttet, men ikke brukt eller testet.
5. Når den første dobbeltrunden er annonsert: minutter per kamp i overstyringsfilen (i dag like for begge kampene).

### Nøyaktig neste steg for en ny økt

```bash
cd <repo>   # main (motoren ble flettet 27. november)
export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH PYTHONDONTWRITEBYTECODE=1
# gw10-fasiten trenger rådata som ikke ligger i git:
cp -R /Users/simenflogstad/Documents/GitHub/Fantasy-FPL/samarbeid/gw10/data/element_summary samarbeid/gw10/data/
(cd samarbeid/motor && python -m pytest tester -q -p no:cacheprovider)     # skal gi 64 bestått, 2 hoppet over (siden d428750)
```

Motoren er godkjent (punkt 1) og flettet (punkt 3). Neste modellarbeid er punkt 4: Free Hit i inneværende runde, før R15.
Oppsettet for en ny uke er forrige ukes `motor/oppsett.json`, første gang `samarbeid/gw11/motor/oppsett.json` (kopier og endre
runde, gratisbytter, bank, chips og `fh_start`; BB ble brukt i R11, så `"BB": []` ut R19; chiprundene må ligge i horisonten),
og overstyringene skrives i `gwNN/claude/minutter_overstyring.csv`.

## Repo-modellen: P1/P2 (parkert, uendret siden 22. oktober)

| Commit | Hva | Skrevet av | Kontrollert av |
|---|---|---|---|
| e1e1fb3 | Optimizer: salgspris, faktiske FT, chipregel 2024/25, horisont | Claude | Codex (godkjent) |
| a82600a | Optimizer: chipvinduer per halvdel | Claude | **Ikke kontrollert ennå** |
| 9b87834 | P0: felles målemotor, paritetstest, keepermål 10 | Codex | Claude |
| 7502dcd | P2: innhoppsfeil i minutes, bak flagg (av) | Claude | Codex: **UAVKLART** (−0,20 % MSE, 5,7 SE; krav 0,5 %) |
| 87a16db | P1: fast bonus-tau, bak flagg (av) | Claude | Codex: **UAVKLART** (tau 7 låst; bonus-MSE −3,5 %, total −0,21 %, 2,6 SE) |

Se `codex/p1p2-maling.md`. Flaggene står av. Kravene endres ikke i ettertid. Ingen ny runde på P1/P2 er planlagt
(se `plan-v2.md` del D); Codex' kontroll av a82600a står fortsatt åpen og bør tas før `modellforbedring` flettes til `main`.
