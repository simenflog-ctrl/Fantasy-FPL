# Oppgaveliste runde 12

Felles liste for Claude og Codex. Hver oppgave har én eier.

**Filansvar:**
- Claude skriver bare i `claude/`, `grunnlag.md`, `oppgaver.md`, `beslutning.md`, `prognose/` og `samarbeid/kalibrering/`.
- Codex skriver bare i `codex/`.
- `data/` ble fryst etter hentingen 2026-11-26 07:44 UTC.
- Ingen av agentene endrer `src/`, `config/`, `tests/`, `data/` i repoets rot eller andre filer i repoet.

**Ukemotoren** (`samarbeid/motor/`) er ennå ikke flettet til `main`. Den er ikke prøvekjørt denne uken, så beregningene er Codex'.

**Codex-modell:** `~/.codex/config.toml` har `gpt-6-astra`, som ikke støttes med ChatGPT-kontoen («model is not supported»).
Alle Codex-kall denne uken bruker derfor `--model gpt-6-luna` (fra `~/.codex/models_cache.json`), som beskrevet i utkastet til
RUTINE på grenen `ukemotor-til-main`.

| # | Eier | Oppgave | Leveranse | Status |
|---|---|---|---|---|
| 0–1 | Claude (agenten fpl-datagrunnlag) | Data, lagstatus og salgspriser; evaluering av R11 og prognoseevaluering | `grunnlag.md`, `data/`, `claude/evaluering-forrige.md`, `kalibrering/` | Ferdig |
| 2 | Claude | Nyheter og minuttoverstyringer | `claude/forutsetninger.md`, `claude/minutter_overstyring.csv` | Ferdig |
| 3 | Codex | Poengmodell og bytte- og chipplaner R12–R19 (skriptene fra gw11 oppdatert) | `codex/analyse.md` | Ferdig |
| 4 | Claude | Eget forslag før Codex' resultat | `claude/forslag.md` | Ferdig |
| 5 | Claude | Kontroll av Codex' analyse | `claude/kritikk-av-codex.md` | Ferdig |
| 6 | Codex | Kritikk av Claudes forslag (`codex/oppdrag-2.md`) | `codex/kontroll.md`, `codex/kontroll_r12.csv` | Ferdig |
| 7 | Claude | Sluttbeslutning og prognose | `beslutning.md`, `prognose/` | Ferdig |

## Logg (UTC), 26. nov

- 07:36: Den planlagte oppgaven starter analysen. R11 er ferdigspilt, og fristen for R12 er 27. nov 18:30 UTC.
  `main` var ren, og botens data fra 21. og 23. nov ble flettet inn uten konflikter.
- 07:37–07:49: Agenten fpl-datagrunnlag henter data og evaluerer R11. Simen fulgte anbefalingen: Muharemović → Van Hecke,
  Bench Boost og kaptein Haaland. Laget fikk 67 poeng (snitt 35) og har nå totalrank 403 909. For første gang oppfyller noen grupper
  kriteriet for tydelig skjevhet i prognoseevalueringen.
- 07:50: Codex-oppdrag 1 feiler på modellen `gpt-6-astra` og sendes på nytt med `--model gpt-6-luna` (ny tråd).
- 07:52–07:55: Claude leverer `forutsetninger.md`, `minutter_overstyring.csv` og `forslag.md` (Ødegaard → Le Fée og
  Dasilva → Konsa, med det tredje byttet spart) før Codex' filer er lest.
- 08:33: Codex leverer oppdrag 1 (`analyse.md` med flere filer): G_keep, Dasilva og Silva ut, Bogle og Justin inn, kaptein De Cuyper og FH15.
  Ødegaard-salget gir −0,56 / +1,39 og oppfyller ikke regelen.
- 08:40: `claude/kritikk-av-codex.md`: gevinsten etter R12 kommer trolig fra senere modellbytter, og Claudes P og salg av Dasilva med ett bytte mangler.
  `codex/oppdrag-2.md` sendes (`--resume-last --model gpt-6-luna`).
- 08:47: Codex leverer `kontroll.md`: P −1,33 mot G_keep i blandingen (−0,39 ved 2 % skade). Med fast tropp gir G_keep +0,06 / +0,85 mot rull,
  og Mitchell (Dasilva-salg med ett bytte) er svakere. Justin + Konsa gir −0,24, med stor spredning mellom poengsettene. De Cuyper er fortsatt kaptein.
- 08:55: Claude beslutter G_keep og kaptein De Cuyper, med B som valg hvis Simen bare har 2 gratisbytter (`beslutning.md`).
  Prognosen er frosset (`prognose/prognose_R12.json`, `SHA256SUMS`; alle OK). Codex' mellomlagring (`codex/checkpoints/`) committes ikke.
