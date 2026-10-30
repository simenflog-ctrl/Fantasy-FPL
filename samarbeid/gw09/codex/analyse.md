# R9: beregning og anbefaling

**Anbefaling: E – wildcard i R9.**
R9: ut Calafiori, Konsa, Thiago, Verbruggen, Steele, van Ewijk, Kusi-Asare, Maguire, N.Williams, E.Le Fée; inn Gabriel, De Cuyper, Rudoni, Thomas-Asante, Barry, Egan, Justin, Trafford, Silva, Tzolakis. Trekk 0 poeng; bank £0.0m. Dette er beregningsgrunnlag før Claudes endelige spilletidsvurdering, ikke gjennomførte FPL-handlinger.

**Ellever:** Tzolakis, Gabriel, Silva, Egan, De Cuyper, Mbeumo, Tavernier, B.Fernandes, Rudoni, Haaland, Barry.
**Kaptein:** Haaland. **Visekaptein:** Mbeumo.
**Benk:** Trafford, Thomas-Asante, Justin, Groß (keeper først, deretter utespillere i prioritert rekkefølge).

## Verifisert og manglende grunnlag

Frosset API 29. okt: 15 spillere, bank £1,6m, to FT, salgsverdi £97,8m; kjøpekraft £99,4m. MUN og BHA har tre hver. Frist R9 31. okt 11:00 UTC. WC10-frist 6. nov; WC11-frist 21. nov, etter landslagspausen. TC brukt; WC1/FH1/BB1 utløper R19. Ingen blanke/doble runder i filene.
Repoets expected_points.csv har 4014 spiller/runde-rader, samtlige 669 spillere R9–R14. R15–R19 bruker Codex også i repo_hybrid. Kopier av botens filer er frosset i codex/input; datoen 26. okt er oppgitt av bruker, ikke en datostemplet kolonne i CSV. Historiske minutter og xG kontrolleres mot bootstrap for alle spillere.
Salah finnes ikke i bootstrap eller repoets spillerunivers: ingen Salah-prognose eller observert snitt kan beregnes. Historikk for tidligere sesonger finnes bare for utvalget i element_summary; øvrige får posisjonsprior. Ingen returdag oppfinnes for kjøpsforbudte/skadde spillere; de er utelatt gjennom R19. Dette er konservativt og kan særlig påvirke senere WC.

## Rangering av konkrete planer

Alle hovedalternativer bruker BB19/FH16. A–D har WC11; F varierer WC-dato med identisk rullerende byttepolitikk. Rangering bygger på 50/50 gjennomsnitt av de to poengsettene. Hver rad er én konkret troppsbane med samme ellever og kaptein vurdert under begge modeller.

