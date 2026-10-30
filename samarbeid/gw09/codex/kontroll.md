# Kontroll R9, runde 2

**Anbefaling: E; WC i R9.**
R9 ut: Calafiori, Konsa, Thiago, Verbruggen, Steele, van Ewijk, Kusi-Asare, Maguire, B.Fernandes, N.Williams, E.Le Fée. Inn: Gabriel, Ødegaard, De Cuyper, Thomas, Rudoni, Barry, Muharemović, Isak, Trafford, Silva, Tzolakis. Bank £0.4m; trekk 0. BB19/FH16 i alle hovedbaner.

**Ellever (3–4–3):** Tzolakis (572), Gabriel (4), Thomas (173), Silva (566), Ødegaard (15), Tavernier (68), Rudoni (183), Mbeumo (427), Barry (249), Isak (379), Haaland (411).
**Kaptein:** Haaland (411). **Visekaptein:** Mbeumo (427).
**Benk:** Trafford (385), Groß (124), De Cuyper (115), Muharemović (334) (keeper først, deretter utespillere i prioritert rekkefølge).

Anbefalingen følger høyest beregnet gjennomsnittsforventning ved skaderate 2 % per frisk spiller/runde, med lik vekt på codex og repo_hybrid. Skaderatene er antatte stressnivåer, ikke estimerte faktiske skaderater. Tallene nedenfor viser hvor mye konklusjonen avhenger av modellen. Ingen FPL-handlinger er utført.

## 1. Autobytter og revidert rangering

Poengfilen inneholder spillerens ubetingede xP. Autobytter legges til på lagnivå. Jeg summerer over sannsynlighetene for antall fravær per posisjon og samtlige åtte spilleutfall for utespillerbenken. Første lovlige benkespiller prioriteres; nominel formasjon etter erstatning må fortsatt ha minst 3 forsvarere, 2 midtbanespillere og 1 spiss. Keeper erstattes bare av benkekeeper. Ved 0 minutter for kapteinen overføres ekstrakopien til visekapteinen hvis han spiller. Et kort innhopp blokkerer autobytte.
Dette er eksakt forventningsverdi gitt uavhengige p_play, ikke en simulering av kamppoeng. Uavhengigheten er en antakelse; særlig keeperne fra samme klubb kan være negativt korrelerte. Det oppstår heller ingen automatisk rolleoppgradering av en reserve når en klubbkamerat skades. Fullt elleversøk tester alle lovlige ellevere, benkerekkefølger og kaptein/vice-par. En særskilt test med 100 000 spilleutfall kontrollerer integrasjonen (autokontroll_r2.json).

Først isoleres autobytter på de samme eierbanene som R1, men med Claudes to nye minuttantakelser. Elleveren velges på nytt i begge beregningene:

| Plan fra R1 | Poengsett | R9 uten auto | R9 med auto | Gevinst | R9–19 med auto |
|---|---|---:|---:|---:|---:|
| A | codex | 48.5 | 51.8 | +3.3 | 664.7 |
| A | repo_hybrid | 56.5 | 59.9 | +3.4 | 728.0 |
| C | codex | 51.0 | 54.2 | +3.2 | 669.3 |
| C | repo_hybrid | 59.7 | 63.0 | +3.3 | 733.5 |
| E | codex | 55.3 | 58.4 | +3.1 | 674.9 |
| E | repo_hybrid | 63.8 | 67.0 | +3.1 | 738.7 |
| F_WC10 | codex | 51.0 | 54.2 | +3.2 | 670.8 |
| F_WC10 | repo_hybrid | 59.7 | 63.0 | +3.3 | 734.7 |
| F_WC11 | codex | 51.0 | 54.2 | +3.2 | 669.3 |
| F_WC11 | repo_hybrid | 59.7 | 63.0 | +3.3 | 733.5 |

Oppdatert planvalg med autobytter i byttepolitikken (tall codex/repo):

