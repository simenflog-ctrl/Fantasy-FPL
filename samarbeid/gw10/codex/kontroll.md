# Kontroll R10 – runde 2

**Endelig anbefaling: Dasilva → Van Hecke og Ødegaard → Iwobi. Ikke Bench Boost nå.** Kaptein **Haaland**, vise **Gabriel**. Bank £0.7m. BB12/FH13 er planleggingsdatoer; særlig FH revurderes senere.

**Ellever:** Trafford, Gabriel, De Cuyper, Muharemović, Tavernier, Groß, Iwobi, Mbeumo, Barry, Isak, Haaland. **Benk:** Tzolakis, Silva, Van Hecke, Rudoni (keeper først; deretter utespillerne i prioritert rekkefølge).

Alle fem planer bruker **BB12/FH13**, FT=2, identiske frosne R1-spillerpoeng, samme adaptive fire-runders byttepolitikk og eksakte autobytter. C er dermed ikke gitt BB11 som i R1-hovedtabellen. Ingen nye minuttantakelser er innført. Valget følger høyest forventning med lik vekt på poengsettene ved 2 % nye fravær; 1 % er følsomhet.

## Konkrete forslag, uten nye fravær

| Plan | Ut → inn | Bank | R10 | R10–R13 | R10–R19 |
|---|---|---:|---:|---:|---:|
| A | ingen → ingen | 0.4 | 60.83 / 69.56 | 253.70 / 292.48 | 619.48 / 675.40 |
| B | Tzolakis → Verbruggen | 0.5 | 60.81 / 69.62 | 253.19 / 293.82 | 618.62 / 677.13 |
| C | Groß, Muharemović → Van Hecke, E.Le Fée | 0.7 | 61.12 / 69.59 | 254.09 / 292.86 | 619.82 / 675.73 |
| Claude_Iwobi | Ødegaard, Dasilva → Van Hecke, Iwobi | 0.7 | 61.02 / 70.20 | 253.89 / 293.12 | 619.35 / 675.72 |
| Claude_Evanilson | Dasilva, Isak → Evanilson, Van Hecke | 2.1 | 59.95 / 69.51 | 251.71 / 293.31 | 616.23 / 677.00 |

Tallpar = codex / repo_hybrid. Alle fem R10-handlinger er lovlige og uten poengtrekk ved 2 FT. Salgspriser brukes, ikke markedspriser. Iwobi-pakken: £0,4 + 4,0 + 6,7 − 5,0 − 5,4 = £0,7m; Evanilson-pakken: £0,4 + 4,0 + 9,1 − 5,0 − 6,4 = £2,1m. Eksakte kjøpspriser og full bankbane følger av planer_r2.json.

## Parede skadesimuleringer

200 felles verdener per rate. Nye fravær fra R11, varighet 1/2/3/6 runder med lik sannsynlighet; fremtidige nye fravær er skjult for byttepolitikken. Fravær rammer også kjøpskandidater. Dette er stressantakelser, ikke medisinsk estimerte rater. De første 100 verdenene gjenskaper R1 nøyaktig.

| Rate | Sett | A snitt | B snitt | C snitt |
|---|---|---:|---:|---:|
| 1% | codex | 616.96 | 615.86 | 616.97 |
| 1% | repo_hybrid | 672.61 | 674.01 | 672.31 |
| 1% | blend | 644.78 | 644.94 | 644.64 |
| 2% | codex | 614.65 | 613.50 | 614.50 |
| 2% | repo_hybrid | 669.78 | 670.99 | 669.13 |
| 2% | blend | 642.22 | 642.24 | 641.81 |



| Rate | Sett | B − A | B vinner | Paret p10–p90 | MC-SE |
|---|---|---:|---:|---|---:|
| 1% | codex | -1.09 | 8.5 % | -2.38 til -0.53 | 0.10 |
| 1% | repo_hybrid | +1.40 | 88.5 % | -0.08 til +1.94 | 0.13 |
| 1% | blend | +0.15 | 65.0 % | -1.18 til +0.91 | 0.11 |
| 2% | codex | -1.15 | 16.0 % | -3.30 til +1.29 | 0.14 |
| 2% | repo_hybrid | +1.21 | 79.5 % | -0.75 til +3.69 | 0.15 |
| 2% | blend | +0.03 | 52.5 % | -1.84 til +2.16 | 0.14 |

«Vinner» gjelder forventede poeng i skadeverdenen, ikke sannsynlighet for flest faktiske kamppoeng. p10–p90 over er for **paret B−A**. Intervall for selve totalsummene og C−A ligger i skadesim_r2.csv og parvise_r2.csv. Kampflaks og modellfeil er ikke med.

| Alternativ mot A | 1 %: Δ blend [p10, p90] | 2 %: Δ blend [p10, p90] |
|---|---:|---:|
| C | -0.14 [-1.64, +0.44] | -0.40 [-2.62, +1.01] |
| Claude_Iwobi | +0.08 [-0.65, +0.41] | +0.12 [-0.89, +1.08] |
| Claude_Evanilson | -0.92 [-2.12, +0.27] | -0.83 [-3.46, +2.33] |