| Plan | WC/BB/FH | R9 codex/repo | R9–12 | R9–16 | R9–19 | Trekk R9 | Bank |
|---|---|---:|---:|---:|---:|---:|---:|
| E | 9/19/16 | 55.8/64.4 | 226.9/267.4 | 458.4/520.7 | 647.4/709.7 | 0 | 0.0 |
| G_BB19_FH16 | 9/19/16 | 55.8/64.4 | 226.9/267.4 | 458.4/520.7 | 647.4/709.7 | 0 | 0.0 |
| G_BB18_FH16 | 9/18/16 | 55.8/64.4 | 226.9/267.4 | 458.4/520.7 | 646.0/708.2 | 0 | 0.0 |
| G_BB17_FH13 | 9/17/13 | 55.8/65.0 | 225.1/264.6 | 457.2/517.7 | 644.8/705.3 | 0 | 0.2 |
| G_BB19_FH13 | 9/19/13 | 55.7/63.0 | 226.2/261.9 | 458.9/515.3 | 646.7/703.1 | 0 | 0.8 |
| F_WC10 | 10/19/16 | 51.5/60.3 | 222.6/263.3 | 454.1/516.6 | 643.1/705.6 | 0 | 1.7 |
| C | 11/19/16 | 51.5/60.3 | 221.4/262.7 | 452.9/515.9 | 641.9/704.9 | 0 | 1.7 |
| F_WC11 | 11/19/16 | 51.5/60.3 | 221.4/262.7 | 452.9/515.9 | 641.9/704.9 | 0 | 1.7 |
| G_BB15_FH18 | 9/15/18 | 56.0/63.2 | 227.9/260.1 | 474.4/523.5 | 648.8/698.0 | 0 | 0.2 |
| F_WC12 | 12/19/16 | 51.5/60.3 | 220.5/262.9 | 452.0/516.1 | 641.0/705.2 | 0 | 1.7 |
| G_FH9 | 11/19/9 | 56.7/67.6 | 225.1/263.9 | 456.7/512.8 | 644.8/700.9 | 0 | 1.6 |
| D3 | 11/19/16 | 49.1/58.4 | 219.9/261.7 | 451.4/515.0 | 640.4/704.0 | 4 | 1.7 |
| B | 11/19/16 | 50.9/59.1 | 220.0/260.3 | 451.6/513.6 | 640.6/702.6 | 0 | 2.4 |
| D4 | 11/19/16 | 46.3/56.2 | 217.2/259.5 | 448.7/512.7 | 637.7/701.7 | 8 | 0.0 |
| F_WC14 | 14/19/16 | 51.5/60.3 | 219.1/260.4 | 450.7/511.6 | 638.7/699.6 | 0 | 1.7 |
| A | 11/19/16 | 49.0/57.2 | 216.7/256.9 | 448.2/510.1 | 637.2/699.1 | 0 | 1.6 |
| D5 | 11/19/16 | 43.0/53.1 | 213.8/256.4 | 445.4/509.7 | 634.4/698.7 | 12 | 0.6 |
| G_BB9 | 11/9/16 | 56.8/65.9 | 226.7/268.2 | 458.2/521.5 | 632.2/695.4 | 0 | 1.7 |
| G_uten_BB_FH | 9/–/– | 55.8/64.4 | 226.9/267.4 | 456.1/518.4 | 630.0/692.3 | 0 | 0.0 |

A = ingen R9-bytter, tre FT i R10. B/C = ett/to gratisbytter. D3/D4/D5 = tre/fire/fem bytter med −4/−8/−12, vurdert netto. E = WC9. F = senere WC. G = alternative chipkalendere; G_uten_BB_FH er bare verdireferanse, ikke anbefalt å la chips utløpe.

| Handling R9 | Ut | Inn |
|---|---|---|
| A | ingen | ingen |
| B | Calafiori | Silva |
| C | Calafiori, Thiago | Gabriel, Barry |
| D3 | Calafiori, Thiago, N.Williams | Gabriel, Barry, Silva |
| D4 | Calafiori, Thiago, Verbruggen, N.Williams | Raya, Gabriel, Barry, Silva |
| D5 | Calafiori, Thiago, Verbruggen, Maguire, N.Williams | Raya, Gabriel, Barry, Egan, Silva |
| E | Calafiori, Konsa, Thiago, Verbruggen, Steele, van Ewijk, Kusi-Asare, Maguire, N.Williams, E.Le Fée | Gabriel, De Cuyper, Rudoni, Thomas-Asante, Barry, Egan, Justin, Trafford, Silva, Tzolakis |

## Hvor robust er R9-valget?

Anbefalingen følger høyest beregnet forventning; det er ikke lagt inn et vilkårlig poengtillegg for å vente på informasjon. Fordelen er likevel liten mot de nærmeste alternativene og må vurderes på nytt når Claude leverer minutter. Intervallene under er parede modellscenarioer, ikke sannsynligheter for faktisk gevinst.

| Anbefalt minus | Poengsett | Forskjell R9–19 | p10–p90 |
|---|---|---:|---|
| A | codex | +10.2 | +2.5 til +17.5 |
| A | repo_hybrid | +10.6 | +2.1 til +18.6 |
| B | codex | +6.8 | +0.2 til +12.5 |
| B | repo_hybrid | +7.1 | -0.3 til +13.5 |
| C | codex | +5.5 | -0.3 til +10.9 |
| C | repo_hybrid | +4.8 | -1.4 til +10.7 |
| F_WC10 | codex | +4.3 | +1.0 til +7.5 |
| F_WC10 | repo_hybrid | +4.1 | +0.7 til +7.5 |
| F_WC11 | codex | +5.5 | -0.3 til +10.9 |
| F_WC11 | repo_hybrid | +4.8 | -1.4 til +10.7 |
| D3 | codex | +7.0 | +1.6 til +11.9 |
| D3 | repo_hybrid | +5.7 | -0.2 til +11.0 |

