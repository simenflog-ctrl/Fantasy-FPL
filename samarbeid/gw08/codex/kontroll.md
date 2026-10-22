# Kontroll og revisjon – runde 1

**Svak anbefaling R8: WC nå, med den felles testede troppen under.**

Jeg godtar at første rundes sammenligning var skjev. Alle hovedplanene her bruker samme fremtidige byttepolitikk, gyldig kjøpsunivers, reelle salgspriser og både BB og FH før R20. Tidligere filer er beholdt.

## Konklusjon om wildcard

Under hvert poengsetts egen optimerte politikk slår WC R8 beste undersøkte senere wildcard med **8.3 poeng** i forbedret Codex-modell og **4.0 poeng** i repo-hybrid. Beste sene runder er henholdsvis R11 og R11. Dette er en langt mer relevant test enn de gamle statiske troppene.

**WC nå består den snevre testen «høyere under begge hovedpoengsett med samme bytteregel».** Det betyr ikke automatisk at ett bestemt wildcardlag er robust: de to poengsettene velger forskjellige spillere. Derfor har jeg også testet samme kompromissplan, alternativ hale etter R13 og et betinget comeback fra R11.

Den beste fellesplanen blant Codex-, repo- og 50/50-bane gir 696.4 / 767.9 når de identiske troppene og chipdatoene vurderes med de to hovedpoengsettene (ellever/kaptein velges på nytt). Mot hver modells beste senere WC er marginene **+1.1 / +4.0**. Med repoets seksrunderssnitt gjentatt i R14–19 er fordelen ved WC nå **+9.9**. Ved frisk Szoboszlai fra R11 er tilsvarende marginer mot de respektive hovedløpenes beste sene datoer **+8.3 / +4.0**.

Disse testene peker alle mot WC nå. Det er modellrobust etter oppgavens kriterium innenfor dette undersøkte settet, men bare svakt: omtrent ett poeng for en felles konkret bane er mindre enn plausibel feil i én spillerrolle. Jeg endrer derfor anbefalingen fra hold til WC på forventning, uten å hevde at en liten rolleendring ikke kan snu den. Ingen av de testede hale-, FT- eller comebackantakelsene snur hovedsammenligningen; det er ingen garanti eller global optimalitetsattest.

## 1. Svar på hver innvending fra Claude

**1 – undervurderte toppspillere: godtar metodekritikken, men avviser å kalibrere direkte til observert snitt.** Individuelle xG/xA-priorer fra de to siste tilgjengelige sesongene erstatter posisjonssnittet der historikk finnes. Seneste sesong har dobbelt vekt av den foregående; prioren veier 540 minutter, og øvrige spillere får 270 minutter posisjonsprior. Samme prior brukes for bonus/kort/straffehendelser når feltet finnes. Lagstyrke bruker nå xG/xGA, ikke mål. Noen eliteverdier øker, andre faller – det er ikke riktig å tvinge alle mot repoets tall eller siste sju runders poeng.

| Spiller | Før, per runde R8–13 | Ny, per runde R8–13 | Repo | Observert R1–7 | Ny xG90 / xA90 |
|---|---:|---:|---:|---:|---|
| Haaland | 5.7 | 6.1 | 8.4 | 8.3 | 0.80 / 0.10 |
| B.Fernandes | 4.4 | 4.8 | 7.3 | 4.7 | 0.35 / 0.26 |
| Mbeumo | 5.1 | 5.3 | 5.5 | 5.9 | 0.48 / 0.16 |
| Rogers | 4.4 | 4.1 | 5.6 | 5.7 | 0.25 / 0.17 |
| Thiago | 3.3 | 3.6 | 4.1 | 2.6 | 0.55 / 0.06 |
| Tavernier | 5.1 | 4.7 | 5.2 | 6.0 | 0.37 / 0.17 |

Haaland: repoet gir omtrent 2.8 bonuspoeng per kamp i R8–13; den nye historikkbaserte bonusraten gir omtrent 1.4 ved R8-minuttene. Det er en vesentlig del av modellgapet. Poengsnittet over sju kamper er ikke en fasit for neste kamp; sammenligningen over er en nivåkontroll, ikke en ut-av-utvalg-kalibrering.

