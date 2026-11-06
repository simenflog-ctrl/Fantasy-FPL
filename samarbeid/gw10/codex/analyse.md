# Analyse R10, 2026/27

Status: fullført og kontrollert. Tallpar er codex / repo_hybrid.

**Modellanbefaling: B; ikke Bench Boost nå; foreløpig BB i R12. Free Hit R13.** Selg Tzolakis; kjøp Verbruggen. Trekk R10: 0. Bank etter: £0.5m.

**Ellever:** Trafford, Gabriel, De Cuyper, Muharemović, Ødegaard, Tavernier, Groß, Mbeumo, Barry, Isak, Haaland. **Kaptein:** Haaland. **Visekaptein:** Gabriel. **Benk:** Verbruggen, Silva, Rudoni, Dasilva (keeper først, deretter prioritert utespillerrekkefølge).

## Verifiserte data og eksplisitte antakelser

API-snapshot 6. november: bank £0,4m; salgsverdi £99,1m; 15 spillere med status a. WC1 brukt R9, TC1 brukt R3. FH1/BB1 utløper R19. Ingen blanke/doble runder i horisonten. Frist 6. november 18:30 UTC / 19:30 norsk tid. Ingen lagendringer er utført.

FT=2 antas, og 1/3 testes nedenfor. Prisene holdes konstante. FH bevarer FT uten ekstra opptjening (uverifisert regel). Andre runder gir +1, maksimalt 5. Alle kjøp må ha tillatt API-status og minstekrav til forventet startandel; d justeres med API-prosent. Ingen antatt friskdato for dagens langtidsskadde/0 %-spillere: disse holdes utenfor hele horisonten. Dette kan undervurdere fremtidige kjøpsmuligheter.

Spilletid står i minutter_antatt.csv og leses som input ved senere kjøring. Baseline bruker vektede starter R1–R9, historiske minutter ved start/innhopp og en liten prior. BHA/BOU/SUN/CRY: R10 p_start og minutter ×0,95 etter torsdag–søndag. Groß: ytterligere ×0,85 etter fot-smell uten diagnose. Dette er antakelser, ikke bekreftet rotasjon/skadegrad. Claude kan overstyre CSV-en. Grealish og Crooks er null i R10; Morita/Toth holdes ute ved ukjent retur.

Poengreglene leses fra bootstrap game_config.scoring, inkludert 10 poeng per keepermål. Ingen tilpasning etter kalibreringsloggen (bare to runder). Repo-filen dekker R10–R15; repo_hybrid bruker Codex R16–R19. Begge skaleres med samme eksplisitte minutter. Repoets rå xP er frosset i input/expected_points.csv.

## A–D: rangerte konkrete planer

Samme FH13, samme fire-runders byttepolitikk og eksakte autobytter i alle planer; BB velges blant alle øvrige runder. Rangering er lik vekt på de to poengsettene. «Beste» betyr beste i det avgrensede søket, ikke bevist globalt optimum.

| Plan | Ut → inn | BB | Trekk R10 | Bank | R10 | R10–R13 | R10–R19 | Skade p10–p90, blend |
|---|---|---:|---:|---:|---:|---:|---:|---|
| B | Tzolakis → Verbruggen | 12 | 0 | 0.5 | 60.8 / 69.6 | 253.2 / 293.8 | 618.6 / 677.1 | 635.1–647.3 |
| C | Groß, Muharemović → Van Hecke, E.Le Fée | 11 | 0 | 0.7 | 61.1 / 69.6 | 254.3 / 292.8 | 620.0 / 675.6 | 634.8–647.0 |
| A | ingen → ingen | 12 | 0 | 0.4 | 60.8 / 69.6 | 253.7 / 292.5 | 619.5 / 675.4 | 634.0–647.2 |
| D3 | Groß, Dasilva, Isak → Rogers, Van Hecke, Gonzalo | 18 | 4 | 0.3 | 55.9 / 66.4 | 235.0 / 277.2 | 611.0 / 673.2 | 630.1–642.1 |
| D4 | Groß, Dasilva, Muharemović, Silva → Van Hecke, Iwobi, Justin, Murillo | 12 | 8 | 0.0 | 53.1 / 62.0 | 245.6 / 283.2 | 611.4 / 665.7 | 624.8–637.7 |

Gjennomsnittlig fordel mot rull er bare +0.44 poeng. Handlingsanbefalingen følger dette nominelle modellgjennomsnittet, men er svak når poengsettene eller skadestressen er uenige. Ingen sikker gevinst ved å bruke FT nå er påvist.

