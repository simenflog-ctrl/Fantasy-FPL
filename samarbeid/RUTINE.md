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
- Filansvar: Claude skriver i `claude/`, `grunnlag.md`, `oppgaver.md`, `beslutning.md`, `prognose/`. Codex skriver bare i `codex/`.
  Ingen endrer `src/`, `config/`, `tests/` eller `data/` i repoets rot. `gwNN/data/` fryses etter henting.

## Steg 0: Klargjøring

1. Node for Codex: `export PATH="$HOME/.nvm/versions/node/v24.22.1/bin:$PATH"` i hver Bash-kommando som kaller Codex
   (`~/.zprofile` har den også, men appens skall leser den ikke alltid).
2. Sjekk Codex: `node ~/.claude/plugins/cache/openai-codex/codex/<versjon>/scripts/codex-companion.mjs setup --json`.
3. Hent GitHub-botens dataoppdateringer: `git fetch origin && git merge origin/main`.
   - Konflikter i `data/` → ta botens versjon (`git checkout --theirs`), den er nyest.
   - Konflikter i `src/` → undersøk begge sider med `git log` før du velger (se mergen 22. okt: opplastingen hadde eldre kode).
4. Kontroller at `main` er ren før du starter.

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
- Kopier `gw08/claude/frys_prognose.py`, oppdater planene og runde-tallene, og kjør. Den nekter å overskrive en frosset prognose.
- Oppdater `oppgaver.md` (status og logg med UTC-tider fra filenes endringstid).

## Steg 6: Lagre

```bash
git add samarbeid/gwNN && git commit -m "samarbeid: Claude + Codex, beslutning runde NN" && git push origin main
```

Rå `element-summary` committes ikke (`.gitignore`). Push virker uten Simen etter engangsoppsettet med token i nøkkelringen.
Hvis push likevel ber om innlogging: commit lokalt, si fra i svaret, og ikke be om token.

## Svaret til Simen

Ett samlet svar på norsk: anbefalt handling (inkludert wildcard), nøyaktige bytter, poengkostnad og bank, ellever, kaptein,
visekaptein, benk, åttesrundersplan, begrunnelse mot alternativene, forventet gevinst og usikkerheter, når byttet bør gjøres
(før prisjustering eller etter bestemte lagnyheter), evaluering av forrige uke, og kort hvem som gjorde hva.

## Gjeldende sesongplan (oppdateres hver uke)

| Chip | Status | Foreløpig plan |
|---|---|---|
| Triple Captain 1 | Brukt R3 | – |
| Wildcard 1 | Tilgjengelig, utløper etter R19 | R11 |
| Bench Boost 1 | Tilgjengelig, utløper etter R19 | R15 |
| Free Hit 1 | Tilgjengelig, utløper etter R19 | Reserve til juleperioden (R17–R19) eller blank runde |
| Andre halvdel | Nytt sett WC/FH/BB/TC fra R20 | – |
