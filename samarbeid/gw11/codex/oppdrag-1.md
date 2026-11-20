<task>
Du er Codex og jobber sammen med Claude om ett virkelig Fantasy Premier League-lag (ID 7089878, sesong 2026/27).
Målet er høyest mulig forventet totalpoengsum resten av sesongen. Neste frist er runde 11, lørdag 2026-11-21 11:00 UTC.
Claude har ansvar for lagnyheter, skader og spilletid. Du har ansvar for beregningene.

Arbeidsmappe: `samarbeid/gw11/` i repoet (grenen `main`). Les `grunnlag.md` først, og `samarbeid/gw10/beslutning.md`,
`gw10/codex/analyse.md` og `gw10/codex/kontroll.md` for forrige ukes beslutning og metode. Frosne API-data for denne uken ligger i
`samarbeid/gw11/data/`.

Ta utgangspunkt i `samarbeid/gw10/codex/modell.py` og `modell_r2.py` (dine egne skript fra forrige uke, med eksakte autobytter,
felles chipdatoer og paret skadesimulering). Kopier dem til `gw11/codex/` og oppdater til ukens data (R11–R19). Gjør ingen andre
modellendringer enn det som trengs for ny uke; si fra hvis du mener noe bør endres, men endre det ikke i denne runden.
Behold begge poengsettene, `codex` og `repo_hybrid`, med vekt 0,5 i blandingen.
Repoets xP: frys `data/derived/expected_points.csv` og `player_matches.csv` (boten 19. nov, R11–R16) til `gw11/codex/input/`.
SHA-256: expected_points.csv 5e94dc6f…6ead19, player_matches.csv c953d4a1…4842.

Tropp (uendret siden R9), bank £0,4m og salgspriser er verifisert i `grunnlag.md`. Gratisbytter: antatt 3 (mulig 2–4; regelen ved
wildcard er ikke verifisert). Ingen klubb har tre spillere. Ingen blanke eller doble runder i horisonten.

Ikke les `samarbeid/gw11/motor/`: det er en uavhengig prøvekjøring av en annen beregning, som skal sammenlignes med dine tall etterpå.
Kvoten din har sluppet opp midt i arbeidet de siste ukene: skriv `analyse.md` tidlig og oppdater den, slik at noe brukbart finnes hvis du stopper.
</task>

<minutes>
Spilletid som i gw10 (vektede starter R1–R10, egne minutter per start, prior, API-flagg), med disse og bare disse overstyringene fra
Claude, i `samarbeid/gw11/claude/minutter_overstyring.csv`:
- BHA, BOU, SUN, CRY: startandel og minutter × 0,95 i R12 (europakamp torsdag 26. nov, liga søndag 29. nov).
- Thiago (id 106, utestengt til 5. des): tilgjengelig fra R14 med p_start 0,9 og 74 forventede minutter.
- Ødegaard (id 15): p_start 0,95 og 82 forventede minutter i R11–R12 (frisk og i god form etter landslagspausen ifølge Simen;
  87–90 minutter i hver av de fire siste ligarundene).
Ingen faktor i R11 (ingen europakamper etter landslagspausen). Skriv tabellen du faktisk bruker til `codex/minutter_antatt.csv`.
Er du uenig i en overstyring, si det i analysen, men bruk den.
</minutes>

<known_news>
Verifisert fra API-et 19. nov 16:30 UTC eller kildebelagte nyheter 19. nov. Fakta, ikke Claudes forslag.
- Alle 15 i egen tropp har status a og ingen nyhet. Bournemouth og Leeds melder ingen skader etter landslagspausen.
- Haaland spilte hele kampen for Norge 14. nov. Ingen nye skader meldt for Gabriel, Ødegaard, Isak, Mbeumo, Groß eller Barry;
  Arsenal, City, Liverpool, United, Brighton og Everton holder pressekonferanser fredag.
- Ute eller usikre blant mulige kjøp (API): Saka 0 %, Thiago utestengt til 5. des, Zubimendi 75 %, Thomas (COV) 75 %.
  Sunderland: Xhaka ute, Brobbey trolig ute. Forest: Hudson-Odoi ute. Palace: Mateta utestengt.
- Kjøpsuniverset: ingen spillere med status u, n, i, s eller 0 %; status d gis redusert startsannsynlighet.
</known_news>

<required_alternatives>
Samme poengmodell, eksakte autobytter, samme byttepolitikk og samme BB- og FH-dato for alle:
A. Spare byttene (rull). Referansen.
B. Beste plan med 1 gratisbytte.
C. Beste plan med 2 gratisbytter.
D. Beste plan med 3 gratisbytter, og beste med ett poengtrekk (−4), bare hvis gevinsten forsvarer det.
E. Bench Boost: beste runde R11–R19 (forrige plan: R12).
F. Free Hit: beste runde R12–R19 (forrige plan: R13), sammen med BB.
G. Kaptein og visekaptein for R11, med forventning for de 3–4 beste.
Rangér med 3 gratisbytter, og vis om anbefalingen endres med 2 eller 4. Paret skadesimulering (100 verdener, 1 % og 2 %) for de
beste planene mot A.
</required_alternatives>

<model_rules>
- Poengregler fra `bootstrap.json` → `game_config.scoring` (keepermål 10).
- Faste kontroller: toppspillernes nivå (Haaland m.fl.) mot observert snitt og repoets xP; en konkret tropp testes under begge poengsett.
- Prognoseevalueringen (`samarbeid/kalibrering/oversikt.md`) har ingen tydelige skjevheter ennå (3 runder); ikke juster modellen etter den.
- Lever `codex/spillerpoeng.csv` med kolonnene id, navn, gw, codex, repo_hybrid for alle spillere og R11–R19. Den fryses med prognosen.
- Oppgi usikkerhet for hovedalternativene. Ingen nettverkstilgang er nødvendig.
</model_rules>

<action_safety>
Skriv bare i `samarbeid/gw11/codex/`. Ikke endre `src/`, `data/`, `config/`, `tests/` eller andre filer, og ikke `gw10/`.
Ikke commit noe i git. Ikke installer pakker; bruk Anaconda: `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH`.
</action_safety>

<deliverables>
1. `codex/modell.py` (og eventuelt `modell_r2.py`): gjenskaper alle tallene fra `data/` og `codex/input/`.
2. `codex/minutter_antatt.csv` og `codex/spillerpoeng.csv`.
3. `codex/alternativer.csv` (én rad per alternativ: inn/ut, poengtrekk, bank, forventet R11, R11–R14, R11–R19, usikkerhet),
   `codex/chiprutenett.csv`, `codex/kapteiner.csv`.
4. `codex/analyse.md` på norsk: anbefalt handling for R11 med ellever, kaptein, visekaptein og benk; budsjettkontroll;
   BB- og FH-tidspunkt; følsomhet for antall gratisbytter; skille mellom verifiserte data, modellresultater og antakelser.
</deliverables>

<completeness_contract>
Ferdig betyr: skriptet kjører uten feil, alternativene A–G er regnet, spillerpoeng dekker alle spillere R11–R19 i begge poengsett,
og `analyse.md` sier tydelig hva du anbefaler for R11 og hvor robust det er. Kjør skriptet selv og bekreft at tallene stemmer.
</completeness_contract>
