# Ukentlig rutine: Claude + Codex styrer FPL-laget

Simen starter med én setning, for eksempel **«Start FPL-analyse for runde 9»**. Claude gjør resten, uten å stille
spørsmål underveis, og leverer ett samlet svar på norsk. Simen gjør bare byttene i FPL-appen selv.

Første gjennomføring: `gw08/` (22. okt 2026). Bruk den som mal. Les `gw08/beslutning.md` og forrige ukes `beslutning.md` først.

## Faste rammer

- Mål: høyest forventet totalpoengsum resten av sesongen. Lag 7089878, «lifegivesyoulammens».
- **Aldri** gjør bytter, aktiver chips eller endre laget på FPL-kontoen. Ingen passord, innloggingskapsler eller betalt API-bruk.
- Claude er hovedagent og tar sluttbeslutningen. Codex gjør reelle beregninger via pluginen; svarene simuleres aldri.
- Skill alltid mellom verifiserte data, opplysninger fra Simen, modellresultater og antakelser.
- Hver uke er en ny mappe `samarbeid/gwNN/` med samme struktur som `gw08/`.
- Filansvar: Claude skriver i `claude/`, `grunnlag.md`, `oppgaver.md`, `beslutning.md`, `prognose/` og `samarbeid/kalibrering/`.
  Codex skriver bare i `codex/`.
  Ingen endrer `src/`, `config/`, `tests/` eller `data/` i repoets rot. `gwNN/data/` fryses etter henting.

## Steg 0: Klargjøring

1. Node for Codex: `export PATH="$HOME/.nvm/versions/node/v24.22.1/bin:$PATH"` i hver Bash-kommando som kaller Codex
   (`~/.zprofile` har den også, men appens skall leser den ikke alltid).
2. Sjekk Codex: `node ~/.claude/plugins/cache/openai-codex/codex/<versjon>/scripts/codex-companion.mjs setup --json`.
3. Hent GitHub-botens dataoppdateringer: `git fetch origin && git merge origin/main`.
   - Konflikter i `data/` → ta botens versjon (`git checkout --theirs`), den er nyest.
   - Konflikter i `src/` → undersøk begge sider med `git log` før du velger (se mergen 22. okt: opplastingen hadde eldre kode).
4. Kontroller at `main` er ren før du starter.

## Steg 1–2 gjøres av agenten `fpl-datagrunnlag`

For å holde økten kort delegerer Claude steg 1 og 2 til agenten i `.claude/agents/fpl-datagrunnlag.md`. Gi den runde N,
ukens og forrige ukes mappe, og alt Simen har sagt om bytter eller lagstatus. Agenten følger stegene under og svarer med et kort sammendrag.
Før steg 3 leser Claude **hele** `grunnlag.md` og `claude/evaluering-forrige.md` selv (rådataene trenger ikke leses).
Melder agenten avvik eller feil, undersøker Claude dem før arbeidet går videre. Faller agenten ut, gjør Claude stegene selv.

## Steg 1: Datagrunnlag (Claude)

Hent fra `https://fantasy.premierleague.com/api/` til `gwNN/data/`: `bootstrap-static/`, `fixtures/`, `entry/7089878/`,
`entry/7089878/history/`, `entry/7089878/transfers/`, `entry/7089878/event/<forrige>/picks/`, og `element-summary/<id>/`
for alle med ≥ 300 minutter (≈ 220 filer, Codex trenger `history_past` til kalibrering). Skriv `data/fetched_at.txt`.

Verifiser og skriv `grunnlag.md`:
- Sesong, neste runde og frist (UTC og norsk tid), prisjusteringstider (`game_config.settings.price_change_deadlines`).
- Bank, tropp, brukte chips, gratisbytter (beregn fra `entry_history`: +1 per runde, maks 5, minus brukte; WC/FH-regelen er ikke verifisert).
- **Salgspriser**: kjøpspris fra R1-pris i `element-summary` eller `transfers.json`; salg = kjøp + halvparten av økningen rundet ned.
- Skader og flagg i egen tropp; blanke og doble runder i `fixtures.json`.
- Poengregler fra `game_config.scoring` (keepermål = 10 i 2026/27; `config/scoring.yaml` sier feilaktig 6).
- Offentlige data viser laget ved forrige frist. Bytter Simen har gjort etter det, syns ikke.

## Steg 2: Evaluer forrige ukes prognose (Claude)

1. `cd samarbeid/gwFORRIGE && shasum -a 256 -c prognose/SHA256SUMS`. Hvis noe feiler: si det, ikke reparer.
2. Hent faktiske poeng (`event/<runde>/live/`) og regn ut hva anbefalt plan og referansen uten bytter faktisk ga.
3. Skriv `gwNN/claude/evaluering-forrige.md`: anbefalt mot referanse, mot begge poengsettene, og hva Simen faktisk gjorde.
   Ett utfall beviser lite; før en løpende tabell over ukene.