| Plan | WC | R9-handling | Bank | R9 | R9–12 | R9–16 | R9–19 |
|---|---:|---|---:|---:|---:|---:|---:|
| E | 9 | Calafiori, Konsa, Thiago, Verbruggen, Steele, van Ewijk, Kusi-Asare, Maguire, B.Fernandes, N.Williams, E.Le Fée → Gabriel, Ødegaard, De Cuyper, Thomas, Rudoni, Barry, Muharemović, Isak, Trafford, Silva, Tzolakis | 0.4 | 59.7/66.1 | 242.9/275.0 | 490.6/539.0 | 685.4/733.8 |
| F_WC10 | 10 | Calafiori, Steele → Silva, Tzolakis | 1.7 | 55.5/63.9 | 238.5/273.1 | 485.3/537.8 | 680.1/732.6 |
| F_WC10_samme_C | 10 | Calafiori, Thiago → Gabriel, Barry | 1.7 | 54.2/63.0 | 237.1/272.2 | 484.0/536.8 | 678.8/731.7 |
| C | 11 | Calafiori, Thiago → Gabriel, Barry | 1.7 | 54.2/63.0 | 234.9/271.7 | 481.0/535.6 | 676.8/731.3 |
| F_WC11 | 11 | Calafiori, Thiago → Gabriel, Barry | 1.7 | 54.2/63.0 | 234.9/271.7 | 481.0/535.6 | 676.8/731.3 |
| F_WC11_samme_C | 11 | Calafiori, Thiago → Gabriel, Barry | 1.7 | 54.2/63.0 | 234.9/271.7 | 481.0/535.6 | 676.8/731.3 |
| C_behold_flagg | 11 | Thiago, Maguire → Gabriel, Barry | 0.6 | 54.0/62.8 | 234.8/271.3 | 480.9/535.1 | 676.6/730.9 |
| A | 11 | ingen → ingen | 1.6 | 51.8/59.9 | 231.2/266.8 | 478.1/531.5 | 672.9/726.3 |

A ruller R9, deretter samme løpende byttepolitikk og WC11. C er beste testede kandidat med nøyaktig to R9-bytter og WC11. F_WC10/F_WC11 bruker samme adaptive byttepolitikk som WC9, fra første runde uten WC. Derfor kan R9-handlingen variere når vinduet før WC er ulikt. Radene med «samme_C» isolerer i tillegg WC-datoen med identisk konkret R9-handling. Samme BB19/FH16 og samme policy gjelder gjennomgående.

**De flaggede og Claudes ellever:** R1-C solgte Calafiori; begge kan derfor ikke startes i akkurat den troppen. C_behold_flagg er en ekstra tobyttevariant der begge beholdes. Alle lovlige startkombinasjoner er undersøkt i det fulle elleversøket.
Claudes foreslåtte A-ellever, med Haaland/Tavernier som C/VC og van Ewijk før Maguire på benken, gir 51.7/59.8 i R9. Beste A-ellever gir 51.8/59.9.

| Plan | Valgt R9-ellever | Benk |
|---|---|---|
| A | Verbruggen, Konsa, van Ewijk, N.Williams, Tavernier, Groß, B.Fernandes, Mbeumo, E.Le Fée, Thiago, Haaland | Steele, Calafiori, Maguire, Kusi-Asare |
| C | Verbruggen, Gabriel, Konsa, N.Williams, Tavernier, Groß, B.Fernandes, Mbeumo, E.Le Fée, Barry, Haaland | Steele, van Ewijk, Maguire, Kusi-Asare |
| C_behold_flagg | Verbruggen, Gabriel, Konsa, N.Williams, Tavernier, Groß, B.Fernandes, Mbeumo, E.Le Fée, Barry, Haaland | Steele, van Ewijk, Calafiori, Kusi-Asare |

## 2. Parede skadesimuleringer: verdien av å vente

