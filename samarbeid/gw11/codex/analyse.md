# Analyse R11, 2026/27

Status: fullført og kontrollert. Tallpar er codex / repo_hybrid. Prognosen bygger på frosne data 19. november, ikke senere nyheter.

**Anbefaling: Dasilva, Mbeumo → Van Hecke, E.Le Fée.** Bench Boost i R11. Kaptein **Haaland**, visekaptein **Gabriel**. Trekk 0 poeng, bank **£1.5m**. Felles planleggingsdatoer: **BB11/FH15**.

**Ellever:** Tzolakis, Gabriel, Van Hecke, De Cuyper, Ødegaard, Tavernier, Groß, Rudoni, E.Le Fée, Isak, Haaland. **Benk:** Trafford, Muharemović, Silva, Barry (keeper først; de tre utespillerne i prioritert rekkefølge).

Nominelt beste alternativ: C. Anbefalt alternativ C har nominelt -1.36 / 6.78 poeng mot rull, blanding +2.71, gjennom R19. Når alle skadeverdener er ferdige følger handlingsvalget høyest 50/50-forventning ved 2 % nye fravær, som i R10s kontrollrunde; 1 % er følsomhet.

## Verifiserte data og antakelser

API-snapshot 19. november 16:30 UTC: bank £0,4m, salgsverdi £99,5m, alle 15 i egen tropp har status a og tom nyhet. Ingen blanke/doble runder i horisonten. WC1 brukt R9 og TC1 R3; BB1/FH1 utløper R19. Frist lørdag 21. november 11:00 UTC / 12:00 norsk tid. Ingen FPL-handlinger er utført.

FT=3 er antatt, ikke verifisert; 2 og 4 testes. Priser holdes konstante. FH bevarer FT uten +1, som i forrige modell; regelen er fortsatt en antakelse. Andre runder gir +1, maks 5. Nåværende salgspriser brukes ved første salg; senere bytter følger samme prisbokføring som R10.

Minutter: vektede starter R1–R10, historiske minutter per start/innhopp og samme prior. Bare Claudes frosne overstyringer brukes: BHA/BOU/SUN/CRY ×0,95 i R12; Thiago 0,90/74 fra R14; Ødegaard 0,95/82 R11–R12. Ingen europafaktor i R11 og ingen gammel Groß-reduksjon. Alle faktiske antakelser står i minutter_antatt.csv. Jeg har ikke grunnlag for å overstyre disse; de er antakelser, ikke spillgarantier.

Kjøp utelukker status u/n/i/s og 0 %, med den eksplisitt oppgitte Thiago-returen som eneste datofestede unntak fra R14. Thiago kan ikke kjøpes R11–R13. Status d skaleres med API-prosent; øvrige ukjente returdatoer modelleres ikke.

Scoring leses fra bootstrap game_config.scoring, inkludert 10 poeng per keepermål. Repo-hybrid er repoets xP skalert med samme minutter i R11–R16 og Codex i R17–R19. Lik vekt 0,5/0,5. Ingen kalibreringsendring på grunnlag av de tre evalueringsrundene. Begge repo-filer har de oppgitte SHA-256-summene.

## A–D med samme chipdatoer

Alle hovedplaner har FT=3, BB11/FH15, samme fire-runders byttepolitikk og eksakte autobytter. Tallene inkluderer alle senere modelltrekk; A betyr rull i R11 og adaptive bytter senere. D4 er fire bytter og −4 nå, og anbefales bare dersom netto forventning er best.

| Plan | Ut → inn | Trekk nå | Bank | R11 | R11–R14 | R11–R19 | Δ blend mot A |
|---|---|---:|---:|---:|---:|---:|---:|
| C | Dasilva, Mbeumo → Van Hecke, E.Le Fée | 0 | 1.5 | 75.06 / 85.20 | 257.20 / 296.81 | 566.59 / 628.31 | +2.71 |
| D3 | Ødegaard, Dasilva, Isak → Van Hecke, N.Jackson, E.Le Fée | 0 | 2.4 | 74.23 / 85.13 | 256.31 / 294.47 | 566.09 / 626.41 | +1.51 |
| B | Muharemović → Van Hecke | 0 | 0.4 | 74.58 / 84.49 | 257.41 / 290.68 | 568.62 / 622.64 | +0.89 |
| A | ingen → ingen | 0 | 0.4 | 73.65 / 83.03 | 256.48 / 289.22 | 567.96 / 621.53 | +0.00 |
| D4 | Ødegaard, Groß, Dasilva, Isak → Rogers, Van Hecke, N.Jackson, E.Le Fée | 4 | 0.2 | 70.02 / 81.59 | 251.16 / 292.14 | 560.55 / 623.64 | -2.65 |

