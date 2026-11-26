# Analyse R12, 2026/27

**Anbefaling for R12 (FT=3):** selg **Dasilva og Silva**, kjøp **Bogle og Justin**. Bruk 2 gratisbytter, trekk 0 poeng; bank **£0,1m**. Dette er beste søkte plan som beholder Ødegaard etter den avtalte salgsterskelen. Sett kaptein **De Cuyper**, visekaptein **Haaland**. Free Hit planlegges i **R15**. Bench Boost er allerede brukt og inngår ikke som chip i denne modellen.

**Startellever:** Trafford, Gabriel, De Cuyper, Bogle, Justin, Tavernier, Groß, Mbeumo, Barry, Isak, Haaland. **Benk:** Tzolakis, Ødegaard, Van Hecke, Rudoni (keeper først, deretter prioritert rekkefølge). R12s ARS–MCI-kamp setter Haaland opp mot Gabriel og Ødegaard; individuelle prognoser inngår i kapteinsvalget.

## Verifiserte data

API-snapshotet er fra 26. november 2026 kl. 07:44 UTC. R12-frist er 27. november kl. 18:30 UTC, R13-frist 1. desember kl. 18:30 UTC. Tropp, bank £0,4m og salgspriser er gjengitt i `../grunnlag.md`. Alle 15 egne spillere har API-status `a`; ingen har nyhet. Kun Free Hit 1 gjenstår før R20. Ingen blanke eller doble runder finnes i R12–R19.

Repo-prognosene fra botoppdateringen 23. november er frosset i `input/`: expected_points SHA-256 56c75829…481f22 og player_matches b42c7b9e…1a06c9. Prognosen `spillerpoeng.csv` inneholder 674 spillere × 8 runder = 5 392 rader.

## Antakelser og modell

Gratisbytter = 3 er antatt, ikke verifisert; 2 og 4 er testet. Prisene står fast på snapshotverdiene. Budsjett bruker salgsverdiene i `data/salgspriser.json`; Bogle/Justin-pakken gir £0,1m bank. Repoets xP for R12–R16 skaleres med de modellerte minuttene; Codex brukes R17–R19. Codex og repo_hybrid vektes 0,5 hver. Ingen kalibreringsskjevhet er lagt inn i hovedprognosen.

Minutter følger GW11-metoden. Kun Claudes CSV-overstyringer brukes: BHA/BOU/SUN/CRY ×0,95 i R12; Thiago 0,9 startandel og 74 minutter fra R14; Mbeumo 0,8/68 i R12; Dasilva 0,4/34 i R12 og 0,6/52 i R13–R14. Status `a` på Mbeumo/Dasilva er API-fakta, mens minuttene er antakelser. Dasilvas varslede skade gir grunn til varsomhet; modellen bruker likevel den oppgitte overstyringen. Kjøpsuniverset utelukker status u/n/i/s og 0 %, og status d reduserer startmuligheten.

R13 er midtukerunde fire dager etter R12. Ingen ekstra lagbasert slitasjefaktor legges til utover Claudes eksplisitte R13-minutter for Dasilva; dette er en usikkerhet.

Repoets player_matches-snapshot er 23. november og R11-raden er ikke oppdatert med R11-faktiske minutter. Derfor beregnes lagstyrke på fullførte R1–R10-kamper fra den frosne filen; R11 API-historikk brukes for minuttanslaget.

## Alternativ A–D, samme FH15

Alle tall er R12 / R12–R15 / R12–R19, vist som codex / repo_hybrid; gevinst mot A er blandingens nominelle differanse. Alle bruker eksakte autobytter og samme senere byttepolitikk.

| Plan | Handling | Trekk | Bank | R12 | R12–R15 | R12–R19 | Δ blanding mot A |
|---|---|---:|---:|---:|---:|---:|---:|
| A | Rull → ingen | 0 | £0.4m | 59.00 / 64.73 | 240.59 / 275.93 | 490.11 / 535.13 | +0.00 |
| B | Silva → Muharemović | 0 | £0.3m | 59.66 / 65.64 | 242.06 / 277.90 | 490.79 / 536.56 | +1.06 |
| C | Ødegaard, Dasilva → Justin, E.Le Fée | 0 | £0.9m | 59.86 / 66.76 | 243.15 / 278.76 | 491.97 / 537.56 | +2.14 |
| D3 | Ødegaard, Van Hecke, Dasilva → Hill, Justin, E.Le Fée | 0 | £0.3m | 59.93 / 66.53 | 243.27 / 277.56 | 492.32 / 535.90 | +1.49 |
| D4 | Ødegaard, Isak, Mbeumo, Silva → N.Jackson, Justin, B.Fernandes, E.Le Fée | 4 | £0.0m | 55.39 / 66.97 | 236.24 / 283.14 | 482.64 / 540.48 | -1.06 |

D4 med ett poengtrekk (−4) taper ca. 1,06 blandingspoeng mot A over R12–R19. Trekket forsvares ikke.

## Ødegaard-regelen og anbefaling

Beste søkte plan som selger Ødegaard mot beste søkte plan som beholder ham gir **-0.56 / +1.39** poeng i R12–R19 (salg minus behold; blanding +0.41). Kravet er over om lag +3 i begge poengsett; det er ikke oppfylt. Derfor anbefaler jeg `G_Odegaard_behold`: Dasilva, Silva → Bogle, Justin. Den gir 492.53 / 536.17 mot rulls 490.11 / 535.13.

Budsjettkontroll: £0,4m + salgsverdi £9.0m − kjøp £9.3m = £0.1m. Ingen klubb har mer enn tre spillere.

## Free Hit