B.Fernandes: repoet gir omtrent 2.1 bonuspoeng per kamp i R8–13; den nye historikkbaserte bonusraten gir omtrent 0.7 ved R8-minuttene. Det er en vesentlig del av modellgapet. Poengsnittet over sju kamper er ikke en fasit for neste kamp; sammenligningen over er en nivåkontroll, ikke en ut-av-utvalg-kalibrering.

**2 – modellavhengig wildcardfordel: godtar og tester.** Hovedtabellen under gjentar hele planleggingen med begge poengsett; den låner ikke bare score til gamle wildcardtropper. Krysskolonnene viser også hvert ferdige forløp under den andre modellen, med ny beste lovlige ellever. Codex-planenes salg av Fernandes var modellfølsomt; de nye hoved-WC-troppene beholder ham ved R8. Eventuelle senere salg er synlige i loggen.

**3 – skjevt wildcardtidspunkt: godtar fullt ut, rettet.** B gjør Szoboszlai → Tavernier i R8. Alle varianter bruker deretter samme grådige fire-runders politikk med rulling og maks fem FT. WC-rundene er R8, R11, R13, R15 og R17. Ingen variant pålegges å holde dagens tropp urørt. Den gamle marginen 4,2 trekkes tilbake som beslutningsgrunnlag.

**4 – ugyldige/ubrukelige spillere: godtar, rettet.** Kjøp krever can_select, status uten u/n/i/s, ikke 0 %, og p_start minst 0,50. Dette gjelder alle 15 i nye WC/FH-tropper, også andrekeeperen. Dennis og begge Hughes er utelukket og kontrolleres med assertion. Eksisterende Steele/Kusi-Asare kan beholdes frem til de faktisk selges; dette er ikke nye kjøp. En skadeflagget spiller blir ikke frisk fordi han har historisk rate. Comebacktesten gjør ett eksplisitt, datert unntak for Szoboszlai fra R11.

**5 – Thiago/Maguire og vice: testes; Claude får støtte for elleveren.** Den forbedrede modellen og repoet velger Thiago fremfor Maguire i R8 etter B. Tabellen for følsomhet viser forskjellen mellom beste lovlige lag med Thiago uten Maguire og omvendt. Bruno velges som vice i den operative anbefalingen, fordi han har sikker rolle og høy forventning i repoet. Min modell alene kan foretrekke Mbeumo; siden vice bare teller ved fravær for Haaland er denne uenigheten liten og ikke grunnlag for et bytte.

**6 – rollevalidering av E: godtar som belegg for den gamle E-troppen, ikke som automatisk godkjenning av nye navn.** Den nye E-troppen er funnet på nytt og inneholder enkelte andre spillere; disse trenger Claudes nyhetskontroll. CSV-en med minutter gjør modellrollene etterprøvbare. Et historisk p_start over 0,50 er et minimumsfilter, ikke en pressekonferanse.

## 2. Hovedsammenligning R8–19

Alle tall inkluderer kaptein, faktiske BB-poeng i forventning, midlertidig FH-tropp og eventuelle trekk. Ingen prosentandel av benken legges til ordinære poeng. Søkets wildcardmål har en liten benkbonus for å støtte senere BB, men den rapporteres ikke som FPL-poeng. Poengforskjeller på få poeng er ikke statistisk signifikante funn.

| Poengsett | WC | BB / FH | R8 | R8–13 | R8–19 | E minus plan | Trekk | Kryss Codex / repo |
|---|---:|---|---:|---:|---:|---:|---:|---|
| codex | 8 | 19 / 13 | 55.3 | 340.8 | 703.6 | +0.0 | 0 | 703.6 / 751.4 |
| codex | 11 | 19 / 9 | 52.3 | 334.2 | 695.3 | +8.3 | 0 | 695.3 / 752.2 |
| codex | 13 | 15 / 16 | 52.3 | 332.0 | 692.2 | +11.4 | 0 | 692.2 / 756.5 |
| codex | 15 | 17 / 9 | 52.3 | 332.8 | 693.2 | +10.4 | 0 | 693.2 / 758.4 |
| codex | 17 | 19 / 9 | 52.3 | 332.8 | 693.2 | +10.4 | 0 | 693.2 / 758.4 |
| repo_hybrid | 8 | 17 / 13 | 65.8 | 406.2 | 767.9 | +0.0 | 0 | 696.4 / 767.9 |
| repo_hybrid | 11 | 15 / 9 | 64.0 | 403.3 | 763.9 | +4.0 | 0 | 691.1 / 763.9 |
| repo_hybrid | 13 | 17 / 9 | 64.0 | 400.8 | 761.5 | +6.4 | 0 | 685.5 / 761.5 |
| repo_hybrid | 15 | 17 / 9 | 64.0 | 402.3 | 760.1 | +7.8 | 0 | 682.9 / 760.1 |
| repo_hybrid | 17 | 19 / 9 | 64.0 | 403.3 | 762.4 | +5.5 | 0 | 686.2 / 762.4 |

