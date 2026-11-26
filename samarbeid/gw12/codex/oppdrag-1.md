<task>
Du er Codex og jobber sammen med Claude om ett virkelig Fantasy Premier League-lag (ID 7089878, sesong 2026/27).
Målet er høyest mulig forventet totalpoengsum resten av sesongen. Neste frist er runde 12, fredag 2026-11-27 18:30 UTC.
R13 er en midtukerunde med frist tirsdag 1. des 18:30 UTC. Claude har ansvar for lagnyheter, skader og spilletid. Du har ansvar for beregningene.

Arbeidsmappe: `samarbeid/gw12/` i repoet (grenen `main`). Les først `grunnlag.md`, deretter `samarbeid/gw11/beslutning.md`,
`gw11/codex/analyse.md` og `gw11/codex/kontroll.md` for forrige ukes beslutning og metode. Frosne API-data for denne uken ligger i
`samarbeid/gw12/data/`.

Ta utgangspunkt i `samarbeid/gw11/codex/modell.py`, `modell_r2.py` og `bb_kontroll.py` (dine egne skript fra forrige uke, med eksakte
autobytter, felles chipdatoer og paret skadesimulering). Kopier dem til `gw12/codex/` og oppdater dem til ukens data (R12–R19).
Bench Boost og Wildcard 1 er brukt. Eneste chip igjen før R20 er Free Hit 1, som må brukes senest i R19.
Gjør ingen andre modellendringer enn det som trengs for ny uke. Si fra hvis du mener noe bør endres, men endre det ikke denne runden.
Behold begge poengsettene, `codex` og `repo_hybrid`, med vekt 0,5 i blandingen.
Repoets xP: frys `data/derived/expected_points.csv` og `player_matches.csv` (botens oppdatering 23. nov, R11–R16) til `gw12/codex/input/`.
SHA-256: expected_points.csv 56c75829…481f22, player_matches.csv b42c7b9e…1a06c9.

Troppen etter R11, bank £0,4m og salgspriser er verifisert i `grunnlag.md` (`data/salgspriser.json`). Gratisbytter: antatt 3,
mulig 2–4 (wildcardregelen er ikke verifisert). Ingen klubb har tre spillere. Ingen blanke eller doble runder i horisonten.
Kvoten din har sluppet opp midt i arbeidet de siste ukene. Skriv derfor `analyse.md` tidlig og oppdater den underveis,
slik at noe brukbart finnes hvis du stopper.
</task>

<minutes>
Spilletiden modelleres som i gw11. Bruk disse og bare disse overstyringene fra Claude, som står i
`samarbeid/gw12/claude/minutter_overstyring.csv`:
- BHA, BOU, SUN og CRY: startandel og minutter × 0,95 i R12 (europakamp torsdag 26. nov, ligakamp søndag 29. nov).
- Thiago (id 106, utestengt til 5. des): tilgjengelig fra R14 med p_start 0,9 og 74 forventede minutter.
- Mbeumo (id 427): p_start 0,8 og 68 minutter i R12. Han startet i R11, men spilte bare 21 minutter uten forklaring.
- Dasilva (id 176, COV): p_start 0,4 og 34 minutter i R12, og 0,6 og 52 minutter i R13–R14. Han var utenfor laget i R11 (0 minutter),
  og en forhåndsomtale melder ham skadet. API-statusen er likevel `a`.
Skriv tabellen du faktisk bruker til `codex/minutter_antatt.csv`. Er du uenig i en overstyring, si det i analysen, men bruk den.
</minutes>

<known_news>
Verifisert fra API-et 26. nov kl. 07:44 UTC. Dette er fakta, ikke Claudes forslag.
- Alle 15 i egen tropp har status `a` og ingen nyhet. Mbeumo spilte 21 minutter i R11 og Dasilva 0.
- Ute eller usikre blant mulige kjøp: Raya 50 %, Boscagli 75 %, Hall 75 %, João Pedro ute, Gakpo ute til 2. des,
  Yeremy utestengt til 2. des, Tarkowski utestengt til 13. des, Thiago utestengt til 5. des.
