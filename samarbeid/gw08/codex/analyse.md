# Beregning og anbefaling R8

**Foreløpig anbefaling: ett gratisbytte, Szoboszlai → Tavernier. Behold wildcard til ny vurdering i R9.** Dette er alternativ B nå og F som betinget videre plan. Bekreft innspillerens rolle med Claude før fristen. Modellen har ikke nok informasjon til å bevise et sesongoptimum eller et optimalt wildcardlag.

## Verifiserte inngangsdata

Fryst API-uttrekk i `../data/`, 22. oktober 2026. Lag 7089878, to gratisbytter, bank £1,0m. Salgsverdi £98,3m; disponibel likvidasjonsverdi £99,3m. Szoboszlai har skadeflagg og 0 %. MUN og BHA har tre hver. Ingen blanke/doble runder i den frosne terminlisten til R19. WC1, BB1 og FH1 utløper R19 ifølge grunnlag.md. API-scoring gir keepermål 10. Ingen nettdata eller repoets avledede poeng brukes som modellinput.

## Modell og søk

Alle alternativer bruker samme spillerpoeng og beste lovlige formasjon hver runde, med dobbel kaptein. 15 spillere: 2/5/5/3, maks tre fra hver klubb; én keeper, minst tre forsvarere, to midtbanespillere og én spiss i elleveren. Budsjettet kontrolleres i heltall (tideler av million). Beholdte egne spillere verdsettes til salgspris, innkjøp til nåpris. Ingen prisendringer antas. Wildcard betyr ikke at beholdte spillere må kjøpes tilbake.

Lagstyrke bygger på mål for/mot i ferdigspilte R1–7, krympet med sju ligagjennomsnittskamper. Hjemme-/bortefaktor er antatt 1,1/0,9. Ingen motstanderjustert regresjon. Individuelle xG/xA per 90 krympes med 270 minutter mot minuttvektet posisjonssnitt fra samme sesong. Mål og assists skaleres med motstanderens forsvar. Poisson brukes til nullen, innslupne par og redningstripler. Bonus, kort, selvmål og straffehendelser bruker krympede historiske rater. Bonus er ikke modellert som konkurranse om seks poeng, en svakhet.

Poengvektene leses fra `game_config.scoring`, inklusive keepermål 10. Tersklene 60 minutter, to innslupne, tre redninger og DC 10/12 er regelantakelser fra grunnlaget; API-scoring oppgir bare poengvektene. DC for egne spillere bruker treff i 60+-kamper med tre pseudoobservasjoner (ett treff). For andre brukes aggregert DC per 90 delt på terskelen × 0,35, avgrenset ved 0,8. Dette er en grov og viktig antakelse, ikke en verifisert sannsynlighetsmodell.

`minutter_antatt.csv` er både leveranse og input. Første kjøring oppretter den; senere kjøringer bevarer overstyringer. Alle 668 spillere har intervall R8–19. Egne spillere får nyere starter vektet med halveringstid fire runder; andre får (starter + 0,35)/7,7. Forventet spilletid bygger på årets minutter og starter. Skade-/suspensjonsstatus holdes gjennom hele perioden, inklusive null for Szoboszlai. Det er et konservativt scenario, ikke en prognose om skadevarighet. P(60+) settes til 0,95 × min(p_start, forventede_min/65); innhoppssannsynlighet er en enkel restberegning. Rader som overlapper: siste rad gjelder. Claude kan endre p_start og forventede_min per intervall uten å endre kode.

B undersøker alle tilgjengelige enkeltbytter. C og D bruker deterministisk beam-søk med 24 beholdte tilstander og en kandidatpool per posisjon. Wildcard/FH bruker lokal forbedring fra eksisterende og billig lovlig tropp. Disse er **beste funn, ikke bevist optimale**. Særlig tverrposisjonelle finansieringsbytter kan overses. `solver.json` viser evaluerte tilstander og status. Ingen heltallsløser er tilgjengelig i installert miljø.