Poengsett (a) er ny Codex-modell R8–19. (b) bruker repoets faktiske spiller-xP i R8–13 og **Codex R14–19**. Der repoet mangler spiller/runde brukes Codex; dekningen lagres i kontrollresultat_r2.json. Uaktuelle/skadde spillere settes til null i begge. Dermed er (b) et hybridscenario, ikke tolv runder uavhengige repo-prognoser. Den tredje testen gjentar hver spillers repo-snitt fra R8–13 gjennom R14–19 i stedet; detaljene står i wildcard_tidspunkt_r2.csv.

### Samme politikk og penger

Fra R9 evalueres alle lovlige enkeltbytter i en posisjonspool på inntil 16 beste etter neste fire runder, sju billigste og beholdte kandidater. Vinduet stoppes før neste planlagte WC; en planlagt FH-runde utelates, og benkepoeng legges til hvis BB ligger i vinduet. Gratisbytte tas ved over ett forventet poeng gevinst over disse rundene. Ved fem FT eller i R19 brukes terskel null, fordi videre lagringsverdi er liten innen horisonten. Lagrede FT kan brukes flere samme runde; ett nytt opptjenes etter ordinære runder, maks fem. Ett betalt ekstrabytte er bare tillatt ved over fem bruttopoeng i de neste fire rundene, altså mer enn fire som krevd. Alle gjennomførte gevinster og terskelutløsere logges. Dette er en felles grådig politikk, ikke et perfekt adaptivt sesongoptimum.

WC/FH har samme kjøpsfilter og søk: deterministisk beam med bredde tre, billig gyldig tropp, reparert eksisterende tropp og eventuelt gyldig eksisterende tropp som startpunkter. WC velges for gjenstående runder til R19; FH for én runde. To lovende BB/FH-datopar velges fra et første forløp og spilles deretter gjennom på nytt med reell gjenoppretting av troppen etter FH. FH gir ingen permanent byttegevinst eller lånt ekstra bank. BB og FH kolliderer aldri med WC eller hverandre. Chipdatoene er beste funn blant disse søkte parene, ikke globalt optimale datoer.

FT ved WC/FH er ikke spesifisert i lokale API-felter. Hovedantakelsen er bevaring av antallet ved chipbruk, uten nytt FT i selve chiprunden; E starter dermed med to videreførte. Jeg oppgir ikke dette som verifisert 2026/27-regel. To alternative bokføringer – bevaring pluss ett, og reset til ett – er testet på samme valgte chipdatoer. FT_regler_r2.csv viser alle resultatene. Denne usikkerheten skjules ikke som en hardkodet regel.

Budsjettet starter med £1,0m bank. Ved hvert faktisk salg brukes spillerens eide salgspris; beholdte opprinnelige spillere beholder denne, nye kjøpes/selges til frossen nåpris. Ved gjenkjøp av en tidligere solgt spiller brukes nåpris, ikke gammel salgspris. Alle WC/FH-tropper og alle ukentlige bytter kontrolleres for posisjoner, maks tre per klubb og ikke-negativ bank. Ingen prisendringer er simulert.

| Plan | Bank etter R8 | Bank etter R19 | FT til R20 |
|---|---:|---:|---:|
| codex WC8 | 0.4 | 0.1 | 3 |
| codex WC11 | 1.6 | 0.1 | 2 |
| codex WC13 | 1.6 | 0.0 | 3 |
| codex WC15 | 1.6 | 0.2 | 4 |
| codex WC17 | 1.6 | 0.0 | 3 |
| repo_hybrid WC8 | 0.1 | 0.6 | 3 |
| repo_hybrid WC11 | 1.6 | 0.2 | 4 |
| repo_hybrid WC13 | 1.6 | 0.2 | 4 |
| repo_hybrid WC15 | 1.6 | 0.2 | 4 |
| repo_hybrid WC17 | 1.6 | 0.0 | 2 |