200 felles verdener per skaderate (1 %, 2 %, 3 %), seed 7089878. Nye fravær kan starte i alle runder R9–R19 for alle 669 spillere, også ikke-eide kjøpskandidater. Varighet 1/2/3/6 runder trekkes med lik sannsynlighet. Ingen ny skade mens spilleren allerede er ute. R9-fravær er kjent før den aktuelle R9-handlingen. Alle baner og begge poengsett møter samme spillerfravær.
Ved hver frist kjenner beslutningstakeren bare fravær som allerede har oppstått, og antatt sluttdato for disse. Fremtidige nye fravær er skjult. WC11 får dermed bruke skader som har oppstått før R11; WC9 får gjøre reparasjoner med opptjente FT. Ingen kjent skadet spiller kjøpes, mens en allerede eid skadet spiller kan beholdes dersom prognosen etter retur forsvarer det. WC-datoene er faste; det er ingen automatisk fremskynding.
Samme neste-fire-runder-politikk i alle baner, avkortet før WC og uten FH-runden. For R9-broen til WC10/WC11 vurderes også de heltallsoptimerte R9-kandidatene; WC11-broen tar med neste frists mulige gratisbytter, beregnet bare med allerede kjent fravær. Dette hindrer at en kjent finansieringsmulighet faller ut av det grådige søket. Gratisbytter krever >1 poeng per brukt FT (null ved fem FT eller R19); ett ekstra betalt bytte krever >5 brutto, altså >1 netto. Enkeltbytter og et avgrenset søk etter tobytte-finansiering vurderes. Maks fem lagrede FT. WC/FH bevarer FT uten opptjening, som R1; denne sesongregelen er fortsatt en antakelse i grunnlaget. A er eksplisitt tvunget til å rulle R9, også når et nytt R9-fravær oppstår.

| p | Mot | Sett | E snitt | Sen/hold snitt | E minus | E vinner | Δ p10–p90 | MC-SE | Endring fra p=0 |
|---|---|---|---:|---:|---:|---:|---|---:|---:|
| 1% | F_WC10 | codex | 682.6 | 677.3 | +5.3 | 99.5% | +3.5 til +7.1 | 0.11 | +0.1 |
| 1% | F_WC11 | codex | 682.6 | 673.6 | +9.1 | 100.0% | +7.2 til +11.4 | 0.15 | +0.5 |
| 1% | A | codex | 682.6 | 670.1 | +12.5 | 100.0% | +10.5 til +14.7 | 0.15 | +0.0 |
| 1% | F_WC10 | repo_hybrid | 731.6 | 729.7 | +1.9 | 91.5% | +0.4 til +4.2 | 0.14 | +0.7 |
| 1% | F_WC11 | repo_hybrid | 731.6 | 727.8 | +3.8 | 98.0% | +1.8 til +6.4 | 0.15 | +1.3 |
| 1% | A | repo_hybrid | 731.6 | 723.2 | +8.4 | 100.0% | +6.6 til +10.8 | 0.13 | +0.9 |
| 2% | F_WC10 | codex | 679.7 | 674.1 | +5.6 | 97.5% | +3.4 til +8.4 | 0.18 | +0.4 |
| 2% | F_WC11 | codex | 679.7 | 670.1 | +9.6 | 99.5% | +6.2 til +13.0 | 0.21 | +1.0 |
| 2% | A | codex | 679.7 | 666.8 | +12.9 | 100.0% | +9.8 til +16.4 | 0.21 | +0.4 |
| 2% | F_WC10 | repo_hybrid | 728.9 | 726.4 | +2.5 | 89.5% | -0.1 til +5.0 | 0.18 | +1.3 |
| 2% | F_WC11 | repo_hybrid | 728.9 | 724.1 | +4.8 | 97.5% | +1.7 til +8.3 | 0.20 | +2.3 |
| 2% | A | repo_hybrid | 728.9 | 719.6 | +9.3 | 100.0% | +6.4 til +12.1 | 0.19 | +1.8 |
| 3% | F_WC10 | codex | 676.9 | 671.1 | +5.9 | 97.5% | +2.9 til +8.9 | 0.20 | +0.6 |
| 3% | F_WC11 | codex | 676.9 | 667.1 | +9.8 | 99.5% | +6.1 til +13.7 | 0.24 | +1.2 |
| 3% | A | codex | 676.9 | 663.5 | +13.4 | 100.0% | +9.7 til +18.0 | 0.25 | +0.9 |
| 3% | F_WC10 | repo_hybrid | 726.4 | 723.3 | +3.1 | 88.5% | -0.1 til +6.2 | 0.19 | +1.9 |
| 3% | F_WC11 | repo_hybrid | 726.4 | 721.0 | +5.5 | 97.0% | +2.0 til +9.2 | 0.23 | +3.0 |
| 3% | A | repo_hybrid | 726.4 | 716.3 | +10.1 | 100.0% | +6.3 til +14.3 | 0.24 | +2.6 |

