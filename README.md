# fpl-model

Datamotor og modellsystem for Simens Fantasy Premier League-lag (`7089878`).

Full spesifikasjon ligger i Claude-prosjektet «Fantasy Premier League», i
`claude/modell-arkitektur.md`. Dette repoet er arm 1 av to.

## Hvorfor dette repoet finnes

Claude kjører i et skymiljø som er **blokkert fra `fantasy.premierleague.com`
på organisasjonsnivå** — `CONNECT tunnel failed, response 403`. Det lar seg
ikke omgå. Samtidig krever lagstyrkemodellen xG per lag per kamp, og FPL
publiserer ikke det noe sted: det må aggregeres opp fra `element-summary` for
hver av ~700 spillere.

GitHub Actions-runnere har åpen internettilgang. De henter dataene og
committer resultatet hit. Claude leser det ferdige resultatet via
`raw.githubusercontent.com`, som er tilgjengelig fra skyen.

Derfor er arbeidsdelingen:

| Arm | Hvor | Gjør |
|---|---|---|
| 1 | Dette repoet, GitHub Actions | Henter data, kjører modellen, committer tall |
| 2 | Claude, planlagt oppgave | Pressekonferanser og lagnytt, skjønn, anbefaling |

Modellen er deterministisk og versjonert. Den avhenger ikke av at en
språkmodell oppfører seg likt hver uke.

## Status: fase 1

Workflowen henter **bare data**. Ingen modell, ingen anbefalinger. Modellsteget
legges til når tallene er verifisert mot virkeligheten — vi vil ikke bake inn
feil vi ennå ikke har oppdaget.

```
src/fetch.py           henter bootstrap, fixtures, live, entry, element-summary
src/build_matches.py   bygger spiller- og lagtabeller (inkl. xG for/imot)
config/scoring.yaml    poengreglene, lest av modellen — aldri hardkodet
tests/                 tester logikken som stille kan ødelegge modellen
```

### Output som committes

```
data/derived/team_matches.csv     én rad per lag per kamp — input til M1
data/derived/player_matches.csv   én rad per spiller per kamp — input til M2/M3
data/raw/bootstrap.json           spillere, lag, runder, poengkategorier
data/raw/fixtures.json            hele kampoppsettet med FDR
data/raw/live_gw*.json            faktiske utfall, brukes til kalibrering (M9)
data/meta.json                    når det ble hentet, hvilken runde, deadline
```

De rå `element-summary`-filene committes ikke — 700 filer og ~7 MB per
snapshot, og de er fullt reproduserbare fra API-et.

## Oppsett (én gang, ca. fem minutter)

1. Opprett et **offentlig** repo på GitHub, f.eks. `fpl-model`. Ikke legg til
   README eller .gitignore — repoet skal være tomt.

   Offentlig er med vilje: da leser Claude resultatene uten at du må dele noen
   nøkkel eller token. Det ligger ingenting sensitivt her — FPL-dataene og
   lag-ID-en din er offentlige uansett.

2. Pakk ut denne mappa lokalt og push den:

   ```bash
   cd fpl-model
   git init -b main
   git add .
   git commit -m "fase 1: datamotor"
   git remote add origin https://github.com/<brukernavn>/fpl-model.git
   git push -u origin main
   ```

3. Gå til **Settings → Actions → General** i repoet, og sett
   *Workflow permissions* til **Read and write permissions**. Uten det får ikke
   workflowen lov til å committe dataene den henter.

4. Gå til **Actions**, velg «Hent FPL-data», og trykk **Run workflow** for å
   kjøre den første gangen manuelt. Den tar under et minutt.

5. Send Claude URL-en til repoet.

Deretter kjører den av seg selv mandag, torsdag og lørdag kl. 06:00 UTC — en
time før de planlagte Claude-oppgavene, slik at dataene alltid er ferske.

## Kjøre lokalt

```bash
pip install -r requirements.txt
python src/fetch.py
python src/build_matches.py
python -m pytest tests/ -q
```

## Neste faser

| Fase | Innhold |
|---|---|
| 2 | M1 lagstyrke (Dixon-Coles på xG, med krymping) + M2 minuttmodell |
| 3 | M3–M6: angrepspoeng, forsvarspoeng, defensive contribution, bonus |
| 4 | M8 optimizer (heltallsprogrammering over 6–8 runders horisont) |
| 5 | M9 kalibrering og backtest mot historiske sesonger |

Fase 2 er der mesteparten av gevinsten ligger: den fjerner FDR og
rotasjonsrisiko, som er de to største feilkildene i vanlig FPL-analyse.

## En ting systemet ikke gjør

Det gjennomfører ikke transfers. Det krever innlogging på FPL-kontoen, og
Claude håndterer ikke passord eller logger inn som deg. Systemet leverer en
ferdig beslutning — inn, ut, kaptein, oppstilling, chip — som du klikker inn i
appen selv. Det tar under to minutter.