- Kjøpsuniverset skal ikke ha spillere med status `u`, `n`, `i` eller `s`, eller 0 %. Status `d` gir redusert startsannsynlighet.
- Ingen pressekonferanser for R12 var holdt da dette ble skrevet.
</known_news>

<required_alternatives>
Bruk samme poengmodell, eksakte autobytter, samme byttepolitikk og samme FH-dato for alle alternativene:
A. Spare byttene (rull). Dette er referansen.
B. Beste plan med 1 gratisbytte.
C. Beste plan med 2 gratisbytter.
D. Beste plan med 3 gratisbytter. Ta også med beste plan med ett poengtrekk (−4), men bare hvis gevinsten forsvarer det.
E. Free Hit: beste runde R12–R19 (foreløpig plan: R15).
F. Kaptein og visekaptein for R12, med forventning for de 3–4 beste. Merk at ARS–MCI gir Haaland mot Gabriel og Ødegaard.
G. Ødegaard-salg: test eksplisitt beste plan som selger Ødegaard. Regelen er at han selges bare hvis gevinsten over R12–R19 er over
   ca. 3 poeng i begge poengsett.
Rangér med 3 gratisbytter, og vis om anbefalingen endres med 2 eller 4. Kjør paret skadesimulering (100 verdener, 1 % og 2 %) for de
beste planene mot A.
</required_alternatives>

<model_rules>
- Poengregler fra `bootstrap.json` → `game_config.scoring` (keepermål gir 10).
- Faste kontroller: sjekk toppspillernes nivå (Haaland m.fl.) mot observert snitt og repoets xP, og test hver konkret tropp under begge poengsettene.
- Prognoseevalueringen (`samarbeid/kalibrering/oversikt.md`, 4 runder) har for første gang grupper som oppfyller kriteriet for tydelig skjevhet:
  codex undervurderer GKP < 5,0, MID 5,0–7,4 og FWD 5,0–7,4, og repo_hybrid overvurderer MID 7,5–9,9 og FWD ≥ 10,0 (bare Haaland, n = 4).
  Ikke juster modellen etter dette. Vis heller i en egen tabell hvordan kapteinsrangeringen for R12 ville sett ut med disse
  skjevhetene lagt til, og merk den som følsomhetstest.
- Lever `codex/spillerpoeng.csv` med kolonnene id, navn, gw, codex og repo_hybrid for alle spillere i R12–R19. Den fryses med prognosen.
- Oppgi usikkerheten for hovedalternativene. Du trenger ikke nettverkstilgang.
</model_rules>

<action_safety>
Skriv bare i `samarbeid/gw12/codex/`. Ikke endre `src/`, `data/`, `config/`, `tests/` eller andre filer, og ikke `gw11/`.
Ikke commit noe i git. Ikke installer pakker. Bruk Anaconda: `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH`.
</action_safety>

<deliverables>
1. `codex/modell.py` (og eventuelt `modell_r2.py`), som gjenskaper alle tallene fra `data/` og `codex/input/`.
2. `codex/minutter_antatt.csv` og `codex/spillerpoeng.csv`.
3. `codex/alternativer.csv` med én rad per alternativ: inn/ut, poengtrekk, bank, forventet R12, R12–R15, R12–R19 og usikkerhet.
   Lever også `codex/chiprutenett.csv` (FH-dato) og `codex/kapteiner.csv`.
4. `codex/analyse.md` på norsk med anbefalt handling for R12: ellever, kaptein, visekaptein og benk. Ta med budsjettkontroll,
   FH-tidspunkt og følsomhet for antall gratisbytter, og skill mellom verifiserte data, modellresultater og antakelser.
</deliverables>

<completeness_contract>
Ferdig betyr at skriptet kjører uten feil og at alternativene A–G er regnet. Spillerpoengene skal dekke alle spillere i R12–R19 i begge
poengsett. `analyse.md` skal si tydelig hva du anbefaler for R12 og hvor robust anbefalingen er. Kjør skriptet selv og bekreft at tallene stemmer.
</completeness_contract>