## Budsjett og konkret tropp

£0,4 + salg £11.9 − kjøp £10.8 = **£1.5m**. Troppen har 2 keepere, 5 forsvarere, 5 midtbanespillere og 3 spisser, maks 3 per klubb.

| Handling | Spiller | Pris £m |
|---|---|---:|
| Selg | Dasilva | 4.0 |
| Selg | Mbeumo | 7.9 |
| Kjøp | Van Hecke | 5.1 |
| Kjøp | E.Le Fée | 5.7 |

Samme konkrete tropp, ellever, benk, kaptein og vise i begge poengsett gir R11 75.06 / 85.20 med valgt chip og autobytter. Ingen modellspesifikk lagseleksjon skjuler forskjellen.

## Usikkerhet og parede skadesimuleringer

100 felles verdener ved hver av 1 % og 2 % nye fravær per spiller/runde. Nye fravær begynner R12; kjent R11-informasjon holdes fast. Varighet 1/2/3/6 runder med lik sannsynlighet. Samme fravær rammer både eide spillere og kjøpskandidater, i alle planer og begge poengsett. Fremtidige fravær er skjult for den adaptive byttepolitikken. Chipdatoene er forhåndsvalgt og felles.

Dette er stressnivåer, ikke estimerte skaderater. p10–p90 er variasjon i forventede poeng mellom skadeverdener, ikke et prediksjonsintervall for faktiske FPL-poeng. Kampflaks, modellfeil, klubbsjokk og rolleendringer kommer i tillegg.

| Plan mot A | Rate | Δ codex / repo | Δ blend | Paret p10–p90 blend | MC-SE | n |
|---|---:|---:|---:|---|---:|---:|
| B | 1% | +0.71 / +0.80 | +0.75 | -0.13 til +1.20 | 0.05 | 100 |
| C | 1% | -1.02 / +5.28 | +2.13 | +1.22 til +2.80 | 0.10 | 100 |
| D3 | 1% | -1.69 / +4.27 | +1.29 | +0.45 til +1.96 | 0.08 | 100 |
| D4 | 1% | -7.33 / +1.27 | -3.03 | -4.45 til -2.06 | 0.10 | 100 |
| B | 2% | +1.08 / +0.49 | +0.79 | -0.17 til +1.32 | 0.07 | 100 |
| C | 2% | -0.36 / +4.19 | +1.92 | +0.68 til +3.04 | 0.12 | 100 |
| D3 | 2% | -1.46 / +4.06 | +1.30 | +0.04 til +2.35 | 0.11 | 100 |
| D4 | 2% | -6.79 / +1.00 | -2.90 | -4.27 til -1.57 | 0.11 | 100 |

Ved 1% rangeres C først med 595.20 forventede poeng, 0.84 foran D3 (100 verdener).

Ved 2% rangeres C først med 593.32 forventede poeng, 0.62 foran D3 (100 verdener).

Totalsummenes p10–p90 finnes i skadesim.csv og alternativer.csv; parede forskjeller og vinnerandeler i parvise.csv. Små forskjeller må vurderes mot både modelluenighet og simuleringens standardfeil.

## E–F: Bench Boost og Free Hit

| BB | FH i sammenligning | Benk brutto | Netto BB | Total R11–R19 |
|---:|---:|---:|---:|---:|
| 11 | 15 | 16.56 / 16.72 | 13.50 / 13.60 | 566.59 / 628.31 |
| 12 | 15 | 15.14 / 16.81 | 11.57 / 12.80 | 564.66 / 627.52 |
| 13 | 15 | 14.89 / 15.00 | 12.08 / 11.97 | 565.18 / 626.68 |
| 14 | 15 | 15.35 / 15.86 | 12.53 / 12.83 | 565.62 / 627.54 |
| 15 | 14 | 15.78 / 15.71 | 12.70 / 12.46 | 567.74 / 622.73 |
| 16 | 15 | 15.43 / 14.63 | 12.51 / 11.71 | 565.60 / 626.42 |
| 17 | 15 | 16.02 / 16.02 | 13.07 / 13.07 | 566.17 / 627.78 |
| 18 | 15 | 16.48 / 16.48 | 13.49 / 13.49 | 566.58 / 628.20 |
| 19 | 15 | 16.93 / 16.93 | 13.41 / 13.41 | 566.51 / 628.12 |