Ved 2 % fravær rangeres Claude_Iwobi først, bare 0.09 poeng foran B. Bytteanbefalingen er derfor svak; poengsettene og fraværsraten betyr mer enn denne marginen. Ingen ekstra skjønnsmessig sparebonus er lagt på A.

Claudes Ødegaard/Dasilva → Iwobi/Van Hecke: +0.12 mot rull ved 2 % nye fravær. Den lille positive forventningen må ses mot intervallet i tabellen.

Claudes Isak/Dasilva → Evanilson/Van Hecke: -0.83 mot rull ved 2 % nye fravær. Dette gir ingen forventet forbedring i denne stresstesten.

## BB10 med fritt valgt FH

R1s chiprutenett er kontrollert for A/B/C og hvert poengsett; samme rutenett er beregnet for begge Claude-pakkene. Det sammenlignes **beste BB10/FH-kombinasjon** mot beste lovlige BB/FH-kombinasjon; ingen ulovlig dobbeltchip. For valgt handling Claude_Iwobi:

| Sett | Beste BB / FH | Beste FH med BB10 | BB10 minus beste |
|---|---|---:|---:|
| codex | 18 / 16 | 18 | -1.46 |
| repo_hybrid | 12 / 13 | 13 | -2.34 |
| blend | 12 / 13 | 13 | -1.86 |

BB10 er bak i alle ni tester (A/B/C × codex/repo/blend), også når FH velges fritt. Se chipkontroll_r2.csv. Dette er nominelle prognoser; nye fravær er modellert i A–C-sammenligningen ovenfor.

## Direkte svar til Claude

1. **Van Hecke:** spiller-xP kan ikke summeres direkte til laggevinst. Dasilva er billig benkedekning, og gevinsten må betale for finansieringsbyttet og tapet av et spart FT i den fremtidige banen. De to pakkene er nå testet eksplisitt, med akkurat samme chipdatoer og autobytter som rull.

2. **Isak → Evanilson:** rå repo-xP og minuttskalert hybrid er forskjellige modeller. Å bruke førstnevnte til å foreslå byttet og sistnevnte til å rangere resten er inkonsistent. Claudes tilbaketrekking er rimelig; den komplette pakken vurderes likevel i tabellen, inkludert £2,1m frigjort bank som senere byttepolitikk kan bruke.

3. **«Alle 15 spiller nå» og BB:** grønne API-flagg er ikke 100 % spillegaranti. Den normale benken gir allerede autobyttedekning; BB-verdien er netto etter dette. Nåværende tilgjengelighet, torsdag/søndag-belastning og Groß-usikkerhet er i R1-prognosen. Senere BB slår BB10 også når FH-datoen er fri.

4. **Haaland og kalibrering:** 5,39 Codex mot 7,56 observert poeng/runde og 7,44 hybrid er en reell nivåforskjell, men beviser ikke bonusundervurdering. Motstand, xG, minutter og priors er også forskjellige, og to evalueringsrunder gir ikke grunnlag for omkalibrering. Claudes «Haaland i begge poengsett» er for sterkt: Mbeumo har høyere R10 spiller-xP i ren Codex (5,53). Haaland vinner i blandingen og repo; Gabriel er vise i den felles lagplanen.

5. **FH13:** en foreløpig modellprioritering, ikke en låst handling. Modelldisagreement om FH13/FH16 og fremtidige nyheter er gode grunner til å revurdere datoen senere, men ikke til å legge en vilkårlig informasjonsbonus oppå rull.

## Kontroll og avgrensning

Fullført: 200 verdener ved hver av 1 og 2 %, fem planer, samme fravær i begge poengsett. Største avvik mot R1s første 100 verdener: 0.00000000; totalsummene er også rekonstruert fra frosne spiller-CSV-er og planvekter (avvik <0,0001). 27 eksisterende filer er uendret. Ingen spillerpoeng_r2.csv behøves: prognosen er identisk med R1.

FT-følsomhet, uten nye fravær og med samme BB12/FH13:

- 1 FT: beste nominelle kandidat A, 619.16 / 675.08. Dette er ikke en ny skadesimulering for FT=1.

- 2 FT: beste nominelle kandidat B, 618.62 / 677.13. Dette er ikke en ny skadesimulering for FT=2.

- 3 FT: beste nominelle kandidat C, 619.82 / 675.73. Dette er ikke en ny skadesimulering for FT=3.

Kjør `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH` og `python samarbeid/gw10/codex/modell_r2.py`. Avgrenset byttesøk, konstante priser og uavhengige normale spilleutfall som i R1. Hovedhorisont til R19, ikke et bevis for globalt maksimum gjennom R38. Ingen FPL-handlinger eller git-commit utført.