4. **Prognoseevaluering** (endrer ikke modellen, bare måler den). Legg til forrige runde i `samarbeid/kalibrering/logg.csv`:
   én rad per spiller med forventet poeng ≥ 1 i ett av poengsettene, med kolonnene `runde, id, navn, posisjon, pris, minutter,
   xp_codex, xp_repo, faktisk, i_tropp, kaptein`. Forventet poeng hentes fra den frosne spillerfilen som står i forrige ukes
   `prognose/SHA256SUMS` (i gw08: `codex/spillerpoeng_r2.csv`), aldri fra en fil som er laget eller endret etter fristen.
   Faktisk fra `event/<runde>/live/`, pris fra forrige ukes `data/bootstrap.json`. Ta med spillere med 0 minutter
   (prognosen skal også fange minuttrisiko). Skriptet er `samarbeid/kalibrering/oppdater.py`: lag det første gang, gjenbruk det etterpå,
   og la det nekte å legge inn en runde som allerede finnes.
   Oppdater `samarbeid/kalibrering/oversikt.md` med skjevhet (snitt av faktisk − forventet) og standardfeil per poengsett, fordelt på
   posisjon × prisklasse (< 5,0 / 5,0–7,4 / 7,5–9,9 / ≥ 10,0) og for de ti med høyest forventet poeng hver runde (kapteinskandidatene).
   En skjevhet regnes som tydelig først når den er over 2 standardfeil, har samme fortegn i minst fire runder og bygger på minst
   fire runder. Svakere mønstre noteres, men brukes ikke.

## Steg 3: Selvstendige analyser (parallelt)

**Codex (start først, i bakgrunnen):** skriv `codex/oppdrag-1.md` (XML-blokker: `<task>`, `<required_alternatives>`,
`<model_rules>`, `<action_safety>`, `<deliverables>`, `<completeness_contract>`) og kjør:

```bash
node <companion> task --write "$(cat samarbeid/gwNN/codex/oppdrag-1.md)"
```

med `run_in_background: true`. Ny uke = ny tråd (ikke `--resume-last`). Be Codex ta utgangspunkt i forrige ukes `codex/modell_r3.py`
(eller nyeste), bruke denne ukens data, og vurdere minst: spare, 1 FT, 2+ FT, trekk, WC nå, WC senere (konkret runde), BB og FH før R19.
Ikke vis Codex Claudes forslag i første oppdrag.

**Claude (mens Codex jobber):** `claude/forutsetninger.md` (skader, roller, minutter, kampprogram, kildebelagt) og
`claude/forslag.md` (eget forslag med enkel kontrollregning), ferdig **før** Codex' resultat leses. Notér klokkeslett.

## Steg 4: Kritikk og revisjon (maks tre runder)

- Claude kontrollerer Codex' tall og antakelser i `claude/kritikk-av-codex.md`, og sender `codex/oppdrag-2.md` med `task --write --resume-last`.
- Codex kritiserer Claudes forslag og tester innvendingene. Uenighet avgjøres med beregninger, ikke enighet.
- Faste kontroller som avslørte feil i gw08:
  - Toppspillernes nivå (Haaland, Fernandes) mot observert snitt og repoets `data/derived/expected_points.csv`.
  - Kjøpsuniverset: ingen status `u`/`n`/`i`/0 %, benkespillere med p_start ≥ 0,5.
  - Sammenlign wildcardtidspunkter med **samme byttepolitikk og samme chipdatoer**.
  - En konkret tropp må testes under begge poengsettene, ikke bare hver modells egen favoritt.

## Steg 5: Beslutning og prognose (Claude)

- `beslutning.md`: handling nå, inn/ut, trekk, bank, ellever, kaptein, visekaptein, benk, plan for neste åtte runder (foreløpig merket),
  hvorfor fremfor å spare og fremfor beste WC-alternativ, forventet gevinst med periode, usikkerheter, hva som bør sjekkes før fristen,
  uenighet og hva kritikken endret.
- Tydelige skjevheter fra `samarbeid/kalibrering/oversikt.md` kan brukes som uttalt antakelse (særlig ved kapteinsvalg),
  og står da i `beslutning.md` med størrelse og antall runder. Modellen endres ikke av dette; en modellendring går via
  forhåndsregistrering i `samarbeid/modell/`.
- Kopier `gw08/claude/frys_prognose.py`, oppdater planene og runde-tallene, og kjør. Den nekter å overskrive en frosset prognose.
  Spillerfilen med forventet poeng for alle spillere (begge poengsettene) skal stå i `SHA256SUMS`, siden prognoseevalueringen bygger på den.
- Oppdater `oppgaver.md` (status og logg med UTC-tider fra filenes endringstid).

## Steg 6: Lagre

```bash
git add samarbeid/gwNN samarbeid/kalibrering && git commit -m "samarbeid: Claude + Codex, beslutning runde NN" && git push origin main
```

Rå `element-summary` committes ikke (`.gitignore`). Push virker uten Simen etter engangsoppsettet med token i nøkkelringen.
Hvis push likevel ber om innlogging: commit lokalt, si fra i svaret, og ikke be om token.

## Svaret til Simen

Ett samlet svar på norsk: anbefalt handling (inkludert wildcard), nøyaktige bytter, poengkostnad og bank, ellever, kaptein,
visekaptein, benk, åttesrundersplan, begrunnelse mot alternativene, forventet gevinst og usikkerheter, når byttet bør gjøres
(før prisjustering eller etter bestemte lagnyheter), evaluering av forrige uke, én linje om prognoseevalueringen
(tydelige skjevheter, eller «ingen ennå» og antall runder), og kort hvem som gjorde hva.

## Gjeldende sesongplan (oppdateres hver uke)

| Chip | Status | Foreløpig plan |
|---|---|---|
| Triple Captain 1 | Brukt R3 | – |
| Wildcard 1 | Anbefalt brukt R9 (Simen gjennomfører) | – |
| Bench Boost 1 | Tilgjengelig, utløper etter R19 | R19 |
| Free Hit 1 | Tilgjengelig, utløper etter R19 | R16, eller blank runde i juleperioden |
| Andre halvdel | Nytt sett WC/FH/BB/TC fra R20 | – |