WC1, FH1 og BB1 er brukt før utløp i alle hovedalternativer. Terminalverdien av ubrukte chips er derfor ikke skjult i sammenligningen. FT, bank og tropp har fortsatt verdi fra R20. Modellen stopper R19 og kan følgelig favorisere små sene bytter uten å prise R20+. Den verdsetter ikke ny informasjon, fremtidige skader eller endret cup-/ligaprogram. Det er en felles begrensning, ikke en dokumentert poengverdi for å vente.

## 3. Følsomhet for R8

Her holdes troppen etter R8-byttet fast for å isolere spiller-/ellevervalget. Det er **ikke** hovedsammenligningen, som bruker fremtidige bytter. Separate full-policy-tester står under.

| Poengsett | Scenario | R8 | R8–13 | R8–19 | Thiago minus Maguire R8 | B minus behold til R19 |
|---|---|---:|---:|---:|---:|---:|
| codex | Tavernier | 52.3 | 315.5 | 639.2 | 0.53 |  |
| codex | Dewsbury-Hall | 51.3 | 309.7 | 627.6 | 0.53 |  |
| codex | Tavernier .75 start / 70 min gitt start (52.5 forventet) | 51.2 | 308.2 | 624.5 |  |  |
| codex | Szoboszlai frisk fra R11: behold / B-fordel | 50.9 | 306.9 | 622.4 |  | 16.83 |
| repo_hybrid | Tavernier | 64.0 | 385.1 | 708.9 | 1.14 |  |
| repo_hybrid | Dewsbury-Hall | 63.1 | 383.4 | 701.4 | 1.14 |  |
| repo_hybrid | Tavernier .75 start / 70 min gitt start (52.5 forventet) | 62.8 | 376.9 | 693.3 |  |  |
| repo_hybrid | Szoboszlai frisk fra R11: behold / B-fordel | 62.2 | 373.2 | 688.7 |  | 20.17 |

Taverniers belastningsscenario tolker 70 minutter som **gitt start**: p_start 0,75, forventede minutter 52,5 og p_60 0,7125. Å sette p_play 0,75 sammen med ubetingede 70 minutter ville være umulig, siden maksimum da er 67,5. For repo-xP skaleres Tavernier med forholdet mellom ny og opprinnelig Codex-prognose i stedet for å late som repoets rateledd er kjent. Dette er et rolletapscenario, ikke en skadeprognose.

Szoboszlai fra R11 er et bevisst optimistisk motstykke til null hele perioden. Det står i konflikt med Claudes sentrale vurdering om ute minst til og med R11, og er derfor en stresstest, ikke nytt skadebelegg. Frisk rate og spilletid estimeres fra egne historiske starter; ingen faktisk returdato antas. I full-policy-testene blir han kjøpbar først fra R11. Senere WC-dato holdes lik den beste fra hovedløpet, mens samme bytteregel og chipsøking kjøres på nytt.

| Full politikk, frisk R11 | WC | R8–19 | BB / FH |
|---|---:|---:|---|
| codex_retur | 8 | 703.6 | 19 / 13 |
| codex_retur | 11 | 695.3 | 19 / 9 |
| repo_hybrid_retur | 8 | 767.9 | 17 / 13 |
| repo_hybrid_retur | 11 | 763.9 | 15 / 9 |

| Full politikk, samme chipdatoer | WC | R8-kjøp | R8–19 |
|---|---:|---|---:|
| codex | 11 | Tavernier | 695.3 |
| codex | 11 | Dewsbury-Hall | 690.5 |
| repo_hybrid | 11 | Tavernier | 763.9 |
| repo_hybrid | 11 | Dewsbury-Hall | 761.8 |

## 4. Konkret kritikk av Claudes forslag