«E vinner» gjelder forventede poeng gitt de trukne skadeforløpene, ikke sannsynligheten for at laget faktisk får flest kamppoeng. p10–p90 er for den parede forskjellen. MC-SE gjelder bare numerisk simuleringsstøy. Spilletids-/bonusfeil, tilfeldige mål og felles lagsjokk er ikke inkludert. Skaderaten økes ikke særskilt i landslagspausen, og nye rolleendringer, friskmeldinger av dagens blokkerte kandidater og endret kampprogram modelleres ikke.
For kjøretid brukes samme begrensede søk i begge baner: ni beste + fire billigste kjøpskandidater per posisjon, symmetriske WC/FH-starttropper, opptil tre lokale forbedringer. Aktuelle bytteforslag velges fra en rask poengtilnærming; de tre beste vurderes med eksakt autobytteforventning. MC-ellever velges fra fire rangeringer og alle formasjoner; alle benkerekkefølger i dette utvalget vurderes eksakt. Ingen global optimalitetsgaranti. Hovedtabellen bruker full elleveroptimering. Forskjellen mot den identiske lette MC-politikken ved p=0 er kontrollert:

| Plan | Sett | Full ellever | MC-policy p=0 | Forskjell |
|---|---|---:|---:|---:|
| E | codex | 685.4 | 685.4 | +0.00 |
| E | repo_hybrid | 733.8 | 733.8 | +0.00 |
| F_WC10 | codex | 680.1 | 680.1 | +0.00 |
| F_WC10 | repo_hybrid | 732.6 | 732.6 | +0.00 |
| F_WC11 | codex | 676.8 | 676.8 | +0.00 |
| F_WC11 | repo_hybrid | 731.3 | 731.3 | +0.00 |
| A | codex | 672.9 | 672.9 | +0.00 |
| A | repo_hybrid | 726.3 | 726.3 | +0.00 |

## 3. Groß: bundet benkebudsjett og BB19

Begge WC9-troppene har samme salgsverdi + bank £99,4m. «Behold» pålegger at Groß inngår ved WC9; «selg» utelukker ham ved WC9. Senere bytter er frie under samme policy, og eventuell tilbakekjøping er synlig i grossplaner_r2.json. Testen gjentas helt uten BB for å undersøke forklaringen. FH16 beholdes.

| WC9-krav | BB | R9-bank | Groß i R19-tropp | Codex R9–19 | Repo R9–19 |
|---|---|---:|---|---:|---:|
| behold | 19 | 0.4 | ja | 685.4 | 733.8 |
| selg | 19 | 0.0 | ja | 676.9 | 738.2 |
| behold | ingen | 0.4 | ja | 675.1 | 723.5 |
| selg | ingen | 0.0 | ja | 666.6 | 727.9 |
Selg minus behold (BB19): -8.5/+4.4 poeng.
Selg minus behold (uten_BB): -8.5/+4.4 poeng.

BB endrer den relative fordelen ved å beholde Groß med +0.0/+0.0 poeng. Dette måles med reoptimerte starttropper og fremtidige bytter, ikke ved å tilskrive all benkeverdi i R19 til Groß. Forskjellen er betinget av det avgrensede søket. Groß har også vanlig benke-/rotasjonsverdi gjennom autobytter; at han står på R9-benken betyr ikke at pengene bare arbeider på BB-dagen.

## 4. Opprykksforsvar: 20 % flere forventede innslupne