BB-gevinsten er netto etter normal autobyttedekning, ikke summen av fire benkespillere. Byttepolitikken er uavhengig av BB-dato og bygger ikke målrettet opp benken. Ved kollisjon med FH flyttes FH eksplisitt i tabellen; hovedalternativene sammenlignes fortsatt med felles datoer.

| FH | Beste lovlige BB | Total R11–R19 |
|---:|---:|---:|
| 12 | 11 | 569.11 / 624.07 |
| 13 | 11 | 565.96 / 626.62 |
| 14 | 11 | 568.54 / 623.87 |
| 15 | 11 | 566.59 / 628.31 |
| 16 | 11 | 566.78 / 624.56 |
| 17 | 11 | 564.96 / 622.71 |
| 18 | 11 | 565.86 / 623.61 |
| 19 | 11 | 566.11 / 623.86 |

codex: beste datoer for denne handlingen BB11/FH12 (569.11).

repo_hybrid: beste datoer for denne handlingen BB11/FH15 (628.31).

blend: beste datoer for denne handlingen BB11/FH15 (597.45).

Datoene velges nominelt fra chiprutenettet før skadesimuleringen. Ved modelluenighet eller små marginer er dette planleggingsdatoer som bør revurderes med neste ukes data.

BB-følsomhet ved 2 % nye fravær, samme handling og samme FH som hovedplanen:

| BB | Forventet blend | BB11 minus denne | Paret p10–p90 |
|---:|---:|---:|---:|
| 11 | 593.32 | +0.00 | +0.00 til +0.00 |
| 12 | 591.48 | +1.84 | +1.36 til +2.97 |
| 13 | 590.76 | +2.56 | +1.52 til +5.54 |
| 14 | 591.07 | +2.25 | +0.87 til +4.91 |
| 16 | 590.02 | +3.30 | +1.44 til +5.64 |
| 17 | 591.35 | +1.97 | +0.48 til +4.86 |
| 18 | 591.76 | +1.56 | +0.06 til +4.30 |
| 19 | 592.57 | +0.75 | -0.21 til +1.46 |

## G: kaptein og visekaptein R11

| Kaptein | Vise | Spiller-xP | Ekstrakopi med vise |
|---|---|---:|---:|
| Haaland | Gabriel | 6.18 / 8.33 | 6.47 / 8.70 |
| Isak | Haaland | 5.23 / 4.82 | 6.12 / 6.03 |
| Gabriel | Haaland | 4.93 / 6.26 | 5.30 / 6.76 |
| Van Hecke | Haaland | 4.84 / 5.52 | 5.20 / 6.01 |

## Gratisbytter: 2, 3 eller 4

Felles BB/FH beholdes. Hele samme R11-kandidatunivers testes ved hvert FT-antall; tabellen viser beste kandidat. FT får verdi gjennom senere faktiske modellbytter, uten en skjønnsmessig sparebonus.

| FT | Beste plan | Ut → inn | Trekk | R11–R19 |
|---:|---|---|---:|---:|
| 2 | C | Dasilva, Mbeumo → Van Hecke, E.Le Fée | 0 | 569.08 / 623.33 |
| 3 | C | Dasilva, Mbeumo → Van Hecke, E.Le Fée | 0 | 566.59 / 628.31 |
| 4 | C | Dasilva, Mbeumo → Van Hecke, E.Le Fée | 0 | 566.93 / 626.48 |

FT-følsomheten er nominell; skadesimuleringen gjelder 3 FT. Samme tobyttepakke C vinner ved 2, 3 og 4 FT. At 4 FT gir lavere modelltotal enn 3 FT skyldes at den uendrede, heuristiske byttepolitikken velger en annen senere bane; et ekstra gratisbytte har ikke negativ iboende verdi. Dette begrenser presisjonen i langtidsrangeringen. Kontroller tallet i FPL før en plan med tre bytter låses.