- **Godt nok:** Szoboszlai ut nå; bruk salgspris; unngå et uberegnet trekk; Thiago foran Maguire i R8; Tavernier og Dewsbury-Hall vurderes som rolleavhengig valg. Thiagos lave poeng er ikke i seg selv salgsgrunn når xG og minutter er sterke. Forslaget oppgir også egne databegrensninger tydelig.
- **Manglet:** tallfestet WC-dato, BB/FH-plan, reelle fremtidige bytter og verdi av å bygge en spillende andrekeeper/benk før BB. Dette er nå regnet under én felles politikk. Vindusforslaget R12–15 var en hypotese, ikke et dokumentert optimum.
- **For sterkt formulert:** «byttet er positivt i alle scenarioer» er ikke en universell robusthetsgaranti når Taverniers minutter kan svikte og Szoboszlai kan komme tilbake. Det må avgrenses til de faktisk testede scenarioene. Belastningstesten over kan favorisere DH.
- **Feil generell påstand:** Fernandes ×0,7 trekker ikke alle planer like mye ned. Det gjelder bare dersom samme spiller beholdes, starter og har samme kapteinsrolle. Når WC kan selge ham, velge en annen kaptein eller finansiere andre posisjoner, kan rangeringen endres. Claudes egen krysskontroll viser nettopp dette.
- **Ikke et tallfestet FT-estimat:** «ett bytte er verdt 3–4 poeng i én runde» er et mulig behovsscenario, ikke forventet verdi av å rulle. Her prises rulling gjennom faktiske senere handlinger. En skade før neste runde er ikke modellert og kan gi ytterligere informasjonsverdi.
- **FH til en eventuell blank:** rimelig beredskap, men lokale data har ingen blank. Å vente på en hendelse utenfor datagrunnlaget er ikke i seg selv en beregnet fordel. Alle planene bruker FH før den utløper også uten blank.

## 5. Anbefalt handling og kontrollerbar tropp R8

**Svak anbefaling R8: WC nå, med den felles testede troppen under.**

**Startellever:** Tzolakis (HUL, 572), Calafiori (ARS, 8), Thomas (COV, 173), De Cuyper (BHA, 115), B.Fernandes (MUN, 426), Mbeumo (MUN, 427), Tavernier (BOU, 68), E.Le Fée (SUN, 542), Groß (BHA, 124), Haaland (MCI, 411), João Pedro (CHE, 165).

**Kaptein:** Haaland (MCI, 411). **Visekaptein:** B.Fernandes (MUN, 426).

**Benk:** Verbruggen (BHA, 109), Silva (BOU, 566), Dasilva (COV, 176), Thomas-Asante (COV, 194). Reservekeeper står først; utespillerne deretter i innbytterekkefølge. **Bank:** £0.1m.

WC ut: Konsa (ARS, 31), Thiago (BRE, 106), Steele (BHA, 111), van Ewijk (COV, 175), Kusi-Asare (FUL, 272), Szoboszlai (LIV, 368), Maguire (MUN, 418), N.Williams (NFO, 469).

WC inn: Tavernier (BOU, 68), De Cuyper (BHA, 115), João Pedro (CHE, 165), Thomas (COV, 173), Dasilva (COV, 176), Thomas-Asante (COV, 194), Silva (BOU, 566), Tzolakis (HUL, 572).

Budsjett: £1,0m + salg £41.2m − kjøp £42.1m = bank £0.1m.

Planlagt BB R17, FH R13; disse datoene er betinget av kjente roller og uendret program, og bør revurderes ukentlig.

### Nye wildcardtropper, til Claudes rollekontroll

| Modellvalg R8 | Tropp | Bank |
|---|---|---:|
| codex | Calafiori (ARS, 8), Tavernier (BOU, 68), De Cuyper (BHA, 115), Groß (BHA, 124), Thomas (COV, 173), Rudoni (COV, 183), Barry (EVE, 249), Calvert-Lewin (LEE, 346), Trafford (LEE, 385), Haaland (MCI, 411), B.Fernandes (MUN, 426), Mbeumo (MUN, 427), Vuskovic (BHA, 504), Silva (BOU, 566), Tzolakis (HUL, 572) | 0.4 |
| repo_hybrid | Calafiori (ARS, 8), Tavernier (BOU, 68), Verbruggen (BHA, 109), De Cuyper (BHA, 115), Groß (BHA, 124), João Pedro (CHE, 165), Thomas (COV, 173), Dasilva (COV, 176), Thomas-Asante (COV, 194), Haaland (MCI, 411), B.Fernandes (MUN, 426), Mbeumo (MUN, 427), E.Le Fée (SUN, 542), Silva (BOU, 566), Tzolakis (HUL, 572) | 0.1 |
| blend | Calafiori (ARS, 8), Tavernier (BOU, 68), De Cuyper (BHA, 115), Groß (BHA, 124), Thomas (COV, 173), Barry (EVE, 249), Bogle (LEE, 330), Calvert-Lewin (LEE, 346), Trafford (LEE, 385), Haaland (MCI, 411), B.Fernandes (MUN, 426), Mbeumo (MUN, 427), E.Le Fée (SUN, 542), Silva (BOU, 566), Tzolakis (HUL, 572) | 0.0 |