Uten WC er C beste testede gratisbytteplan. D-alternativene vurderes etter poengtrekk; de må slå den beste gratisplanen, ikke bare A, for å forsvare trekket. WC10/11-tabellen bruker samme konkrete R9-handling som C, slik at bytteantall ikke blandes inn i tidssammenligningen.


## Budsjett og faktisk tropp

| Spiller | Klubb | Marked | Budsjettverdi salg/kjøp | Behold/kjøp |
|---|---|---:|---:|---|
| Trafford | LEE | 5.0 | 5.0 | kjøp |
| Tzolakis | HUL | 4.7 | 4.7 | kjøp |
| Gabriel | ARS | 7.9 | 7.9 | kjøp |
| De Cuyper | BHA | 5.3 | 5.3 | kjøp |
| Egan | HUL | 4.1 | 4.1 | kjøp |
| Justin | LEE | 4.5 | 4.5 | kjøp |
| Silva | BOU | 5.0 | 5.0 | kjøp |
| Tavernier | BOU | 6.4 | 6.3 | behold |
| Groß | BHA | 6.2 | 5.9 | behold |
| Rudoni | COV | 4.9 | 4.9 | kjøp |
| B.Fernandes | MUN | 11.7 | 11.7 | behold |
| Mbeumo | MUN | 7.9 | 7.9 | behold |
| Thomas-Asante | COV | 5.0 | 5.0 | kjøp |
| Barry | EVE | 5.6 | 5.6 | kjøp |
| Haaland | MCI | 15.8 | 15.6 | behold |

| Utgående spiller | Verifisert salgspris |
|---|---:|
| Calafiori | £5.8m |
| Konsa | £4.6m |
| Thiago | £7.8m |
| Verbruggen | £4.5m |
| Steele | £4.0m |
| van Ewijk | £3.9m |
| Kusi-Asare | £4.4m |
| Maguire | £4.7m |
| N.Williams | £5.0m |
| E.Le Fée | £5.7m |

Kontroll: £1,6m + salg £50.4m − kjøp £52.0m = £0.0m. Alle baner kontrolleres for 2/5/5/3 posisjoner, maks tre per klubb, ikke-negativ bank og lovlig kjøpsunivers. Beholdte spillere belastes salgsverdi i WC-budsjettet; man betaler ikke markedspris for å beholde egne prisstigninger.

## Foreløpig viderebane for anbefalingen

| Runde | Chip | Ut | Inn | FT etter | Bank |
|---|---|---|---|---:|---:|
| 9 | WC | Calafiori, Konsa, Thiago, Verbruggen, Steele, van Ewijk, Kusi-Asare, Maguire, N.Williams, E.Le Fée | Gabriel, De Cuyper, Rudoni, Thomas-Asante, Barry, Egan, Justin, Trafford, Silva, Tzolakis | 2 | 0.0 |
| 10 | – | ingen | ingen | 3 | 0.0 |
| 11 | – | ingen | ingen | 4 | 0.0 |
| 12 | – | ingen | ingen | 5 | 0.0 |
| 13 | – | ingen | ingen | 5 | 0.0 |
| 14 | – | ingen | ingen | 5 | 0.0 |
| 15 | – | ingen | ingen | 5 | 0.0 |
| 16 | FH | Rudoni, Barry, Egan, Justin, Trafford, B.Fernandes, Mbeumo, Tzolakis | Raya, Ødegaard, Hill, Henderson, Anthony, Walton, Isak, Vuskovic | 5 | 0.0 |
| 17 | – | ingen | ingen | 5 | 0.0 |
| 18 | – | ingen | ingen | 5 | 0.0 |
| 19 | BB | Rudoni, Thomas-Asante, Egan, B.Fernandes | Ødegaard, Konsa, Gomez, Isak | 2 | 0.2 |

FH-troppen er midlertidig; oppgitt bank er den permanente bankbeholdningen som kommer tilbake etter FH. Alle fremtidige kjøp er foreløpige med frosne priser og nyheter.

## WC-tidspunkt med lik chipkalender

