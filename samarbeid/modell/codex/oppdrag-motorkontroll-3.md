<task>
Fortsett i samme tråd. Du stoppet på bruksgrensen i steg 5, etter at du hadde gitt dommen «klar etter disse rettingene» i din siste
melding. Claude har siden rettet funnene som gjensto, i commit 4ed2cbc på grenen `ukemotor-fletting`. Tre punkter gjenstår, i denne
rekkefølgen. Skriv `samarbeid/modell/codex/motorkontroll.md` på nytt etter hvert punkt, slik at rapporten er brukbar hvis du stopper.
</task>

<steps>
1. **Steg 5 i rapporten, før du kontrollerer noe nytt.** Skriv den samlede dommen fra din siste melding på første linje under
   overskriften (i stedet for «ikke klar») og den prioriterte listen over det som måtte rettes før R12. Oppdater arbeidsstatusen øverst.
2. **Kontroller Claudes rettinger** (`git show 4ed2cbc`; nye tester nederst i `samarbeid/motor/tester/test_oppsett.py`):
   - F1, F2, F7: `kjor.kontroller_oppsett` og `Motor` avviser `fh_start` uten tilgjengelig FH, gratisbytter/`ft_folsomhet` som ikke er
     heltall 0–5, vekt utenfor [0, 1], chiprunder utenfor vinduet og horisont forbi chipvinduet. `bane()` avviser FH som ikke er tilgjengelig.
   - F3: hver overstyringsrad kontrolleres før bruk (hele runder, `gw_fra` ≤ `gw_til`, innenfor horisonten, tall ≥ 0).
   - F6: skadesimuleringen kjøres også uten Bench Boost (totalene uten BB, siste rad i `simuler_raa`); `kontroll.json` sier alltid
     om den ble kjørt. Dette gjelder R12 direkte: BB ble brukt i R11.
   - F9: `poeng.prognose` stopper når en spiller som regnes, får minutter med P(spiller) = 0.
   - F11: `chiprutenett_egne.csv` med alle lovlige chipdatoer for hvert av Claudes egne alternativer (`Motor.rutenett_for`).
   - F12: `minutter.csv` har kolonnen `retur`, og `les_minuttabell` leser den, så en frossen tabell gir de samme poengene.
   Kjør dine fire kontrollskript på nytt mot dagens kode, og standardtestene (`cd samarbeid/motor && python -m pytest tester -q
   -p no:cacheprovider`). Claude har kjørt `--langsom`; resultatet står i `samarbeid/modell/claude/pytest-langsom-4ed2cbc.log`.
   Oppdater F-tabellen (`RETTET` / `GJENSTÅR`), og vurder om rettingene har innført nye feil eller endret tall for gyldige planer.
3. **Endelig dom** på første linje: «klar til bruk fra R12», «klar etter disse rettingene: …» eller «ikke klar».
</steps>

<action_safety>
Som før: skriv bare i `samarbeid/modell/codex/`. Ikke endre `samarbeid/motor/`, `src/`, `data/`, `samarbeid/gw*/` eller andre filer,
og ikke commit. Skriv aldri i hovedmappen `/Users/simenflogstad/Documents/GitHub/Fantasy-FPL/`. Ingen nettverk.
Anaconda: `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH PYTHONDONTWRITEBYTECODE=1`. Ikke to tunge jobber samtidig.
La kontrollskriptene bruke faste mappenavn under `motorkontroll-data/`.
</action_safety>

<completeness_contract>
Må du stoppe før punkt 3, skriv i rapporten hvilket punkt du nådde og hva som gjenstår, og oppgi tidspunktet bruksgrensen nullstilles
hvis du får vite det.
</completeness_contract>
