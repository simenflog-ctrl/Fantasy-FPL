<task>
Du er Codex og jobber sammen med Claude om ett virkelig Fantasy Premier League-lag (ID 7089878, sesong 2026/27).
Målet er høyest mulig forventet totalpoengsum resten av sesongen. Neste frist er runde 9, 2026-10-31 11:00 UTC.
Claude har ansvar for lagnyheter, skader og spilletid. Du har ansvar for beregningene.

Arbeidsmappe: samarbeid/gw09/ i repoet. Les grunnlag.md først, og samarbeid/gw08/beslutning.md og gw08/codex/kontroll_r3.md
for forrige ukes beslutning og metode. Frosne API-data for denne uken ligger i samarbeid/gw09/data/ (bootstrap.json, fixtures.json,
picks_gw8.json, entry_history.json, transfers.json, salgspriser.json, live_gw8.json, element_summary/ med history og history_past).

Ta utgangspunkt i samarbeid/gw08/codex/modell_r3.py (nyeste versjon), kopier den til gw09/codex/ og oppdater den til ukens data.
Behold begge poengsettene fra forrige uke: "codex" (din kalibrerte modell) og "repo_hybrid" (repoets xP fra data/derived/,
som nå er generert av GitHub-boten 26. okt; sjekk om den dekker R9 og hvilke runder). Rangér reelle bytte- og chipplaner for R9–R16,
og ta med chipverdien til og med R19 (siste runde for WC1, FH1 og BB1).

Tropp, bank (£1,6m), salgspriser og 2 gratisbytter er verifisert i grunnlag.md. MUN og BHA har allerede 3 spillere.
</task>

<known_news>
Verifisert fra API-et eller kildebelagte nyheter 26.–29. okt. Dette er fakta, ikke Claudes forslag. Claude kommer med fullstendige
spilletidsantakelser etterpå; bruk dette som utgangspunkt i minutter_antatt.csv og merk kilden.
- B.Fernandes (MUN): ubrukt innbytter i R8 (0 min) etter uenighet med Carrick; Sky Sports 28. okt: ventes tilbake i laget mot Chelsea i R9.
  API-status a. Behandl startsannsynligheten som noe lavere enn normalt, ikke null.
- Calafiori (ARS): status d, 75 %, hofte; 22 min i R8; tvilsom mot Liverpool (søndag). Hincapie og Lewis-Skelly startet cupkampen.
- N.Williams (NFO): status d, 75 %, arm/albue.
- Ligacupen 27.–29. okt (4. runde): Haaland og Verbruggen hvilte (Rulli og Steele i mål). Le Fée hvilte (Sunderland gjorde 11 bytter).
  Thiago spilte hele cupkampen og scoret (Sunderland 3–2 Brentford). Tavernier startet cupkampen (Bournemouth 3–0 Villa).
  Groß spilte i cupen (Man City 2–2 Brighton, 120 min + straffer). Arsenal røk ut mot Fleetwood med et nesten helt rotert lag; Konsa 8 min.
- Ute i R9 og lenger (FPL-flagg 0 % eller klubb): Saka, Semenyo (≈ 8 uker), Szoboszlai (tvilsom), João Pedro (CHE, «noen uker»),
  Sesko, Shaw, Mainoo (tilbake ≈ 8. nov), Mitoma (til etter landslagspausen).
- Kjøpsuniverset: ingen spillere med status u, n, i eller 0 %; spillere med status d gis redusert startsannsynlighet.
</known_news>

<required_alternatives>
Vurder minst disse, med samme poengmodell for alle:
A. Spare byttene (0 bytter, rull til 3 gratisbytter i R10). Referansealternativet.
B. Beste plan med 1 gratisbytte.
C. Beste plan med 2 gratisbytter.
D. Beste plan med ett eller flere poengtrekk (−4 per ekstra bytte), hvis gevinsten forsvarer det.
E. Wildcard nå (R9), med optimal tropp innenfor salgsverdi + bank = £99,4m.
F. Wildcard senere i en konkret runde (minst R10 og R11 sammenlignet; R10-frist 6. nov, R11-frist 21. nov, landslagspause imellom).
G. Bench Boost og Free Hit: når gir de mest innen R19?
Wildcardtidspunkter skal sammenlignes med samme byttepolitikk og samme BB/FH-datoer (lærdom fra gw08).
</required_alternatives>

<model_rules>
- Poengregler fra bootstrap.json → game_config.scoring (keepermål 10), ikke config/scoring.yaml.
- Spilletid eksplisitt i codex/minutter_antatt.csv (id, navn, lag, gw_fra, gw_til, p_start, forventede_min, kilde), slik at Claude kan overstyre.
- Faste kontroller: toppspillernes nivå (Haaland, Fernandes, Salah og andre premium) mot observert snitt 2026/27 og repoets
  data/derived/expected_points.csv; bonus for premiumspillere særskilt. En konkret tropp testes under begge poengsettene.
- Oppgi usikkerhet (spredning eller intervall) for hovedalternativene, og ikke mer presisjon enn modellen tåler.
- Lever også en spillerfil codex/spillerpoeng.csv med kolonnene id, navn, gw, codex, repo_hybrid for alle spillere og R9–R16.
  Den fryses sammen med prognosen og brukes i prognoseevalueringen.
- Ingen nettverkstilgang er nødvendig. Hvis noe mangler i dataene, si det i stedet for å gjette.
</model_rules>

<action_safety>
Skriv bare i samarbeid/gw09/codex/. Ikke endre src/, data/, config/, tests/ eller andre filer, og ikke gw08/.
Ikke commit noe i git. Ikke installer pakker; bruk Anaconda: export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH
</action_safety>

<deliverables>
1. codex/modell.py: ett skript som gjenskaper alle tallene fra data/ og skriver resultatene.
2. codex/minutter_antatt.csv og codex/spillerpoeng.csv som beskrevet.
3. codex/alternativer.csv: én rad per alternativ med bytter inn/ut, poengtrekk, bank etter, forventet poeng R9, R9–R12, R9–R16, R9–R19 med chips, og usikkerhet.
4. codex/analyse.md på norsk: rangerte alternativer og anbefalt handling for R9 med ellever, kaptein, visekaptein og benk;
   budsjettkontroll med salgspriser; WC-tidspunkt med lik chipkalender; følsomhet (særlig Fernandes' og Calafioris spilletid);
   skille mellom verifiserte data, modellresultater og antakelser.
</deliverables>

<completeness_contract>
Ferdig betyr: modell.py kjører fra start til slutt uten feil, alternativer.csv har alle alternativene A–G, spillerpoeng.csv dekker
alle spillere R9–R16 i begge poengsett, og analyse.md sier tydelig hva du anbefaler for R9 og hvor robust det er.
Kjør skriptet selv og bekreft at tallene i analyse.md stemmer med det skriptet skriver.
</completeness_contract>