For A–E beholdes troppen etter R8 og startlaget optimeres ukentlig. F gjør B i R8 og wildcard i oppgitt runde; ellers holdes troppen. E velges for R8–15, E19 for R8–19 som horisontkontroll. Ingen videre gratisbytter brukes i disse sammenligningene. Resultatene viser derfor ikke beste adaptive flerukersplan, og lang horisont overvurderer gevinsten av mange bytter nå sammenlignet med gratis reparasjoner senere. G_BB og G_FH bygger på B og bruker hver sin chip; FH-troppen forsvinner etter chiprunden.

## Modellresultater og rangering

Poeng inkluderer kaptein og oppgitte trekk. Spredning er stresscenario for forventningen, **ikke** et sannsynlighetsintervall for faktiske poeng: lav = 0,90 × spillerpoeng − 0,25 × angrepspoeng; høy = 1,05 × spillerpoeng + 0,25 × angrepspoeng. Elleveren velges på nytt i scenarioene. Faktisk kampvariasjon og lagkorrelasjon kommer i tillegg. Overlapp kan ikke brukes som en statistisk test på forskjellen.

| Rang | Alternativ | R8 | R8–11 | R8–15 | Stress R8–15 | R8–19 |
|---|---|---:|---:|---:|---|---:|
| 1 | E19 | 58.2 | 232.0 | 470.7 | 384–535 | 713.5 |
| 2 | E | 58.8 | 231.5 | 469.6 | 382–535 | 706.8 |
| 3 | F | 53.9 | 227.6 | 466.7 | 381–529 | 709.3 |
| 4 | D5 | 46.2 | 215.1 | 448.5 | 361–513 | 682.8 |
| 5 | D4 | 49.2 | 215.8 | 446.0 | 360–509 | 676.7 |
| 6 | D3 | 52.0 | 215.5 | 441.2 | 359–502 | 670.8 |
| 7 | C | 55.1 | 215.6 | 434.3 | 352–495 | 655.6 |
| 8 | G_FH | 53.9 | 210.8 | 433.8 | 352–494 | 653.9 |
| 9 | G_BB | 60.5 | 217.4 | 430.9 | 349–491 | 651.0 |
| 10 | B | 53.9 | 210.8 | 424.3 | 344–484 | 644.4 |
| 11 | A | 52.1 | 201.8 | 407.6 | 331–464 | 617.3 |

Rangeringen er rå modellpoeng under de oppgitte faste planene. Den er ikke en handlingsrangering med likt chipforbruk. E/E19/F bruker WC, G bruker BB/FH, mens A–D beholder disse ressursene.

B slår A med 16.7 poeng til R15 i scenarioet der Szoboszlai fortsatt er ute. C gir ytterligere 10.0, men koster den andre gratisbytten og selger en spillende Thiago. D3/D4/D5 viser at trekk kan tjenes inn dersom troppen ellers holdes urørt; dette er ikke grunnlag for å ta trekk nå, fordi gratisbytter senere ikke er optimert. Anbefalingen om å selge den skadde spilleren er mer robust enn navnene på innspillerne, chipdatoene eller salg av friske spillere.

## Startlag R8 for anbefalt B

**Elleve:** Calafiori, Konsa, Tavernier, Verbruggen, Groß, Haaland, Maguire, B.Fernandes, Mbeumo, N.Williams, E.Le Fée.

**Kaptein:** Haaland. **Visekaptein:** Mbeumo.

**Benk i rekkefølge:** Steele, Thiago, van Ewijk, Kusi-Asare (reservekeeper først; deretter tre utespillere). Modellen regner ikke automatiske innbytter eller kapteinsfallback; forventningene inkluderer redusert spilletid, men benkedekning er ikke lagt oppå startelleveren. Bench Boost teller alle 15 fullt etter spillerens forventning.

## Budsjettkontroll og konkrete bytter