Valgt plan minus rull: -0.9 / 1.7 gjennom R19. D3/D4 er testede 3-/4-bytteplaner med alle trekk inkludert; et trekk anbefales bare hvis netto forventning er høyest. FT3 gjør trebytteplanen gratis.

## Budsjettkontroll

£0,4m + salg £4.7m − kjøp £4.6m = **£0.5m**. Salg bruker salgspriser.json, ikke markedsverdi. Troppen er kontrollert for 2/5/5/3 og maks tre per klubb.

| Handling | Spiller | Pris £m |
|---|---|---:|
| Selg | Tzolakis | 4.7 |
| Kjøp | Verbruggen | 4.6 |

## E: Bench Boost nå eller senere

Fast konkret R10-handling B, samme eierskapsbane og FH13. Politikken optimaliserer normal ellever over neste fire runder, og er med vilje uavhengig av BB-dato. Dermed får ingen dato særskilt benkeopprusting. Dette er en kontrollert sammenligning, og kan undervurdere målrettet oppbygging før en senere BB.

Benkens bruttopoeng omfatter fire spillere. Netto BB-gevinst trekker fra vanlig autobytteverdi og tillater optimalt kaptein/vice-valg. At alle forventes å spille betyr ikke at alle har 100 % p_play.

| BB-runde | Benk brutto | Netto BB | Total R10–R19 | BB10 minus denne |
|---|---:|---:|---:|---:|
| 10 | 13.6 / 15.0 | 9.4 / 10.5 | 616.0 / 674.1 | 0.0 / 0.0 |
| 11 | 15.2 / 16.0 | 12.1 / 12.8 | 618.7 / 676.4 | -2.7 / -2.3 |
| 12 | 15.3 / 17.2 | 12.0 / 13.5 | 618.6 / 677.1 | -2.6 / -3.0 |
| 13 (FH, BB ikke mulig) | 12.9 / 14.4 | 10.7 / 11.9 | – | – |
| 14 | 13.9 / 16.0 | 10.9 / 12.7 | 617.5 / 676.3 | -1.5 / -2.2 |
| 15 | 15.0 / 14.4 | 12.0 / 11.5 | 618.7 / 675.2 | -2.6 / -1.0 |
| 16 | 14.7 / 14.7 | 11.5 / 11.5 | 618.2 / 675.1 | -2.1 / -1.0 |
| 17 | 14.6 / 14.6 | 11.5 / 11.5 | 618.1 / 675.1 | -2.1 / -1.0 |
| 18 | 14.9 / 14.9 | 11.8 / 11.8 | 618.4 / 675.4 | -2.3 / -1.3 |
| 19 | 15.1 / 15.1 | 11.3 / 11.3 | 618.0 / 674.9 | -1.9 / -0.8 |

BB13 kolliderer med hovedplanens FH13. For å vurdere også denne BB-datoen flyttes FH til R16 i **begge** sammenligningsbanene: BB10 617.0 / 670.1, BB13 618.5 / 670.6; forskjell -1.5 / -0.5. Benk brutto R13: 13.6 / 13.9, netto BB 10.9 / 11.0. Dermed er alle R11–R19 vurdert uten ulovlig dobbeltchip.

Full benktabell for A–D: benk_per_runde.csv. Alle kombinasjoner av FH11–19 og lovlig BB10–19 finnes i chiprutenett.csv.

## Parede nye fravær og usikkerhet

Samme tilfeldige spillerfravær i alle alternativer, inkludert ikke-eide kjøpskandidater. Nye fravær begynner R11 (R10 bygger på den oppgitte informasjonen), med 1/2/3/6 runders varighet, lik sannsynlighet. Ved hver frist er bare allerede inntruffet fravær og retur kjent; nye fremtidige fravær er skjult. Fire-runders byttepolitikk reparerer adaptivt med tilgjengelige FT. BB-/FH-datoer velges på forhånd, ikke med fasit i hver verden.

1–3 % er stressnivåer, ikke estimerte skaderater. p10–p90 måler variasjon i forventede poeng mellom skadeverdener, ikke intervallet for faktiske FPL-poeng. Kampflaks, modellfeil, felles klubbsjokk og uventede rolleendringer kommer i tillegg. Modellenes forskjell i A–D-tabellen viser en annen, viktig usikkerhet.