| WC | codex R9–19 | repo R9–19 |
|---|---:|---:|
| 9 | 647.4 | 709.7 |
| 10 | 643.1 | 705.6 |
| 11 | 641.9 | 704.9 |
| 12 | 641.0 | 705.2 |
| 14 | 638.7 | 699.6 |

Felles kalender valgt fra 9 kandidatpar etter gjennomsnittlig resultat for WC9/10/11. wildcard_tidspunkt.csv inneholder alle par som er spilt gjennom. Søket vurderer marginal BB/FH-verdi i alle lovlige runder, spiller gjennom topprangerte sene par og faste kontrollpar, samt BB9/FH9. Dette er ikke et uttømmende globalt optimum over alle datoer og fremtidige bytter.
Alle bruker neste fire runder (avkortet før WC, FH utelatt, BB inkludert). Gratisbytte krever >1 poeng forbedring, ved fem FT eller R19 >0; ett ekstra betalt bytte krever >5 brutto. Maks fem lagrede FT. WC/FH antas å bevare FT uten opptjening; reset og +1 er prøvd i FT_regler.csv. Prisene fryses. Fremtidige skader, ny informasjon og informasjonsverdien av landslagspausen er ikke simulert eller priset.

## BB og FH

Valgt konkret plan: BB19 og FH16. chipdatoer_marginal.csv viser separat benkeverdi og FH-gevinst fra chipfrie baner; G-radene inkluderer den endrede byttebanen. BB/FH-overlapp og overlapp med WC er utelukket. Cupflyttinger og juleturnover kan endre dette; datoene er foreløpige.

Med samme WC9 og samme R9-handling gir BB19/FH16 samlet 17.3/17.3 ekstra poeng mot den beregnede banen uten BB/FH. Dette inkluderer endrede bytter, ikke bare en løs chipbonus.

## Kalibrering og bonus

| Spiller | Observert/runde | Codex R9 | Repo rå R9 | Repo justert R9 | Bonus obs./Codex/repo rå |
|---|---:|---:|---:|---:|---|
| Haaland | 8.2 | 6.8 | 8.8 | 8.9 | 1.8/1.4/2.7 |
| B.Fernandes | 4.1 | 4.2 | 5.1 | 5.4 | 0.4/0.6/1.0 |
| Mbeumo | 5.4 | 4.9 | 5.1 | 5.2 | 0.6/0.6/0.6 |
| Rogers | 5.1 | 4.0 | 5.6 | 5.2 | 0.2/0.3/0.9 |
| Gabriel | 6.5 | 4.5 | 5.5 | 5.5 | 0.6/0.7/0.9 |
| Palmer | 4.6 | 4.3 | 4.9 | 5.1 | 0.4/0.5/0.8 |
| Isak | 6.4 | 4.2 | 2.6 | 3.1 | 1.8/1.2/0.3 |
| Watkins | 0.0 | 0.0 | 0.0 | 0.0 | 0.0/0.0/0.0 |
| Tavernier | 6.5 | 4.7 | 6.0 | 5.3 | 1.5/0.8/1.5 |
| Thiago | 2.9 | 3.4 | 4.6 | 3.9 | 0.0/0.2/0.3 |

Codex viderefører R2/R3: nåværende xG/xA/bonus per 90 krympes mot inntil to tidligere sesonger (540 prior-minutter; ellers posisjonsprior 270). Lagstyrke krympes med syv kamper; xGA er motstanderens samlede xG. Poisson for nullen/innslupne/redninger; empirisk defensive-contribution-treffrate. Alle poengvekter kommer fra game_config.scoring, keepermål 10. Bonus følger historisk bonusrate, ikke en ny premiumrabatt. Ingen ny kalibrering ut fra én enkelt R8-kamp. Repoets høyere premiumbonus beholdes i repo_hybrid og synliggjøres i tabellen.
Repo-hybrid skalerer rå xP med våre forventede minutter / repoets minutter for å bruke samme nyhetsgrunnlag. Dette er en tilnærming, særlig ved 60-minuttersgrensen. R15–19 er lik Codex, så modellspennet der er ikke uavhengig. Modellen beregner forventet valgt ellever + kaptein, uten autobytter eller visekaptein-overføring ved null minutter; benkedekning kan derfor være undervurdert.

## Usikkerhet og følsomhet

