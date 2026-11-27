<task>
Du er Codex. Kontroller ukemotoren i `samarbeid/motor/` uavhengig, før den kan erstatte de ukentlige engangsskriptene
(`samarbeid/gwNN/codex/modell*.py`) i FPL-rutinen. Claude (Fable) skrev motoren 16. november ved å flytte logikken fra
`samarbeid/gw10/codex/modell.py` og `modell_r2.py`, som du selv skrev. Du er den som ikke skrev endringen, og skal lete etter feil.
Arbeidskopien er grenen `claude/happy-sutherland-2bb9aa` (denne mappen). `main` er ikke involvert.
</task>

<read_first>
`samarbeid/modell/plan-v2.md` (arkitektur, akseptansetester, hva som bevisst ikke gjøres), `samarbeid/motor/README.md`,
`samarbeid/modell/STATUS.md`. Deretter `samarbeid/motor/*.py` og testene i `samarbeid/motor/tester/`.
Sammenlign med `samarbeid/gw10/codex/modell.py` og `modell_r2.py`.
</read_first>

<required_checks>
1. Kjør testene: `cd samarbeid/motor && python -m pytest tester -q -p no:cacheprovider` (23 skal bestå, 2 hoppes over)
   og med `--langsom` (25 skal bestå). Rapporter tid og resultat.
2. Ekvivalens: er logikken i `poeng.py`, `lag.py`, `motor.py`, `skadesim.py` den samme som i gw10-skriptene der gw10-fasiten dekker den?
   Påpek alle avvik, også de som ikke slår ut i gw10-tallene.
3. Det som er nytt og ikke dekket av gw10-fasiten. Let særlig her, og lag en liten test eller et minimalt eksempel som viser hver feil du finner:
   a. Dobbeltrunde og blank runde i `poeng.prognose` (to kamper, null kamper), også for `repo_hybrid` og i autobytter og Bench Boost.
   b. Overstyringsfilen (`claude/minutter_overstyring.csv`): rekkefølge, `faktor` mot `p_start`/`forventede_min`, lag-rader,
      spillere som er ute (u/n/i/s/0 %) og en rad som gjør dem tilgjengelige, feil i filen (manglende `kilde`, ukjent id).
   c. `chips` med tom liste, Free Hit i inneværende runde (skal være ulovlig), BB og FH i samme runde, chipvinduet til R19 og fra R20.
   d. `kjor.py`: `--frys`, `--bare-poeng`, full kjøring, standardverdier (bank fra `entry.json`, horisont, `fh_start`),
      Claudes egne `alternativer`, `ft_folsomhet`, og at den bare skriver i `gwNN/motor/`.
   e. Regler: salgspris, budsjett, maks tre per klubb, 2/5/5/3, gratisbytter (maks 5, +1 per runde, antakelsen ved WC/FH),
      kjøpsuniverset (ingen u/n/i/s/0 %), poengtrekk.
4. Det som bevisst mangler (Wildcard, Triple Captain, Free Hit i inneværende runde): bekreft at motoren ikke gir feil svar stille
   hvis noen ber om dem, men stopper eller sier fra.
5. Samlet dom: kan motoren brukes som regnemaskin i ukeanalysen fra runde 12, med Codex som kontrollør? List det som må rettes først.
</required_checks>

<action_safety>
Skriv bare nye filer i `samarbeid/modell/codex/` (rapporten og eventuelle testskript du lager). Ikke endre `samarbeid/motor/`,
`src/`, `data/` eller andre filer, og ikke commit. Ingen nettverkstilgang trengs. Anaconda:
`export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH PYTHONDONTWRITEBYTECODE=1`.
Kvoten din har sluppet opp midt i arbeidet flere ganger: skriv `samarbeid/modell/codex/motorkontroll.md` tidlig og utvid den,
slik at noe brukbart finnes hvis du stopper.
</action_safety>

<deliverables>
`samarbeid/modell/codex/motorkontroll.md` på norsk: for hvert punkt 1–5 en dom (OK / feil / usikker), med fil og linje,
alvorlighet (påvirker beslutninger / kosmetisk) og et minimalt eksempel for hver feil. Til slutt en prioritert liste over det som
må rettes før motoren brukes i en ukeanalyse. Ikke rett feilene selv; Claude retter, og du kontrollerer etterpå.
</deliverables>
