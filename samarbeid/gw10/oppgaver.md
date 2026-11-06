# Oppgaveliste runde 10

Felles liste for Claude og Codex. Hver oppgave har én eier.

**Filansvar:** Claude skriver bare i `claude/`, `grunnlag.md`, `oppgaver.md`, `beslutning.md`, `prognose/`
og `samarbeid/kalibrering/`. Codex skriver bare i `codex/`. `data/` er fryst etter henting 2026-11-06 06:38 UTC.
Ingen av agentene endrer `src/`, `config/`, `tests/`, `data/` i repoets rot eller andre filer i repoet.

| # | Eier | Oppgave | Leveranse | Status |
|---|---|---|---|---|
| 0–1 | Claude (agent fpl-datagrunnlag) | Data, lagstatus, salgspriser; evaluering av R9 og prognoseevaluering | `grunnlag.md`, `data/`, `claude/evaluering-forrige.md`, `kalibrering/` | Ferdig |
| 2 | Claude | Lagnyheter, Europa-belastning, minutter | `claude/forutsetninger.md` | Ferdig |
| 3 | Codex | Poengmodell, bytte- og chipplaner R10–R19 (BB nå eller senere) | `codex/analyse.md` + `modell.py` | Foreløpig (bruksgrense) |
| 4 | Claude | Eget forslag før Codex' resultat | `claude/forslag.md` | Ferdig |
| 5 | Claude | Kontroll av Codex' analyse | `claude/kritikk-av-codex.md` | Ferdig |
| 6 | Codex | Skadesimulering A/B/C, Claudes forslag, BB10 | `codex/kontroll.md` | Ferdig (én runde) |
| 7 | Claude | Sluttbeslutning og prognose | `beslutning.md`, `prognose/` | Ferdig |

## Logg (UTC), 6. nov

- 06:38–06:43: Agenten fpl-datagrunnlag henter data; wildcarden i R9 bekreftet (vise Ødegaard i stedet for Mbeumo). R9: 48 poeng, −9 mot referansen.
- 06:44: Codex får oppdrag 1.
- 06:45: Claude leverer `forutsetninger.md` og `forslag.md` (Dasilva → Van Hecke, Isak → Evanilson, BB nå) før Codex' resultat finnes.
- 06:58: Codex stopper på bruksgrensen («try again at 12:44 PM» norsk tid) med foreløpig `analyse.md`: knapp leder Tzolakis → Verbruggen
  (+0,4 mot rull), BB12 i stedet for BB10 (BB10 1–3 poeng bak), FH13.
- 06:59: Claude-kontroll (`claude/kritikk-av-codex.md`): Claude trekker Isak → Evanilson og BB10; forskjellene mellom rull, keeperbytte og
  tobytte er støy. `codex/oppdrag-2.md` skrevet, sendes etter 11:44 UTC.
- 11:46: Oppdrag 2 sendt med `--resume-last`.
- 13:33: Codex leverer `codex/kontroll.md` og stopper deretter på bruksgrensen igjen. Iwobi-pakken +0,12 og keeperbytte +0,03 mot rull
  (2 % nye fravær); BB10 bak beste BB-dato i alle ni tester.
- 13:34: Claude tar sluttbeslutning: **rull, ikke BB** (`beslutning.md`), og fryser prognosen (`prognose/prognose_R10.json`, SHA256SUMS).
  Tredje kritikkrunde ikke brukt.