For valgt plan er forventning R9 55.8/64.4; R9–19 647.4/709.7. Modellfølsomhet p10–p90: Codex 596.3–700.0, repo 650.0–768.1.
Intervallene kommer fra 1 000 parede lognormale rater: 20 % vedvarende spillerusikkerhet og 10 % ekstra per runde, middel 1. Dette er antatt modellspredning, ikke kalibrerte konfidensintervaller eller intervaller for faktiske kamppoeng. Ingen kamputfallsstøy, ny skadeprosess eller ny bytteoptimering i trekkene. Spillerfaktorer er felles på tvers av planene. Tall vises med én desimal for kontroll, men små forskjeller er ikke beslutningspresisjon.

| Følsomhet valgt handling | p_start R9 | Codex R9 | Repo R9 | Valgt minus C, codex/repo R9 |
|---|---:|---:|---:|---:|
| B.Fernandes | 0.55 | 54.3 | 62.5 | +4.3/+4.1 |
| B.Fernandes | 0.85 | 55.8 | 64.5 | +4.3/+4.1 |
| B.Fernandes | 0.98 | 56.4 | 65.3 | +4.3/+4.1 |
| Calafiori | 0.00 | 55.8 | 64.5 | +4.3/+4.1 |
| Calafiori | 0.35 | 55.8 | 64.5 | +4.3/+4.1 |
| Calafiori | 0.65 | 55.8 | 64.5 | +4.3/+4.1 |
| Calafiori | 0.90 | 55.8 | 64.5 | +4.3/+4.1 |

| Flerukescenario, faste kjøp | E minus WC10, codex/repo | E minus C/WC11, codex/repo |
|---|---:|---:|
| Fernandes p_start 0.55 R9–10 | +4.3/+4.1 | +5.8/+4.4 |
| Calafiori p_start 0.90 R9–10 | +4.3/+4.1 | +5.4/+4.8 |
| Calafiori helt ute R9–10 | +4.3/+4.1 | +5.4/+4.8 |
| Begge flaggede friske fra R10 | +4.3/+4.1 | +5.1/+4.9 |

Flerukescenarioene er betingede antakelser, ikke nye nyheter. XI/kaptein velges på nytt; kjøpsbanen er frosset, så tabellen måler følsomhet for de konkrete planene, ikke reoptimalt byttevalg. Full tabell i folsomhet_fleruker.csv.

Følsomhet endrer R9-poeng proporsjonalt med start/minutter og velger ny lovlig ellever/kaptein i samme tropp. Calafiori testes også helt ute. Dette er ikke en medisinsk returmodell. Full tabell for A/B/C/E og anbefalingen i folsomhet.csv. Fernandes har 0,85 start R9 og 0,92 senere; Calafioris og N.Williams’ 75 %-flagg videreføres uten sikker retur. Groß reduseres etter cupbelastning; hvile for Haaland/Verbruggen/Le Fée og belastning for Thiago/Tavernier er eksplisitte antakelser i minutter_antatt.csv. Claude kan endre denne filen og kjøre modellen på nytt.

## Søkeavgrensning og reproduksjon

B/C/D har heltallsoptimaliserte kandidater for R9 alene, R9–10 og R9–12; beste faktiske viderebane av disse velges. Tre, fire og fem bytter med trekk vurderes. WC/FH optimaliseres som statisk tropp over relevante runder med eksakt lovlig ellever/kaptein i hvert ledd, hele det godkjente kjøpsuniverset, CBC maks 15 sekunder og relativ toleranse 0,005 %. Ingen global optimalitetsgaranti for adaptiv sesongplan. sokelog.csv viser løserstatus; begrenset tid kan gi bare en gjennomførbar løsning. Kjøpsunivers krever normalt p_start ≥0,5 (d ≥0,35), samme konservative rolleprinsipp som R8; derfor er optimum betinget av filteret.
Kjør: `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH` og `python samarbeid/gw09/codex/modell.py`. Bruker eksisterende numpy/PuLP/CBC. Ingen nettverk eller installasjon. modell_r3_original.py er urørt kopi som metodeproveniens; modell.py er selvstendig og leser ikke R8-filer. minutter_antatt.csv overskrives ikke. Rå input, minuttscenario og spillerprognoser har SHA256 i validering.json. Alle CSV-er og denne rapporten genereres i samme kjøring; planer.json gir hele byttebanen.