| Nye fravær | Mot BB | Sett | BB10 minus senere | Endring fra uten nye skader | Paret p10–p90 | MC-SE |
|---|---:|---|---:|---:|---|---:|
| 1% | 12 | codex | -1.98 | +0.60 | -2.58 til +0.81 | 0.13 |
| 1% | 12 | repo_hybrid | -2.30 | +0.71 | -3.01 til +1.06 | 0.15 |
| 1% | 19 | codex | -1.97 | -0.06 | -2.45 til -1.73 | 0.05 |
| 1% | 19 | repo_hybrid | -0.88 | -0.06 | -1.36 til -0.63 | 0.05 |
| 1% | 13 (FH16) | codex | -0.94 | +0.58 | -1.52 til +1.87 | 0.15 |
| 1% | 13 (FH16) | repo_hybrid | +0.12 | +0.57 | -0.45 til +3.12 | 0.16 |
| 2% | 12 | codex | -1.51 | +1.06 | -2.58 til +1.17 | 0.17 |
| 2% | 12 | repo_hybrid | -1.76 | +1.25 | -3.01 til +1.15 | 0.19 |
| 2% | 19 | codex | -1.99 | -0.08 | -2.64 til -1.36 | 0.06 |
| 2% | 19 | repo_hybrid | -0.89 | -0.08 | -1.54 til -0.27 | 0.06 |
| 2% | 13 (FH16) | codex | -0.53 | +0.99 | -1.52 til +1.91 | 0.18 |
| 2% | 13 (FH16) | repo_hybrid | +0.55 | +1.00 | -0.48 til +3.32 | 0.19 |
| 3% | 12 | codex | -0.96 | +1.61 | -2.58 til +1.24 | 0.21 |
| 3% | 12 | repo_hybrid | -1.15 | +1.86 | -3.01 til +1.47 | 0.24 |
| 3% | 19 | codex | -1.94 | -0.03 | -2.68 til -0.96 | 0.08 |
| 3% | 19 | repo_hybrid | -0.84 | -0.03 | -1.59 til +0.14 | 0.08 |
| 3% | 13 (FH16) | codex | +0.12 | +1.64 | -1.52 til +2.08 | 0.22 |
| 3% | 13 (FH16) | repo_hybrid | +1.21 | +1.66 | -0.64 til +3.45 | 0.23 |

100 parede verdener per skaderate. Alle senere BB-datoer og alle hovedalternativer finnes i skadesim.csv; råtrekk i skadetrekk.csv.

Forhåndsvalgt BB per plan, 2 % nye fravær (gjennomsnittlig forventning):

| Plan | Codex / repo |
|---|---:|
| A | 615.0 / 670.0 |
| B | 613.6 / 671.0 |
| C | 615.1 / 669.4 |
| D3 | 606.5 / 667.5 |
| D4 | 606.2 / 659.6 |

Nominal rangering velger B; sentral skadestress rangerer A høyest. Skadesannsynligheten er en antakelse, ikke estimert, så se forskjellens størrelse før konklusjonen tolkes som robust.

## F: Free Hit sammen med BB

| FH | Beste BB | R10–R19 |
|---:|---:|---:|
| 11 | 12 | 616.9 / 673.7 |
| 12 | 11 | 614.9 / 671.4 |
| 13 | 12 | 618.6 / 677.1 |
| 14 | 11 | 617.9 / 670.9 |
| 15 | 12 | 617.9 / 675.9 |
| 16 | 12 | 619.7 / 672.8 |
| 17 | 12 | 618.8 / 671.9 |
| 18 | 12 | 618.5 / 671.5 |
| 19 | 12 | 618.4 / 671.5 |

## G: kaptein og visekaptein R10

Spiller-xP er ubetinget. Ekstrakopi inkluderer reservekaptein dersom kapteinen får null minutter. Samme konkrete ellever testes i begge poengsett.

| Kaptein | Vice | Spiller-xP | Ekstrakopi med vice |
|---|---|---:|---:|
| Haaland | Gabriel | 5.4 / 7.4 | 5.7 / 7.9 |
| Gabriel | Haaland | 5.4 / 6.7 | 5.7 / 7.2 |
| Mbeumo | Haaland | 5.5 / 6.0 | 5.9 / 6.5 |
| Isak | Haaland | 4.9 / 4.5 | 5.8 / 5.7 |

## FT-følsomhet

| FT nå | Beste antall R10-bytter | BB | Trekk R10 | R10–R19 |
|---:|---:|---:|---:|---:|
| 1 | 0 | 12 | 0 | 619.2 / 675.1 |
| 2 | 1 | 12 | 0 | 618.6 / 677.1 |
| 3 | 2 | 11 | 0 | 620.0 / 675.6 |

ft_sensitivitet.csv har alle kandidatplaner. FT-verdien oppstår gjennom senere faktiske modellbytter; ingen ekstra vilkårlig sparebonus legges på.

## Groß og toppspillernes nivå

