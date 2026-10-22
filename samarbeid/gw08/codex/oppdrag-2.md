<task>
Runde 1 av kritikk og revisjon (oppgave 6 i samarbeid/gw08/oppgaver.md). Les disse filene:
- samarbeid/gw08/claude/forslag.md — Claudes uavhengige forslag, skrevet før Claude leste analysen din. Kritiser det.
- samarbeid/gw08/claude/kritikk-av-codex.md — Claudes kontroll av modellen din. Svar på hver innvending: godta, avvis med belegg, eller test.
- samarbeid/gw08/claude/forutsetninger.md — Claudes kildebelagte rolle- og skadevurderinger.

Begge foreslår nå Szoboszlai → Tavernier i R8. Den reelle uenigheten er om **wildcard skal brukes nå (E) eller holdes**.
Claude mener E-fordelen er modellavhengig (+6,7 til +35 poeng R8–13 over B) og at tidspunktsammenligningen er skjev
fordi planene uten wildcard ikke bruker gratisbytter. Avgjør dette med beregninger.
</task>

<required_work>
1. **Kalibrering av toppspillere.** samarbeid/gw08/data/element_summary/ har nå 222 filer (alle med ≥ 300 min i år), med
   `history_past` (tidligere sesonger, inkl. expected_goals/assists og minutter). Bruk dette som prior for individuelle rater
   i stedet for, eller i tillegg til, krymping mot posisjonssnittet. Lag også lagstyrke på xG/xGA fra `player_matches`
   eller element_summary-historikken i stedet for faktiske mål, hvis det lar seg gjøre fra lokale data.
   Rapporter Haaland, B.Fernandes, Mbeumo, Rogers, Thiago og Tavernier før og etter, mot observert snitt.
2. **Filtrer kjøpsuniverset:** ingen spillere med status `u` eller `n`, ingen `i`/0 %, og benkespillere må ha rimelig startsannsynlighet.
   Dennis (BOU, «joined MK Dons») og begge Hughes er eksempler på feil i forrige runde.
3. **Rettferdig wildcardsammenligning R8–R19:**
   - E: WC i R8 (med den forbedrede modellen; finn troppen på nytt), deretter ett gratisbytte per runde der det lønner seg.
   - B + gratisbytter: R8 Szoboszlai → Tavernier, deretter en grådig eller beam-basert byttepolitikk med reelle gratisbytter
     (rulling, maks 5, ingen trekk med mindre gevinsten over de neste ~4 rundene er > 4), og WC i R11, R13, R15 og R17.
   - Bruk samme byttepolitikk i alle varianter. Ta med BB og FH før R20 i alle.
4. **Kjør hovedsammenligningen med to poengsett:** (a) din forbedrede modell og (b) repoets data/derived/expected_points.csv
   der den finnes (R8–13; for R14–19 kan du bruke ditt eget eller gjenta snitt). Si om E slår B+senere WC i begge.
5. **Følsomhet for R8-beslutningen:** Tavernier vs Dewsbury-Hall; Thiago vs Maguire i elleveren; Szoboszlai tilbake fra R11.
6. Kritiser Claudes forslag konkret: hva mangler, hva er feil, hva er godt nok.
</required_work>

<action_safety>
Skriv bare i samarbeid/gw08/codex/. Behold forrige runde sine filer; legg nye resultater i nye filer eller med suffiks _r2.
Ikke endre src/, data/, config/, tests/ eller claude/. Ikke commit. Ikke installer pakker. Ingen nettverkstilgang trengs.
</action_safety>

<deliverables>
- codex/kontroll.md (norsk): svar på hver innvending, kritikk av Claudes forslag, resultater fra punkt 1–5, og en tydelig
  anbefaling for R8: WC nå eller ikke, hvilke bytter, startellever, kaptein, visekaptein, benk.
- codex/alternativer_r2.csv og codex/wildcard_tidspunkt_r2.csv.
- Oppdatert modell.py (eller modell_r2.py) som gjenskaper tallene.
</deliverables>

<completeness_contract>
Ferdig betyr: skriptet kjører uten feil, tallene i kontroll.md kommer fra skriptet, og du sier eksplisitt om
WC nå er robust (bedre under begge poengsett og med rettferdig byttepolitikk) eller avhenger av én usikker antakelse.
Hvis noe ikke lar seg gjøre fra lokale data, si hva og hva du gjorde i stedet.
</completeness_contract>
