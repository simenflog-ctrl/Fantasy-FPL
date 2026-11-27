<task>
Fortsett i samme tråd. Din dom 23. november var «klar etter disse rettingene» med to gjenværende funn, F7 og F3. Claude har
rettet begge i commit d428750 på grenen `ukemotor-fletting`:

- **F7:** `Motor` stopper nå med `AssertionError` når en oppgitt BB- eller FH-runde ligger utenfor horisonten, i stedet for å
  filtrere den bort. `kjor.kontroller_oppsett` krever chiprunder i horisonten (`runde`..`horisont_til`), ikke bare i chipvinduet.
- **F3:** `bruk_overstyringer` krever at hele raden ligger i horisonten (`gw_fra` ≥ første runde og `gw_til` ≤ siste runde).
  Valgt regel: delvis overlapp **avvises**, som rader helt utenfor; ingen klipping. README sier at `gw_til` settes til
  horisontens siste runde for et lengre fravær.

Kontroller rettingen kort, og gi endelig dom. Skriv `samarbeid/modell/codex/motorkontroll.md` på nytt etter hvert punkt.
</task>

<steps>
1. Les `git show d428750` (kode, README og de nye testtilfellene i `samarbeid/motor/tester/test_oppsett.py`). Kjør dine
   reproduksjoner av F7 og F3 på nytt mot dagens kode; oppdater kontrollskriptene der de forventet at rundene eller radene
   ble godtatt. Kjør standardtestene (`cd samarbeid/motor && python -m pytest tester -q -p no:cacheprovider`). Claudes
   langsomkjøring står i `samarbeid/modell/claude/pytest-langsom-d428750.log`.
2. Vurder om rettingen kan stoppe et gyldig ukeoppsett: gw10 (`samarbeid/motor/tester/gw10_oppsett.json` og
   `gw10_overstyring.csv`), gw11 (`git show main:samarbeid/gw11/motor/oppsett.json` og
   `git show main:samarbeid/gw11/claude/minutter_overstyring.csv`) og et typisk R12-oppsett (runde 12, horisont 12–19,
   BB tom liste fordi BB ble brukt i R11, FH 13–19). Sjekk også at tallene for gyldige planer er uendret.
3. Oppdater F-tabellen for F3 og F7 (`RETTET` / `GJENSTÅR`) og skriv endelig dom på første linje under overskriften:
   «klar til bruk fra R12», «klar etter disse rettingene: …» eller «ikke klar».
</steps>

<action_safety>
Som før: skriv bare i `samarbeid/modell/codex/`. Ikke endre `samarbeid/motor/`, `src/`, `data/`, `samarbeid/gw*/` eller andre
filer, og ikke commit. Skriv aldri i hovedmappen `/Users/simenflogstad/Documents/GitHub/Fantasy-FPL/`. Ingen nettverk.
Anaconda: `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH PYTHONDONTWRITEBYTECODE=1`. Ikke to tunge jobber samtidig.
La kontrollskriptene bruke faste mappenavn under `motorkontroll-data/`, og legg nye logger der som `*-d428750.log`.
</action_safety>

<completeness_contract>
Må du stoppe før punkt 3, skriv i rapporten hvilket punkt du nådde og hva som gjenstår, og oppgi tidspunktet bruksgrensen
nullstilles hvis du får vite det.
</completeness_contract>