Groß-testen endrer R10 p_start, forventede minutter og begge xP-sett proporsjonalt; p_play beregnes på nytt. Senere minutter holdes faste. Eksakte autobytter og senere byttepolitikk beregnes på nytt. Kandidatlisten for R10 er fast; et helt nytt best kjøp ved alvorlig skade krever nytt søk.

| Groß p_start | Minutter | Beste BB for valgt handling | BB10 total | BB19 total |
|---:|---:|---:|---:|---:|
| 0.000 | 0.0 | 12 | 612.7 / 670.1 | 617.5 / 673.9 |
| 0.500 | 43.9 | 12 | 614.9 / 672.8 | 617.8 / 674.6 |
| 0.758 | 66.5 | 12 | 616.0 / 674.1 | 618.0 / 674.9 |
| 0.900 | 79.0 | 12 | 616.7 / 674.9 | 618.0 / 675.1 |
| Spiller | Observert snitt R1–R9 | Codex R10 | Repo rå R10 | Repo justert R10 | Codex / repo R10–R15 snitt |
|---|---:|---:|---:|---:|---:|
| Gabriel | 6.44 | 5.39 | 6.73 | 6.72 | 4.77 / 5.91 |
| Rogers | 5.56 | 3.95 | 5.59 | 5.28 | 3.98 / 5.30 |
| Watkins | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 / 0.00 |
| Tavernier | 6.11 | 4.72 | 5.60 | 5.26 | 4.71 / 5.07 |
| Palmer | 5.00 | 4.21 | 5.00 | 5.27 | 4.24 / 5.29 |
| Isak | 5.89 | 4.86 | 3.81 | 4.45 | 4.71 / 4.13 |
| Haaland | 7.56 | 5.39 | 7.59 | 7.44 | 5.88 / 7.91 |
| B.Fernandes | 3.89 | 4.49 | 6.34 | 6.01 | 4.20 / 5.84 |
| Mbeumo | 4.89 | 5.53 | 5.95 | 5.99 | 5.16 / 5.77 |

Salah finnes ikke i de 670 bootstrap-spillerne (heller ikke ved søk i fullt navn); observert snitt og prognose kan derfor ikke kontrolleres. Palmer-raden gjelder Chelsea-spilleren (ID 154), ikke navnebroren ID 301.

Observert snitt er poeng/9 runder, ikke poeng per opptreden. Prognosen bruker xG/xA, historiske priors, motstand og minutter; den skal derfor ikke nødvendigvis treffe tidligere poengsnitt. Bonus er krympet mot historikk i Codex, mens repoets nivå bevares etter minuttskalering. Se kalibrering.csv for bonuskontrollen.

## Metode, søkegrenser og etterprøvbarhet

modell.py er en selvstendig videreføring av gw09/codex/modell_r2.py: identisk eksakt integrator for uavhengige spilleutfall, lovlige autobytter, kort innhopp som blokkerer auto, samt kaptein/vice. Keeper byttes bare mot keeper. Hovedtabellene søker alle lovlige ellevere og benkerekkefølger. Simuleringen bruker R2s begrensede elleverkandidater, men eksakt forventning for hver kandidat.

R10-kandidater inkluderer alle lovlige enkeltbytter som forslag, finansieringspar fra de beste enkeltbyttene og heltallsoptimering med 1–4 bytter, tre horisonter og begge poengsett samt blanding. Kandidatene rangeres med en rullerende eierbane. FH-søket bruker heltallsforslag fra hver dato og begge modeller, deretter lokal forbedring. Senere byttesøk bruker 12 beste + 4 billigste per posisjon, enkeltbytter og avgrensede finansieringspar; de tre beste forslagene vurderes eksakt. Gratisbytte krever >1 poeng i fire-rundersvinduet (0 ved 5 FT/R19), betalt bytte >5 brutto. BB tas ikke med i bytteobjektivet. Søket er avgrenset og hovedhorisonten stopper ved chiputløpet R19, ikke sesongslutt R38. Ingen påstand om globalt maksimum for hele sesongen.

Kjør: `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH` og `python samarbeid/gw10/codex/modell.py`. Standard 100 parede verdener per stressrate; `--draws` styrer antallet. Minuttfilen bevares og brukes ved kjøring; andre resultater gjenskapes. Ingen nettverk eller installasjon. Alle skrivinger skjer i codex/.

Kontroll: alle 670 spillere × 8 runder = 5360 rader i spillerpoeng.csv (R10–R17). R18–19 ligger separat. Budsjett, posisjoner, klubbgrense og poengvekter kontrolleres automatisk. Rapporten genereres direkte fra de samme planene som alternativer.csv.