For HUL, LEE og COV settes λ for innslupne mål til 1,2 × λ i hver kamp R9–R19. Dermed endres både P(nullen)=exp(−λ) og forventet straff for hvert annet innslupne mål. Dette er ikke et flatt 20 %-kutt i nullsannsynligheten. Angrep, minutter, redninger, bonus og DC holdes uendret. Repo-filen mangler rene CS/GC-komponenter; samme absolutte Codex-komponentendring legges derfor på repo_hybrid. Dette er en eksplisitt hybridtilnærming.
Faste kjøpsbaner; ellever, kaptein og benkerekkefølge velges på nytt under stresstallene. Testen isolerer prognosefeilen og inkluderer ikke nye kjøp som svar på en ny erkjennelse av lagstyrke.

| Plan | Codex før → etter | Repo før → etter | Tap codex/repo |
|---|---:|---:|---:|
| E | 685.4 → 678.7 | 733.8 → 726.9 | -6.7/-6.9 |
| F_WC10 | 680.1 → 673.9 | 732.6 → 726.1 | -6.2/-6.5 |
| F_WC11 | 676.8 → 671.5 | 731.3 → 726.0 | -5.3/-5.3 |
| C | 676.8 → 671.5 | 731.3 → 726.0 | -5.3/-5.3 |
| A | 672.9 → 667.0 | 726.3 → 720.4 | -5.9/-5.9 |

Etter stresstesten: E minus F_WC11 = +7.2/+0.9 poeng. E minus C = +7.2/+0.9.

## 5. Claudes spilletid og innhoppsusikkerheten

B.Fernandes settes til p_start 0,75 og Calafiori til 0,50 i R9. Deres forventede minutter skaleres tilsvarende fra R1, slik at minuttforventningen følger den nye startsannsynligheten. Alle øvrige spiller-/rundeminutter er identiske med R1. Full fil: minutter_antatt_r2.csv. Ingen av Claudes øvrige minuttforslag er sneket inn.
Fernandes p_play R9 = 0.75; Calafiori p_play = 0.75. For Calafiori kommer forskjellen fra innhoppsandelen blant observerte kamper uten start og API-tilgjengelighet 75 %. Utvalget er lite, og dette er en modellantakelse – ikke et nytt medisinsk faktum. Jeg viser derfor også p_play=0,50 ved samme ubetingede xP. Det isolerer mer benkedekning fremfor å endre spillerprognosen samtidig.

| Plan | Calafiori p_play | Codex R9 | Repo R9 | Calafiori starter |
|---|---:|---:|---|
| A | 0.50 | 52.2 | 60.2 | ja |
| C | 0.50 | 54.2 | 63.0 | nei |
| C_behold_flagg | 0.50 | 54.4 | 63.0 | ja |
| E | 0.50 | 59.7 | 66.1 | nei |
| A | 0.75 | 51.8 | 59.9 | nei |
| C | 0.75 | 54.2 | 63.0 | nei |
| C_behold_flagg | 0.75 | 54.0 | 62.8 | nei |
| E | 0.75 | 59.7 | 66.1 | nei |

## 6. Direkte vurdering av Claudes forslag

Å rulle (A) koster mot C: 2.4/3.1 forventede poeng i R9 og 3.9/5.0 gjennom R19 i den nominelle beregningen med autobytter.
Å rulle (A) koster mot E: 7.9/6.2 forventede poeng i R9 og 12.5/7.5 gjennom R19 i den nominelle beregningen med autobytter.

Claude har rett i at autobytter må med. Det følger derimot ikke at de svekker WC9-fordelen: en WC-tropp med en sterkere spillende benk får også merverdi. Tabellen i punkt 1 måler virkningen for begge sider. En fast «+1,5 til A» uten å beregne E på samme måte er ikke en sammenligning.
Informasjon etter landslagspausen er reell, men er ikke gratis poeng. Sen WC kan velge med nyere skadeinfo; tidlig WC gir en bedre benk og FT som kan reparere. Den parede skadesimuleringen priser akkurat denne delen under identiske fravær og samme byttepolitikk. Den beregnede endringen fra p=0 er riktig mål på skadeinformasjonens nettovirkning i testen. Det er ikke grunnlag for å legge ytterligere «1–2 poeng per spart FT» på A etter at FT allerede er brukt i den simulerte politikken.
Testen avgjør ikke verdien av ukjente trener-/rolleendringer, pressekilders kvalitet eller retur for dagens utelukkede kjøpskandidater etter pausen. Å velge venting på grunn av dette er et skjønn om umodellert informasjon, ikke et resultat fra skadeberegningen. Et bevis for at all informasjonsverdi er null finnes ikke her.