Felles FH-dato i A–D er R15. FH-rutene R12–R19 sammenlignes med samme lagplan og transferpolitikk. `chiprutenett.csv` har alle datoer per alternativ og for G_keep. R15 er den felles blandingsdatoen.

## Kaptein og følsomhetstest

Grunnrangeringen i anbefalt tropp gir kaptein **De Cuyper**, vise **Haaland**. Tabellen viser topp fire kapteinsvalg ved uendrede xP; ekstra kopi er kapteins-/viceforventningen.

| Kaptein | Vise | Spiller-xP (codex / repo_hybrid) | Ekstrakopi (codex / repo_hybrid) | Blend |
|---|---|---:|---:|---:|
| De Cuyper | Haaland | 4.93 / 5.78 | 5.45 / 6.41 | 5.93 |
| Haaland | De Cuyper | 4.92 / 5.94 | 5.21 / 6.28 | 5.74 |
| Groß | Haaland | 4.62 / 5.61 | 5.13 / 6.23 | 5.68 |
| Mbeumo | Haaland | 4.19 / 4.60 | 5.17 / 5.79 | 5.48 |

Skjevhetene i fire-runders kalibreringen legges bare til i følsomhetstesten: codex +0,97 GKP <5,0, +0,39 MID 5,0–7,4 og +0,74 FWD 5,0–7,4; repo_hybrid −1,40 MID 7,5–9,9 og −4,76 FWD ≥10,0 (Haaland, n=4).

| Kapteinsvalg | Vise (codex / repo_hybrid) | Ekstrakopi (codex / repo_hybrid) | Blend |
|---|---|---:|---:|
| De Cuyper | Barry / Groß | 5.50 / 6.37 | 5.94 |
| Groß | Barry / De Cuyper | 5.57 / 6.22 | 5.89 |
| Tavernier | Barry / De Cuyper | 5.46 / 5.45 | 5.46 |
| Barry | Groß / De Cuyper | 5.68 / 5.19 | 5.43 |

Rangering og verdier med skjevhetene lagt til står i `kapteiner_folsomhet.csv`. Dette er en følsomhetstest, ikke en modelljustering. Den gjør Haaland mindre attraktiv i repo_hybrid på grunn av den ene FWD ≥10,0-gruppen; kapteinsvalget vurderes på 50/50-blandingen.

## Usikkerhet

100 parede skadeverdener ved 1 % og 2 % nye fravær per spiller/runde, med varighet 1/2/3/6 runder likt fordelt. Dette er stressrater, ikke estimerte skadefrekvenser. p10–p90 beskriver variasjon i forventet total mellom skadeverdener, ikke faktiske poeng.

| G_keep mot A | Rate | Δ codex / repo | Δ blanding | Paret p10–p90 blanding | MC-SE |
|---|---:|---:|---:|---:|---:|
| G_keep | 1% | +2.03 / +1.35 | +1.69 | +0.95 til +2.40 | 0.10 |
| G_keep | 2% | +1.97 / +1.21 | +1.59 | +0.34 til +2.77 | 0.12 |

A–D samlet: se `skadesim.csv` og `parvise.csv` for p10–p90, MC-SE og vinnerandel. Ved 2 % rangerer den ubundne 2-bytteplanen C først; etter Ødegaard-regelen blir G_keep valgt. Modelluenighet og kandidat-/byttesøk gir større usikkerhet enn MC-SE alene.

## Følsomhet for gratisbytter

| Gratisbytter | Beste plan som beholder Ødegaard | Ut → inn | Codex / repo_hybrid R12–R19 |
|---:|---|---|---:|
| 2 | 1 bytter | Silva → Muharemović | 490.79 / 536.56 |
| 3 | 2 bytter | Dasilva, Silva → Bogle, Justin | 492.53 / 536.17 |
| 4 | 3 bytter | Gabriel, Van Hecke, Mbeumo → Justin, Muharemović, B.Fernandes | 490.30 / 539.75 |

Med 2, 3 og 4 FT er beste plan under salgsterskelen vist ovenfor. De ubundne topplanene er i `ft_sensitivitet.csv`; de selger Ødegaard og oppfyller ikke kriteriet om >3 i begge poengsett.

## Kontroller og gjenskaping

Nivåkontroll: modell-xP sammenlignet med observert poengsnitt R1–R11 og rå xP fra repoet. Tidligere poeng er en kontroll, ikke en ekstra modelljustering.

| Spiller | Observert R1–R11 | Codex R12 | Repo rå R12 | Repo_hybrid R12 |
|---|---:|---:|---:|---:|
| Haaland | 6.55 | 4.92 | 6.04 | 5.94 |
| Gabriel | 6.09 | 4.61 | 5.25 | 5.26 |
| Isak | 6.00 | 4.70 | 3.31 | 3.93 |
| Mbeumo | 4.27 | 4.19 | 5.65 | 4.60 |
| B.Fernandes | 4.27 | 4.76 | 7.07 | 6.95 |

Scoring leses fra `bootstrap.json` via `game_config.scoring` (keepermål 10). Hver hovedtropp er kontrollert under codex og repo_hybrid; lovlige lag, budsjett, 5-5-3-2-posisjonskvoter, klubbtak, poengrekonstruksjon fra `spillerpoeng.csv` og eksakte autobytter er validert. Kontroll: `kontroll_r2.json` (5392 prognoser, maks avvik 0,000003, fullstendig elleversøk mot simulatorkontroll 0, 100 verdener per rate).

Kjør: `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH`; `PYTHONDONTWRITEBYTECODE=1 python samarbeid/gw12/codex/modell.py` (gjenta ved checkpoints), deretter `python samarbeid/gw12/codex/finalize.py`. Alt skrives i `samarbeid/gw12/codex/`.