Likviditetskontroll for R8: £1,0 + salgsinntekter − kjøp = bank. Ingen salgsgevinst fra beholdte spillere brukes som ekstra penger.

| Alternativ | Ut | Inn | Salg | Kjøp | Bank | Trekk |
|---|---|---|---:|---:|---:|---:|
| A | – | – | 0.0 | 0.0 | 1.0 | 0 |
| B | Szoboszlai | Tavernier | 6.8 | 6.2 | 1.6 | 0 |
| C | Thiago, Szoboszlai | Tavernier, Calvert-Lewin | 14.6 | 12.3 | 3.3 | 0 |
| D3 | Verbruggen, van Ewijk, Szoboszlai | Tavernier, De Cuyper, Tzolakis | 15.2 | 16.2 | 0.0 | 4 |
| D4 | Thiago, Verbruggen, van Ewijk, Szoboszlai | Tavernier, De Cuyper, Calvert-Lewin, Tzolakis | 23.0 | 22.3 | 1.7 | 8 |
| D5 | Konsa, Thiago, Verbruggen, van Ewijk, Szoboszlai | Tavernier, De Cuyper, Bogle, Calvert-Lewin, Tzolakis | 27.5 | 27.0 | 1.5 | 12 |
| E | Konsa, Thiago, Verbruggen, van Ewijk, Kusi-Asare, Szoboszlai, Maguire, N.Williams, E.Le Fée | Tavernier, De Cuyper, Thomas, Tarkowski, Barry, Iwobi, Bogle, Calvert-Lewin, Tzolakis | 47.4 | 48.3 | 0.1 | 0 |
| E19 | Konsa, Thiago, Verbruggen, Steele, van Ewijk, Kusi-Asare, Szoboszlai, Maguire, B.Fernandes, N.Williams, E.Le Fée | Raya, Ødegaard, Tavernier, De Cuyper, Hughes, Barry, Bogle, Isak, Guéhi, Vuskovic, Tzolakis | 63.2 | 63.9 | 0.3 | 0 |
| F | Szoboszlai | Tavernier | 6.8 | 6.2 | 1.6 | 0 |
| G_BB | Szoboszlai | Tavernier | 6.8 | 6.2 | 1.6 | 0 |
| G_FH | Szoboszlai | Tavernier | 6.8 | 6.2 | 1.6 | 0 |

F: WC i R9. Ut fra B-troppen: Konsa, Thiago, Verbruggen, Steele, van Ewijk, Kusi-Asare, Maguire, B.Fernandes, N.Williams, E.Le Fée. Inn: Raya, Ødegaard, De Cuyper, Hughes, Tarkowski, Barry, Bogle, Isak, Vuskovic, Tzolakis. Bank etter WC: £0.1m.

Alle tropper gjennomgår assertions for klubbgrense, posisjoner og salgsverdibudsjett. `detaljer.json` inneholder ID-er og ukepoeng for hele planene. `chip_tidspunkt.csv` viser også de midlertidige FH-troppene. Priser kan endres før fristen; modellen må da kjøres med oppdaterte godkjente data.

## Chips og fleksibilitet til R19

På B-troppen gir BB mest i R8: 6.6 merpoeng; FH mest i R12: 9.5. Dette er betinget av at B-troppen beholdes, og ingen fremtidige blanke/doble runder. Lite BB-utbytte skyldes blant annet reservekeeper og en spiss uten registrerte minutter.

For hver permanent plan viser alternativer.csv også beste funne kombinasjon av BB og FH før R20, på ulike runder og uten kollisjon med wildcard. Dette er en **oppnåelig ekstra chipverdi blant undersøkte tropper**, ikke noe som skal legges på G-radene som allerede bruker chipen. FH-kandidatene søkes med opprinnelig eierskap, men budsjettet kontrolleres på nytt for faktisk eierskap hver runde. Ugyldige kandidater får null FH-merverdi (bruk ordinær tropp); derfor kan bedre gyldige FH-tropper være oversett. FH i R8 er utelukket når planen har permanente R8-bytter. Samlet chipoptimering kan gi andre tropper og datoer.