## Nivåkontroll av toppspillere

| Spiller | Observert snitt R1–R10 | Codex R11 | Repo rå R11 | Repo-hybrid R11 | Snitt R11–R16 codex / repo |
|---|---:|---:|---:|---:|---:|
| Gabriel | 6.60 | 4.93 | 6.27 | 6.26 | 4.81 / 5.90 |
| Rogers | 5.20 | 4.00 | 5.68 | 5.37 | 4.04 / 5.32 |
| Watkins | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 / 0.00 |
| Tavernier | 5.80 | 4.83 | 5.55 | 5.49 | 4.82 / 5.12 |
| Palmer | 4.70 | 4.18 | 5.08 | 5.34 | 4.24 / 5.28 |
| Isak | 6.10 | 5.23 | 4.14 | 4.82 | 4.82 / 4.31 |
| Haaland | 7.00 | 6.18 | 8.49 | 8.33 | 5.91 / 7.82 |
| B.Fernandes | 4.50 | 4.01 | 5.85 | 5.58 | 4.35 / 6.10 |
| Mbeumo | 4.60 | 4.47 | 4.65 | 4.67 | 4.84 / 5.12 |

Observert snitt er poeng per runde, ikke per opptreden. Modellen bruker xG/xA, historiske priors, motstand og minutter; tidligere poengsnitt er en kontroll, ikke et kalibreringsmål. Bonusmetoden er uendret. Modellenes nivåforskjell er reell modellusikkerhet.

## Metode, avgrensning og gjenskaping

Poengberegning, minuttprior, eksakt integrasjon av uavhengige spilleutfall, lovlige autobytter, kaptein/vice og byttepolitikk er videreført fra R10. Hovedtabellene søker alle lovlige ellevere/benkerekkefølger. Skadeverdener bruker forrige ukes begrensede elleverkandidater med eksakt forventning for hver kandidat.

Først foreslås 1–4 bytter fra heltallsoptimering over én, fire og ni runder, begge poengsett og blandingen; alle lovlige enkeltbytter brukes også til forslag og finansieringspar. Forslagene rangeres på rullerende eierbaner, først FH16, deretter felles chipdatoer. «Beste» betyr beste i dette avgrensede søket, ikke et bevist globalt optimum.

Senere byttesøk: 12 beste + 4 billigste per posisjon, enkeltbytter/finansieringspar, tre forslag vurderes eksakt. Gratisbytte krever >1 poeng over fire runder, med terskel 0 ved 5 FT/R19; betalt bytte krever >5 brutto. FH bruker samme heltallsforslag og lokale forbedring som R10.

Horisonten slutter R19. Det gjør at denne modellen ikke direkte verdsetter tropp og lagrede bytter ved inngangen til R20 eller maksimerer hele R11–R38. En terminalverdi og målrettet oppbygging før BB kunne vært undersøkt senere; ingen slike modellendringer er gjort her.

Kjør med Anaconda: `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH`, så `PYTHONDONTWRITEBYTECODE=1 python samarbeid/gw11/codex/modell.py`. Gjenta til status.json sier fullført. Hver kommando har tidsbudsjett 420 sekunder og lagrer etter hvert delarbeid. `--stage report` oppdaterer rapporten; `--stage check` gjentar kontrollene. Slett checkpoints bare hvis hele beregningen skal kjøres fra bunnen med de samme fryste inputene.

spillerpoeng.csv inneholder alle 672 spillere × 9 runder = 6048 rader. Prognosefilenes SHA-256 kontrolleres mot filene fra 19. november. Alle skrivinger skjer i codex/. Ingen nettverk, installasjon, git eller FPL-handlinger.

Kontroll: {"status": "OK", "spillerpoeng_uendret": true, "spillere": 672, "rader": 6048, "maks_planavvik_fra_CSV": 4.893570576314232e-06, "maks_full_mot_sim_elleversok": 0.0, "verdener_per_rate": 100, "rater": [0.01, 0.02], "planer": 5, "BB": 11, "FH": 15, "valgt": "C"}

Runde 2: se [kontroll.md](kontroll.md) for kritikken av Claude og [bb_skade.csv](bb_skade.csv) for den parede BB11/18/19-testen av A og B med FH12 og FH15.
