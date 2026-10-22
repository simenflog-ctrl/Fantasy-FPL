<task>
Runde 2 av kritikk og revisjon. Dette er siste beregningsrunde før Claude tar sluttbeslutningen. Les
samarbeid/gw08/claude/kritikk-av-codex-r2.md og samarbeid/gw08/claude/forutsetninger.md (tillegget nederst om R14–R19).

To konkrete tester avgjør om WC skal brukes i R8 eller holdes til R11:
</task>

<required_work>
1. **Like chipdatoer.** Kjør E (WC8) og B_WC11 med **identiske** BB- og FH-runder, for minst tre felles datopar
   (for eksempel BB15/FH9, BB17/FH13, BB19/FH13) og i begge poengsett (codex og repo_hybrid). Rapporter E minus B_WC11 for hvert par,
   samt hvert plans eget beste par. Da isoleres effekten av wildcardtidspunktet.
2. **Informasjonsverdi / skader.** Lag en enkel Monte Carlo-simulering (minst 300 trekk, fast seed) av nye fravær fra R9 til R19:
   - Hver spiller som eies, kan få fravær med sannsynlighet p per runde (hovedverdi p = 0,02; test også 0,01 og 0,03),
     med varighet trukket fra {1, 2, 3, 6} runder med like sannsynligheter. Fraværet er ukjent før runden det starter.
   - I B_WC11-banen: WC brukes i R11 som planlagt, men tidligere (R9 eller R10) hvis minst tre startere er ute den runden.
   - I begge baner brukes samme grådige byttepolitikk med gratisbytter til å erstatte fravær.
   - Rapporter gjennomsnittlig R8–R19 for E og B_WC11, forskjellen og andelen trekk der E vinner, for hver p.
   Hold det enkelt og dokumenter forenklingene. Bruk samme fravær for begge baner i hvert trekk (felles tilfeldige tall) der det er mulig.
3. Konklusjon: si eksplisitt om WC nå er bedre, likeverdig (innenfor ±5 poeng) eller dårligere enn WC i R11 etter disse testene.
</required_work>

<action_safety>
Skriv bare i samarbeid/gw08/codex/, nye filer med suffiks _r3. Ikke endre tidligere filer, src/, data/ eller claude/. Ikke commit, ingen installasjon, ingen nett.
</action_safety>

<deliverables>
- codex/kontroll_r3.md (norsk, kort): resultat av test 1 og 2, endelig anbefaling for R8 og hva som eventuelt ville endre den.
- codex/chipdatoer_r3.csv, codex/skadesim_r3.csv, og skriptet som gjenskaper dem.
</deliverables>

<completeness_contract>
Ferdig betyr: begge testene er kjørt fra skript, tallene i kontroll_r3.md stemmer med CSV-ene, og konklusjonen er tydelig.
Hold kjøretiden nede: reduser beam-bredde eller kandidatpool i simuleringen hvis nødvendig, og si hva du forenklet.
</completeness_contract>