| Permanent plan | BB+FH anslag | BB-runde | FH-runde |
|---|---:|---:|---:|
| A | 15.1 | 15 | 12 |
| B | 16.1 | 8 | 12 |
| C | 15.0 | 8 | 13 |
| E | 16.3 | 10 | 19 |
| E19 | 15.1 | 10 | 12 |
| F | 15.0 | 14 | 12 |

F er den konkrete senere wildcardplanen med høyest R8–19-sum i det søkte settet. Alle datoer R9–19 finnes i wildcard_tidspunkt.csv. Forskjeller på få poeng mellom tidlige wildcarddatoer er for små til å overstyre nye lagnyheter. Behold muligheten til å vente; ikke bind deg til en ubetinget WC-dato. BB etter WC bør planlegges når begge keepere og benken faktisk spiller; en ny søking for BB kan kreve en annen wildcardtropp. Modellen har ikke optimert dette samlet.

Gratisbytter: A gir tre i R9; B gir to; C og D gir én, forutsatt ett nytt gratisbytte per runde og maks fem. Til R15 er alle statiske planer ved taket, og det illustrerer hvorfor det er urimelig å behandle dem som sesongoptimum. En ekstra FT har ingen fast poengverdi: den er verdiløs uten et ønsket bytte, men kan spare et trekk på fire poeng når behovet kommer. Bruk 0–4 poeng som beslutningsscenario for én ekstra FT, ikke som estimert forventning eller absolutt tak. A vs B må også veies mot at B fjerner en kjent nullspiller. FT-bevaring ved WC/FH er ikke uttrykkelig dokumentert i de frosne regelfeltene; repoets automatiske reset til én kan ikke bekreftes fra dette datagrunnlaget. Ingen poeng er kreditert på grunnlag av den regelen.

WC1/FH1/BB1 har ingen ubrukt terminalverdi etter R19: de utløper. Men troppen og bank/lagrede bytter påvirker R20 og videre. Nytt chipsett i andre halvdel gjør det heller ikke riktig å spare første sett forbi fristen. R19 er derfor en nyttig planleggingsgrense, ikke sesongslutt. Det mangler en adaptiv sesongsimulering, prisprognose og verdi av fremtidig informasjon; ikke tolk R8–15-summen som målet for resten av sesongen.

## Kontroll av repoets plan.json

Enig i å undersøke wildcard: flere benkespillere har svak spilletid, Szoboszlai er ute, og forbedringspotensialet er synlig også her. Uenig i at det foreliggende resultatet er tilstrekkelig grunnlag for å aktivere chipen:

- `src/optimize.py` bruker samme nåpris ved kjøp og salg. De ti R8-salgene i plan.json gir £58,8m etter salgsprisene; innkjøpene koster £60,7m i frosne bootstrap. Med £1,0m bank mangler **£0,9m**. Selv salg til nåpris (£59,1m) gir et underskudd på £0,6m mot disse dataene. Planen ser derfor også ut til å bruke andre pris-/bankinnganger enn det fryste grunnlaget.
- Start-FT er hardkodet til én, mens faktisk utgangspunkt er to. WC-reset til én er også hardkodet; dette er ikke verifisert i de tilgjengelige API-reglene.
- `HORIZON = 5` gir R8–12. Spillerpoengfilen omfatter R8–13, ikke R8–15 eller R19. Slutt-BB kan derfor få kunstig stor verdi uten å prise etterfølgende troppsbehov.
- Maks tre spillere per klubb og lovlige formasjoner er korrekt inkludert i optimizeren. Wildcard og BB hindres fra samme runde. FH er ikke modellert.
- Målfunksjonen inkluderer 15 % av all benk, ekstra fire poeng straff per hit og byttefriksjon. `objective=362.55` er derfor ikke rene forventede FPL-poeng og kan ikke sammenlignes direkte med tabellen her.
- `expected_points.py` har keepermål hardkodet til 6. Minuttmodellen håndterer skadeflagg og innhopp, men bruker samme minutter over horisonten, generisk P(60+|start) og forsøker å hente fjorårsdata over nett. Dette kan ikke reproduseres fra bare det frosne datagrunnlaget. Det er ikke belegg for at dens tall er kontrollert.