Fellesplanen står i felles_valgt_E_r2.json. Blant de tre ferdige banene fra Codex, repo-hybrid og 50/50-blanding velges banen med høyest laveste margin mot de to hovedmodellenes beste sene WC. Det er et lite maximin-søk, ikke en bevist robust optimal tropp. Blend-banen bevares separat i felles_E_r2.json. Kryssvurdering velger ellever på nytt, men endrer ikke de fremtidige byttene; dette er én implementerbar troppsbane under to vurderinger, ikke en uavhengig tredje prognose.

## 6. Etterprøvbarhet og gjenværende svakheter

Verifiserte data: 222 element-summary-filer; bootstrap-spillere/status/priser; lokal historikk for R1–7; tidligere sesongers xG/xA/minutter der feltene finnes; spillereglenes poengvekter; frosne kamper til R19. player_matches summeres og kontrolleres mot bootstrap for **alle 668 spilleres minutter og xG**, uten avvik. Lag-xGA tas fra motstanderens summerte xG i kampen; man summerer aldri individuelle overlappende xGA. Det lokale historikkgrunnlaget er dermed tilstrekkelig for xG-lagstyrke.

Antakelser: sju kamper krymping i lagstyrke; hjemme/borte 1,1/0,9; 540/270 min prior; historisk p_start og minutter uten nye pressekonferanser; fire-runders byttevindu; ett poeng terskel for FT-bruk; benkbonus 0,35 × største forventede benkepoeng i WC-søket; FT-regel ved chip; ingen prisendringer; ingen nye blanke/doble. Empirisk DC-treff fra de 222 historikkene erstatter den gamle grove DC-haleformelen. Data om tidligere bonus er observert i et annet sesongregime og kan også ha strukturell skjevhet.

Modellresultater er tabellene, ikke verifiserte fotballfakta. Lavere feil mot observert snitt i sju runder er ingen dokumentasjon på bedre fremtidsprognose. Modellen er ikke backtestet med de nye priorene. Den korrigerer heller ikke historiske spiller-xG for motstand før den projiserer nye kamper. Det er usikkerhet både i nivå og relative spillerverdier.

Automatiske innbytter og kapteinsfallback er ikke simulert. Dette undervurderer en fungerende benk i ordinære runder og kan påvirke marginer på få poeng; alle WC/FH-benker har likevel minst 50 % startsjanse. Poengintervaller fra runde 1 var stressbånd, ikke konfidensintervaller. Her bruker jeg **spredningen mellom poengsett, fellesplan, hale- og comebackscenario** som beslutningsusikkerhet; ingen statistisk sikkerhetsprosent er beregnet. Lokale søk kan overse finansieringskombinasjoner. Ingen av disse resultatene er et bevist globalt optimum.

Kjør fra repoets rot:

```sh
/Users/simenflogstad/opt/anaconda3/bin/python3 samarbeid/gw08/codex/modell_r2.py
```

Ingen installasjon eller nett. modell_r2.py leser gamle spillerpoeng bare for før-kolonnen, bevarer minutter_antatt_r2.csv som overstyringsinput, genererer alle *_r2-resultatene og bruker rapport_r2.py til denne teksten. Alle poengtall her kommer fra resultatobjektene i den samme kjøringen. Fullstendige ukentlige kjøp/salg, salgspriser, bank, FT og chips ligger i planer_r2.json; JSON-logs inneholder begrunnelsen i fire-rundersgevinst per bytte. Forrige runde er ikke overskrevet.

### Samme E-bane vurdert med begge poengsett

| Bane valgt med | Codex-poeng / margin mot senere WC | Repo-poeng / margin mot senere WC |
|---|---|---|
| codex | 703.6 / +8.3 | 751.4 / -12.5 |
| repo_hybrid | 696.4 / +1.1 | 767.9 / +4.0 |
| blend | 701.4 / +6.1 | 760.2 / -3.7 |

### FT-regel ved chip: E minus beste sene dato fra hovedløpet

| Poengsett | Bevaring | Bevaring + ett | Reset til ett |
|---|---:|---:|---:|
| codex | +8.3 | +8.1 | +12.0 |
| repo_hybrid | +4.0 | +4.3 | +4.7 |