## Konkret tropp og budsjett for anbefalingen

| ID | Spiller | Lag/status | Handling | Salgsverdi hvis eid | Ny kjøpspris | R9-rolle |
|---:|---|---|---|---:|---:|---|
| 385 | Trafford | LEE/a | kjøp | – | 5.0 | Benk GK |
| 572 | Tzolakis | HUL/a | kjøp | – | 4.7 | XI |
| 4 | Gabriel | ARS/a | kjøp | – | 7.9 | XI |
| 115 | De Cuyper | BHA/a | kjøp | – | 5.3 | Benk 2 |
| 173 | Thomas | COV/d | kjøp | – | 4.0 | XI |
| 334 | Muharemović | LEE/a | kjøp | – | 5.1 | Benk 3 |
| 566 | Silva | BOU/a | kjøp | – | 5.0 | XI |
| 15 | Ødegaard | ARS/a | kjøp | – | 6.7 | XI |
| 68 | Tavernier | BOU/a | behold | 6.3 | – | XI |
| 124 | Groß | BHA/a | behold | 5.9 | – | Benk 1 |
| 183 | Rudoni | COV/a | kjøp | – | 4.9 | XI |
| 427 | Mbeumo | MUN/a | behold | 7.9 | – | XI (VC) |
| 249 | Barry | EVE/a | kjøp | – | 5.6 | XI |
| 379 | Isak | LIV/a | kjøp | – | 9.1 | XI |
| 411 | Haaland | MCI/a | behold | 15.6 | – | XI (C) |

Budsjett: £1,6m + verifiserte salg £62.1m − kjøp £63.3m = **£0.4m i bank**. Beholdt salgsverdi + nye kjøp er £99.0m; sammen med banken er dette £99,4m. Tallene bruker de frosne prisene fra 29. oktober, ikke en ny prisinnhenting 30. oktober.

| Ut-ID | Spiller ut | Verifisert salgspris |
|---:|---|---:|
| 8 | Calafiori | 5.8 |
| 31 | Konsa | 4.6 |
| 106 | Thiago | 7.8 |
| 109 | Verbruggen | 4.5 |
| 111 | Steele | 4.0 |
| 175 | van Ewijk | 3.9 |
| 272 | Kusi-Asare | 4.4 |
| 418 | Maguire | 4.7 |
| 426 | B.Fernandes | 11.7 |
| 469 | N.Williams | 5.0 |
| 542 | E.Le Fée | 5.7 |

**Thomas er ID 173, COV, forsvarer, status d, 75 %, «Unspecified injury - 75% chance of playing».** Han er ikke Thomas-Asante. R9-prognosen bruker p_start **0,7015**, **59,28 forventede minutter** og det reduserte p_play fra `p_play_r2.csv`. Det er også forutsetningen gjennom R19. Hele spillerfilen er nå gjenberegnet fra `minutter_antatt_r2.csv`; det er ingen frisk 90-minutters-Thomas skjult i poengtallene. E forblir best blant de testede hovedplanene på 50/50-gjennomsnittet av de to poengsettene med nettopp denne antakelsen. Dette er ikke en garanti for globalt optimum eller at Thomas faktisk starter.
Fernandes (426) er solgt i denne WC9-planen. Ødegaard, Isak og Muharemović er med i de oppførte ID-ene. Dette er en ny WC-tropp fra R2, ikke R1-troppen. Salget er en samlet budsjett-/poengprioritering gjennom R19, ikke en påstand om at Fernandes er ute.

## Sluttkontroll av avbrudd, ID-er og prognose