## Viktigste begrensninger og neste kontroll

Bare 15 element-summary-filer finnes, så nylig form, starter, DC-treff og pris-/rollehistorikk kan ikke kontrolleres tilsvarende for innspillere. Det mangler skadekomback, forventede rotasjoner, startoppstillinger og dokumentert fremtidig terminendring. API summer er data; hjemmefaktorer, ratekrymping, minuttmodell og skadevarighet er antakelser; tabellpoengene er modellresultater.

Navn som Tzolakis, De Cuyper og Tavernier må rollevalideres av Claude. Aggregert DC og kort historikk kan overvurdere dem. Ved store spilletidsoverstyringer skal alle alternativene kjøres på nytt. Skadefrisk Szoboszlai fra for eksempel R10 og reduserte minutter for innkandidatene er de viktigste neste scenarioene. Stressbåndene over erstatter ikke disse spesifikke scenariotestene.

## Reproduksjon og kontroll

Kjør fra repoets rot:

```sh
/Users/simenflogstad/opt/anaconda3/bin/python3 samarbeid/gw08/codex/modell.py
```

Bruk eksisterende Python med numpy (systemets python3 har ikke numpy). Ingen pakker installeres og ingen nettforespørsler utføres. Skriptet skriver bare i codex/, bevarer minutter_antatt.csv og gjenskaper CSV, JSON, denne analysen og modellpoeng. Søk har fast rekkefølge og ingen tilfeldig trekning. Summer i analysen genereres direkte fra samme resultatobjekter som alternativer.csv; lovlighet og budsjett kontrolleres under kjøring. A–G er representert, med D3/D4/D5 og G_BB/G_FH som egne rader.

**Oppdraget er ikke løst som et bevist globalt flerperiode-/sesongoptimum.** Leveransen er en kjørbar, etterprøvbar grunnmodell med konkrete lovlige alternativer og tydelige forbehold om søk og fremtidige handlinger.

## Supplerende kontroller og følsomhet

Poengreglene er rekonstruert på alle 105 tilgjengelige historiske spillerkamper: **null avvik**. Dette støtter DC-tersklene 10/12, redningstripler og innslupne par i dette utvalget. Keepermål er ikke observert; verdien 10 kommer direkte fra API-et. Resultatet står i kontrollresultat.json.

Når wildcard begge steder velges for R19, gir E19 713.5 mot F 709.3 poeng til R19: WC nå leder med 4.2. Anbefalingen om å vente én runde er derfor et skjønn om verdien av ny informasjon og å unngå en stor omlegging på svakt datagrunnlag; den følger ikke direkte av høyeste modellpoeng. En forskjell på 4.2 er liten i forhold til rolleusikkerheten. Hvis Claude bekrefter hele den foreslåtte nye troppens roller og fravær, støtter modellen WC nå.

En paret rollestress-test reduserer bare Taverniers poeng, lar dagens spillere være uendret og velger elleveren på nytt. Dette er lineær poengstress, ikke en ny full minuttmodell eller et comebackscenario for Szoboszlai.

| Tavernier poengfaktor | B minus A til R15 |
|---|---:|
| 100% | 16.7 |
| 75% | 6.7 |
| 50% | 0.0 |
| 0% | 0.0 |

`folsomhet.csv` gjenskapes automatisk av modell.py. Den gir en mer relevant robusthetskontroll på enkeltbyttet enn bare overlappende totalbånd.
