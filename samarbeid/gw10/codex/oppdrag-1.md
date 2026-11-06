<task>
Du er Codex og jobber sammen med Claude om ett virkelig Fantasy Premier League-lag (ID 7089878, sesong 2026/27).
Målet er høyest mulig forventet totalpoengsum resten av sesongen. Neste frist er runde 10, 2026-11-06 18:30 UTC (i dag).
Claude har ansvar for lagnyheter, skader og spilletid. Du har ansvar for beregningene.

Arbeidsmappe: samarbeid/gw10/ i repoet. Les grunnlag.md først, og samarbeid/gw09/beslutning.md og gw09/codex/kontroll.md
for forrige ukes beslutning og metode. Frosne API-data for denne uken ligger i samarbeid/gw10/data/ (bootstrap.json, fixtures.json,
picks_gw9.json, entry_history.json, transfers.json, salgspriser.json, live_gw9.json, element_summary/ med history og history_past).

Ta utgangspunkt i samarbeid/gw09/codex/modell_r2.py (nyeste, med eksakte autobytter og parede skadesimuleringer), kopier den
til gw10/codex/modell.py og oppdater til ukens data (R10–R19). Behold begge poengsettene: "codex" og "repo_hybrid"
(repoets xP i data/derived/expected_points.csv, generert av GitHub-boten 5. nov; sjekk hvilke runder den dekker).

Wildcard 1 ble brukt i R9. Tropp, bank (£0,4m) og salgspriser er verifisert i grunnlag.md. Gratisbytter i R10 er ikke verifisert:
antakelse 2 (mulig 1 eller 3). Ingen klubb har tre spillere. Ingen blanke eller doble runder før R19.
Codex' kvote har sluppet opp to ganger forrige uke: skriv analyse.md tidlig og oppdater den, slik at noe brukbart finnes hvis du stopper.
</task>

<known_news>
Verifisert fra API-et 6. nov 06:38 UTC eller kildebelagte nyheter 4.–6. nov. Fakta, ikke Claudes forslag.
- Alle 15 i egen tropp har status a og ingen nyhet i API-et.
- Groß (BHA): fikk en smell på foten mot slutten av 1–0-seieren på City i R9 (Sussex Express 5./6. nov); ingen diagnose.
  Brighton spilte Europa League borte mot Getafe torsdag 5. nov; ligakamp mot BRE søndag 14:00 UTC.
- Bournemouth (Tavernier, Silva) spilte Europa League mot Sparta Praha torsdag; IPS borte søndag 14:00 UTC.
  Alex Toth (BOU) operert, ute til 2027; Juanlu Sanchez (BOU) ny ankelskade.
- Coventry: Bobby Thomas (id 173) tvilsom (legg). Everton: Grealish utestengt internt mot COV.
- Leeds: Calvert-Lewin «forsiktig optimistisk»; Okafor og Stach store tvil; Justin og Gudmundsson OK.
- Hull: Crooks utestengt én kamp; Morita (lyske) ute «noen uker».
- Ute (0 %): João Pedro, Saka, Semenyo, Lacroix, Cash (utestengt til 21. nov), Shaw, James, Šeško, Frimpong, E.Martinez (CHE),
  Lisandro Martínez (MUN, utestengt). Tvil 75 %: Rashford, Gravenberch, Henderson.
- Kjøpsuniverset: ingen spillere med status u, n, i eller 0 %; status d gis redusert startsannsynlighet.
</known_news>

<required_alternatives>
Vurder minst disse, med samme poengmodell og eksakte autobytter for alle:
A. Spare byttene (rull). Referansealternativet.
B. Beste plan med 1 gratisbytte.
C. Beste plan med 2 gratisbytter.
D. Beste plan med poengtrekk (−4 per ekstra bytte), bare hvis gevinsten forsvarer det.
E. Bench Boost i R10 mot Bench Boost i hver av R11–R19 (særlig R19, som var forrige ukes plan), med samme byttepolitikk og samme
   FH-dato. Simen spør konkret om BB10 er lurt nå som hele troppen er ny og alle 15 forventes å spille. Rapporter benkens forventning
   per runde for planene, og hvor mye skadesimuleringen (1–3 % nye fravær) flytter forskjellen mellom BB10 og BB senere.
F. Free Hit: beste runde R11–R19 (forrige plan: R16), sammen med BB-valget.
G. Kaptein og visekaptein for R10, med forventning for de 3–4 beste kandidatene.
Rangér med FT-antakelse 2, og vis om anbefalingen endres med 1 eller 3 gratisbytter.
</required_alternatives>

<model_rules>
- Poengregler fra bootstrap.json → game_config.scoring (keepermål 10), ikke config/scoring.yaml.
- Spilletid eksplisitt i codex/minutter_antatt.csv (id, navn, lag, gw_fra, gw_til, p_start, forventede_min, kilde), slik at Claude kan overstyre.
  Ta hensyn til torsdagskamp i Europa for BHA, BOU, SUN, CRY (søndagskamp i R10) som en mulig rotasjonsfaktor, og si hvordan.
- Faste kontroller: toppspillernes nivå (Haaland, Salah, Palmer og andre premium) mot observert snitt 2026/27 og repoets xP.
  En konkret tropp testes under begge poengsettene.
- Prognoseevalueringen (samarbeid/kalibrering/oversikt.md) har ingen tydelige skjevheter ennå (2 runder); ikke juster modellen etter den.
- Oppgi usikkerhet (spredning eller intervall) for hovedalternativene.
- Lever codex/spillerpoeng.csv med kolonnene id, navn, gw, codex, repo_hybrid for alle spillere og R10–R17. Den fryses med prognosen.
- Ingen nettverkstilgang er nødvendig. Hvis noe mangler i dataene, si det i stedet for å gjette.
</model_rules>

<action_safety>
Skriv bare i samarbeid/gw10/codex/. Ikke endre src/, data/, config/, tests/ eller andre filer, og ikke gw09/.
Ikke commit noe i git. Ikke installer pakker; bruk Anaconda: export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH
</action_safety>

<deliverables>
1. codex/modell.py: ett skript som gjenskaper alle tallene fra data/ og skriver resultatene.
2. codex/minutter_antatt.csv og codex/spillerpoeng.csv som beskrevet.
3. codex/alternativer.csv: én rad per alternativ med bytter inn/ut, poengtrekk, bank etter, forventet poeng R10, R10–R13, R10–R19 med chips, og usikkerhet.
4. codex/analyse.md på norsk: rangerte alternativer og anbefalt handling for R10 med ellever, kaptein, visekaptein og benk;
   budsjettkontroll med salgspriser; BB- og FH-tidspunkt; følsomhet for FT-antall og Groß' spilletid;
   skille mellom verifiserte data, modellresultater og antakelser.
</deliverables>

<completeness_contract>
Ferdig betyr: modell.py kjører uten feil, alternativer.csv har alternativene A–G, spillerpoeng.csv dekker alle spillere R10–R17
i begge poengsett, og analyse.md sier tydelig hva du anbefaler for R10 (inkludert BB nå eller ikke) og hvor robust det er.
Kjør skriptet selv og bekreft at tallene i analyse.md stemmer med det skriptet skriver.
</completeness_contract>