Kjøringen som fortsatte etter avbruddet fullførte alle tre skaderater og avsluttet med `DONE E`. 200 parede verdener ved hvert av 1 %, 2 % og 3 % gir 600 skadeverdener; begge poengsett er vurdert i de samme verdenene. Alle 18 sammendragsrader er uavhengig beregnet på nytt fra `skadetrekk_r2.csv`.
Det raske søket er korrigert: broen til WC11 vurderer også de kjente tobytte-kandidatene og det påfølgende gratisbyttet i R10. F_WC11 velger nå samme R9-tropp som C (Calafiori/Thiago → Gabriel/Barry) og gir 676,8/731,3 nominelle poeng. Samtlige skaderater i rapporten bruker denne korrigerte politikken. Ingen fremtidige, ennå ukjente skader gis til planleggeren.
Testen uten BB er også korrigert: faktisk BB-parameter sendes gjennom både WC-søket og byttepolitikken. Ingen del av den varianten planlegger for eller scorer BB19. At behold/selg-forskjellen likevel er den samme med og uten BB, er resultatet av den nye kjøringen. BB forklarer derfor ikke at Groß beholdes her. Codex foretrekker behold-pakken, mens repo-hybrid foretrekker salgspakken; dette er en reell modelluenighet.
Alle 5352 rader i `spillerpoeng_r2.csv`, samt R17–R19-filen, er kontrollert mot den faktiske minuttfilen og poengmotoren. Største avvik er 0.00000050 poeng, bare CSV-avrunding. Alle hoved- og Groß-planpoeng er deretter beregnet på nytt fra spiller-CSV-ene og de lagrede autobytte-/kapteinsvektene; største avvik per runde er 0.00000377 poeng. Alle rapporterte horisonter stemmer innen avrunding.
Tropp, ellever, benkrekkefølge, kaptein, visekaptein, vekter og poeng er identiske mellom E i `planer_r2.json` og «behold_BB19» i `grossplaner_r2.json`. De tilhørende CSV-radene er kontrollert mot disse eksakte planene. ID-listen over finnes også i `anbefalt_tropp_r2.csv`, med salgs-/kjøpspris og R9-rolle. Ingen R1-filer er endret.
Robusthet: WC9 leder i begge modeller i skadeforløpene, men fordelen mot WC10 er liten i repo-hybrid; p10 ved 2 % og 3 % ligger svakt under null. Opprykksstressen reduserer repo-fordelen mot WC11 til omtrent 0,9 poeng. Anbefalingen er derfor WC9 etter forventning, med tydelig modellusikkerhet – ikke en sikker eller stor gevinst.

## Kjøring og avgrensning

Kjør `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH` og `python samarbeid/gw09/codex/modell_r2.py`. Bruker eksisterende numpy, numba og PuLP/CBC. Ingen nettverk/installasjon. R1-koden leses som metodegrunnlag med alle skrivefunksjoner deaktivert; R1s hovedkjøring utføres ikke. R1-filene har uendrede sjekksummer etter kjøringen.
spillerpoeng_r2.csv dekker alle 669 spillere R9–R16 i begge poengsett. Den inneholder spiller-xP uten lagavhengige autobytter; vektene som gjenskaper lagpoengene ligger i planer_r2.json. Repo-hybrid bruker repoets R9–R14 og Codex R15–R19, med samme minuttskalering som R1. Prognoseevalueringen må bruke spillerfilen på spillernivå og ta autobytter fra lagplanen separat.
Hovedbegrensninger: konstante priser, ingen nye blanke/doble runder, uavhengige normale spilleutfall, dagens kjøpsfilter og utestengte/skadde holdt ute til ukjent retur. WC/FH- og transfer-søk er avgrenset; samme starttropper og metode benyttes symmetrisk. Tall med én desimal er for etterprøvbarhet, ikke et løfte om tilsvarende prognosepresisjon.

Kjør deretter `python samarbeid/gw09/codex/sluttkontroll_r2.py` for ID-tabeller og uavhengig konsistenskontroll. Denne etterkontrollen endrer ingen prognoser eller simuleringstall.
