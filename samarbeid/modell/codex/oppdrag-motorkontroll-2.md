<task>
Du er Codex. Fullfør den uavhengige kontrollen av ukemotoren (`samarbeid/motor/`) som du startet 19. november. Den stoppet på
bruksgrensen etter ca. 8 minutter. Les først din egen `samarbeid/modell/codex/motorkontroll.md` og fortsett der den slapp.
Grunnoppdraget står uendret i `samarbeid/modell/codex/oppdrag-motorkontroll.md`; les det. Dette dokumentet sier hva som er
endret siden, og i hvilken rekkefølge du skal jobbe nå.
</task>

<what_changed>
- Arbeidskopien er denne mappen, grenen `ukemotor-fletting`, laget fra `claude/happy-sutherland-2bb9aa` (tipp c0f7ebe).
  Motoren er ikke endret etter e5cde2e. Filene dine fra 19. november (`motorkontroll.md`, `motorkontroll_eksempler.py`,
  `motorkontroll_kanttilfeller.py`, `motorkontroll-data/`) er kopiert hit uendret.
- **e5cde2e har rettet de fem funnene i `motorkontroll.md`** (`git show e5cde2e`; 14 nye tester i `samarbeid/motor/tester/test_oppsett.py`):
  `kjor.kontroller_oppsett` stopper på WC/TC i `chips`, FH i inneværende runde, felles BB/FH utenfor `chips` eller i samme runde,
  `horisont_til` forbi chipvinduet, `gratisbytter` utenfor 0–5 og en oppgitt overstyringsfil som mangler. `Motor.alternativ()` og
  `faste_planer()` avviser BB i FH-runden og chiprunder som ikke er tilgjengelige. G-radenes `modellspredning` regnes etter
  kapteinsendringen. `--frys` kopierer fra repoet ukemappen ligger i. README sier at prognoseskriptet fryser spillerpoengene.
- Loggene dine (`motorkontroll-data/eksempler.log` og `kanttilfeller.log`) har flere funn enn rapporten: F1–F11. Noen er dekket av
  e5cde2e, andre trolig ikke (for eksempel F2 for `ft_folsomhet`/`vekt_codex`, F3 omvendt intervall, F6, F9, F10, F11). Det er din
  jobb å avgjøre hvilke.
- Tester: Claude har kjørt `cd samarbeid/motor && python -m pytest tester -q -p no:cacheprovider` på denne grenen: 37 bestått,
  2 hoppet over (79 s). `--langsom` er kjørt av Claude; resultatet står i `samarbeid/modell/claude/pytest-langsom-c0f7ebe.log`.
  gw10-rådataene (`samarbeid/gw10/data/element_summary/`) er kopiert inn. Du trenger ikke kjøre `--langsom` på nytt.
- Prøvekjøring ved R11 (19.–20. november): motoren og dine egne gw11-skript ga identiske spillerpoeng (672 spillere × R11–R19,
  begge poengsett, største avvik 0,000000) og identiske lagtall for samme plan og chipdatoer. Forskjellen var bare i søket: motoren
  rangerte byttekandidater med `fh_start` 13 og fant D3, ditt skript rangerte med FH16 og fant C. Se `samarbeid/modell/STATUS.md`
  punkt 2. R11-filene ligger på `main` i hovedmappen `/Users/simenflogstad/Documents/GitHub/Fantasy-FPL/samarbeid/gw11/`
  (bare til lesing).
</what_changed>

<steps>
Kvoten din er liten. Jobb i korte steg, og skriv `motorkontroll.md` på nytt etter **hvert** steg, slik at rapporten alltid er
brukbar hvis du stopper. Begynn hvert steg med å skrive én linje i rapporten om hva du gjør nå.

1. Les `motorkontroll.md`, de to loggene, `git show --stat e5cde2e` og `test_oppsett.py`. Før resultatene fra loggene inn i
   rapporten, merket «kjørt 19. november, før e5cde2e». Kjør ingenting i dette steget.
2. Kjør de to skriptene dine på nytt mot dagens kode. Tilpass dem slik at et rettet funn logges som `RETTET` i stedet for å krasje,
   og et gjenstående som `GJENSTÅR`. Før en tabell for F1–F11 i rapporten: `RETTET` / `GJENSTÅR` / `AKSEPTERT`, med alvorlighet og
   kort begrunnelse.
3. Punkt 2 i grunnoppdraget (ekvivalens): `poeng.py`, `motor.py` og `skadesim.py` mot `samarbeid/gw10/codex/modell.py` og
   `modell_r2.py`. `lag.py` er allerede AST-identisk ifølge loggen din. Bare avvik som gw10-fasiten ikke dekker, trenger eksempel.
4. Punkt 3–4, det som gjenstår: tom `chips`-liste, chipvinduet fra R20, og at WC, TC og FH i inneværende runde stopper med en
   melding både i `kjor.py` og i `Motor`.
5. Punkt 5: samlet dom og prioritert liste. Ta også stilling til om søkets avhengighet av `fh_start` må rettes i motoren før R12,
   eller kan håndteres i rutinen (samme `fh_start` i begge analyser, eller søk over flere FH-datoer).
</steps>

<action_safety>
Skriv bare i `samarbeid/modell/codex/` (rapporten, skriptene dine og `motorkontroll-data/`). Ikke endre `samarbeid/motor/`, `src/`,
`data/`, `samarbeid/gw*/` eller andre filer, og ikke commit. Skriv aldri i hovedmappen
`/Users/simenflogstad/Documents/GitHub/Fantasy-FPL/`; den er bare til lesing. Ingen nettverkstilgang trengs.
Anaconda: `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH PYTHONDONTWRITEBYTECODE=1`.
Kjør ikke to tunge jobber samtidig: heltallsløseren har tidsgrense, og CPU-konkurranse kan endre søkets svar.
Store kopier av ukedata under `motorkontroll-data/` (element_summary, frosne `player_matches.csv`, pytest-tmp) blir ikke committet;
skriptene dine skal kunne lage dem på nytt. La nye kjøringer bruke faste mappenavn (uten tidsstempel), så mappen ikke vokser.
</action_safety>

<deliverables>
`samarbeid/modell/codex/motorkontroll.md` på norsk, som i grunnoppdraget: dom per punkt 1–5 (OK / feil / usikker) med fil og linje,
alvorlighet (påvirker beslutninger / kosmetisk), et minimalt eksempel for hver feil, tabellen for F1–F11, og til slutt en prioritert
liste over det som må rettes før motoren brukes i ukeanalysen for R12 (torsdag 26. november).
Første linje under overskriften er den samlede dommen: «klar til bruk fra R12», «klar etter disse rettingene: …» eller «ikke klar».
Ikke rett feilene selv; Claude retter, og du kontrollerer etterpå.
</deliverables>

<completeness_contract>
Må du stoppe før steg 5, skriv i rapporten hvilket steg du nådde og hva som gjenstår, slik at en ny tråd kan fortsette uten å
gjenta arbeid. Oppgi tidspunktet bruksgrensen nullstilles, hvis du får vite det.
</completeness_contract>
