<task>
Du er Codex og jobber sammen med Claude om ett virkelig Fantasy Premier League-lag (ID 7089878, sesong 2026/27).
Målet er høyest mulig forventet totalpoengsum resten av sesongen. Neste frist er runde 8, 2026-10-23 17:30 UTC.
Claude har ansvar for lagnyheter, skader og spilletid. Du har ansvar for beregningene.

Ditt oppdrag (oppgave 3 i samarbeid/gw08/oppgaver.md): bygg en transparent og reproduserbar
poengmodell, og ranger reelle bytte- og chipplaner for runde 8–15. Ta også med verdien av chips
og fleksibilitet til og med runde 19, som er siste runde for WC1, FH1 og BB1.

Arbeidsmappe: samarbeid/gw08/ i repoet. Les grunnlag.md og oppgaver.md først.
Ferske, frosne API-data ligger i samarbeid/gw08/data/ (bootstrap.json, fixtures.json, picks_gw7.json,
entry_history.json, transfers.json, salgspriser.json, element_summary/).
Repoet har en eksisterende modell i src/ (expected_points.py, minutes.py, team_strength.py, optimize.py)
med utdata i data/derived/ (expected_points_horizon.csv, minutes.csv, plan.json). Disse ble generert
i dag kl. 11 UTC og er ikke kontrollert. Du kan bruke dem, men skal etterprøve dem:
plan.json foreslår wildcard nå. Kontroller blant annet om den bruker salgspriser eller nåpriser,
og om horisont, lagbegrensning og spilletid er riktig håndtert.
</task>

<required_alternatives>
Vurder minst disse, med samme poengmodell for alle:
A. Spare byttene (0 bytter, rull til 3 gratisbytter i R9). Dette er referansealternativet.
B. Beste plan med 1 gratisbytte.
C. Beste plan med 2 gratisbytter.
D. Beste plan med ett eller flere poengtrekk (-4 per ekstra bytte), hvis gevinsten forsvarer det.
E. Wildcard nå (R8), med optimal ny tropp innenfor salgsverdi + bank = 99,3.
F. Wildcard senere, i en konkret runde mellom R9 og R19, med begrunnelse for hvilken.
G. Bench Boost og Free Hit: når gir de mest innen R19?
Ta hensyn til at Szoboszlai er skadet (0 %, ukjent comeback), at MUN og BHA allerede har 3 spillere,
at budsjettet skal regnes med salgspriser, og at ubrukte gratisbytter har en verdi fremover.
</required_alternatives>

<model_rules>
- Bruk poengreglene i bootstrap.json → game_config.scoring, ikke config/scoring.yaml (den har feil keepermål).
- Gjør antakelser om spilletid eksplisitte. Lag en enkel spilletidsparameter per spiller som Claude kan overstyre
  senere: skriv den til codex/minutter_antatt.csv (kolonner: id, navn, lag, gw_fra, gw_til, p_start, forventede_min, kilde).
- Ikke presenter tall med mer presisjon enn modellen tåler. Oppgi usikkerhet (spredning eller intervall) for hovedalternativene.
- Behandle ikke 8-rundersresultatet som sesongoptimum: si hva som skjer med chipverdien til R19 og videre.
- Ingen nettverkstilgang er nødvendig. Hvis noe mangler i dataene, si det i stedet for å gjette.
</model_rules>

<action_safety>
Skriv bare i samarbeid/gw08/codex/. Ikke endre src/, data/, config/, tests/ eller noen andre filer.
Ikke commit noe i git. Ikke installer pakker globalt; bruk det som er installert (python3, pandas hvis tilgjengelig).
</action_safety>

<deliverables>
1. codex/modell.py (eller tilsvarende): ett skript som gjenskaper alle tallene fra data/ og skriver resultatene.
2. codex/minutter_antatt.csv som beskrevet over.
3. codex/alternativer.csv: én rad per alternativ med bytter inn/ut, poengtrekk, penger igjen, forventet poeng R8, R8–R11, R8–R15, og usikkerhet.
4. codex/analyse.md på norsk med:
   - rangert liste over alternativene og anbefalt handling for R8, med startellever, kaptein, visekaptein og benk
   - budsjettkontroll med salgspriser for hvert alternativ
   - hva i repoets plan.json du er enig eller uenig i, og hvorfor
   - svakheter i datagrunnlaget og hvilke antakelser resultatet er mest følsomt for
   - skille mellom verifiserte data, modellresultater og antakelser
</deliverables>

<completeness_contract>
Ferdig betyr: modell.py kjører fra start til slutt uten feil, alternativer.csv har alle alternativene A–G,
og analyse.md sier tydelig hva du anbefaler for R8 og hvor robust det er. Kjør skriptet selv og bekreft at tallene i analyse.md
stemmer med det skriptet skriver.
</completeness_contract>
