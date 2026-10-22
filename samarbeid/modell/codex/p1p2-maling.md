# Uavhengig måling av P1 B1 og P2

**P2: UAVKLART. P1 B1: UAVKLART.**

Behold `BONUS_TAU_FIXED = None`. Tau 7 var det låste utviklingsvalget, men er ikke godkjent for aktivering. Behold `SUB_GIVEN_NO_START = False`. Standardverdiene er ikke endret; ingen commit.

## Låst metode og gjennomføring

Lest diffene `7502dcd` og `87a16db`. Kravene er hentet uendret fra `samarbeid/modell/plan.md` og `claude/p1-bonus-forhandsregistrering.md`; hasher er lagret i `p1p2_metode_for_kjoring.json`. P2 er testet isolert med bonusflagget på `None`; B1 med P2 av. Baseline er `SUB_GIVEN_NO_START=False`, `BONUS_TAU_FIXED=None`.

Alle tre sesonger, **GW8–38**, 72 583 spiller–kamp-prognoser per hovedmodell og 93 runder. Paring er identisk sesong/spiller/fixture og faktiske utfall. Effekt er kandidat minus baseline: negativ MSE er bedre, positiv topp-k er bedre. SE bruker de samme fire-runders blokkene innen sesong som P0: 8 blokker per år, 24 samlet. «±» betyr én SE, ikke et 95 %-intervall. Topp-k er poengsnitt for k valgte spiller–kamp-rader per runde; ikke en lovlig budsjettert ellever.

StringIO-broen er fjernet: historikk gis som `last_season` direkte til Claudes produksjonsfunksjon. Tau-rutenettet deler identiske minutter/lagstyrker/kampprogram, men **hver tau kjøres gjennom produksjonens `forecast` og flagget `BONUS_TAU_FIXED`**. En paritetstest mot separat full flaggkjøring består. Ny baseline mot P0 har største xP-avvik **1.8e-15**; `p1p2_p0_paritet.csv` dokumenterer dette. Ingen andre prediksjonsformler er innført.

## P1: utviklingsvalg før kontrollåret

Minimering av bonus-MSE, akkurat rutenettet {4, 5, 6, 7, 8, 10, 12}, bare på 2023/24 og 2024/25. Samlet verdi er vektet med antall spiller–kamper; ved likhet velges lavere tau. Verken total-MSE eller topp-k velger tau.

| Fast tau | Bonus-MSE 2023/24 | Bonus-MSE 2024/25 | Utvikling samlet |
| --- | --- | --- | --- |
| 4 | 0.173981 | 0.187541 | 0.180509 |
| 5 | 0.170301 | 0.180461 | 0.175192 |
| 6 | 0.169599 | 0.177618 | 0.173460 |
| **7** | 0.169963 | 0.177196 | 0.173445 |
| 8 | 0.170653 | 0.177817 | 0.174102 |
| 10 | 0.172097 | 0.179757 | 0.175784 |
| 12 | 0.173288 | 0.181490 | 0.177236 |

**Låst tau = 7.** Låsen ble skrevet **2026-10-22T20:56:35.540256+00:00**, før 2025/26 ble lastet. `p1_tau_last.json` lagrer lasteloggen og hash av utviklingstabellen. På kontrollåret kjøres bare den låste verdien, ingen rutenettsøk. Historiske kontrollårsdata er sett i tidligere prosjektarbeid, men ingen B1-kontrollmåling er brukt til dette tau-valget. Samlede B1-tall inkluderer utviklingsårene og er derfor ikke en ny uavhengig bekreftelse; kontrollåret vises separat.

## P2: totalpoeng og topp-k

| Sesong | N | Total-MSE før → etter | Δ total-MSE ± SE | MSE-reduksjon | Forbedring/SE | Topp10 før → etter (Δ ± SE) | Topp20 før → etter (Δ ± SE) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2023-24 | 24845 | 3.717964 → 3.709829 | -0.008135 ± 0.002319 | +0.219 % | 3.51 | 4.997 → 5.032 (+0.035484 ± 0.013360) | 4.608 → 4.634 (+0.025806 ± 0.045514) |
| 2024-25 | 23064 | 4.464954 → 4.457488 | -0.007467 ± 0.003060 | +0.167 % | 2.44 | 5.365 → 5.329 (-0.035484 ± 0.033027) | 4.663 → 4.679 (+0.016129 ± 0.033052) |
| 2025-26 | 24674 | 3.785241 → 3.776589 | -0.008652 ± 0.002295 | +0.229 % | 3.77 | 4.884 → 4.871 (-0.012903 ± 0.048090) | 4.363 → 4.303 (-0.059677 ± 0.036633) |
| alle | 72583 | 3.978198 → 3.970100 | -0.008099 ± 0.001413 | +0.204 % | 5.73 | 5.082 → 5.077 (-0.004301 ± 0.020021) | 4.545 → 4.539 (-0.005914 ± 0.023098) |

**Konklusjon P2: UAVKLART.** Ikke oppfylt: Minst 0,5 % lavere total-MSE samlet. Samlet gevinst er 0.204 % og 5.73 blokk-SE. Dette er en målt liten gevinst, men terskelen på 0,5 % senkes ikke etter resultatet.

### Minutt- og innhoppsmekanismen

Felles utvalg: prognoser med **p_start < 0,6**; p_start er identisk av/på. `p_play` sammenlignes med 1[minutter > 0], minutter med faktiske minutter. `p_sub = p_play − p_start` sammenlignes med 1[ikke start og minutter > 0]. Dette er ubetinget innhoppssannsynlighet per kamp, ikke etterhåndsfiltrering til dem som faktisk spilte. Sannsynlighets-MSE er Brier-score. Delgruppene 0–0,2, 0,2–0,4 og 0,4–0,6 finnes i CSV-en i tillegg til totalutvalget under.

| Sesong | Mål | N | Predikert før → P2 | Faktisk | Bias før ± SE | Bias P2 ± SE | Δ Brier/MSE ± SE |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2023-24 | p_play | 19497 | 0.2280 → 0.2530 | 0.2367 | -0.0088 ± 0.0025 | +0.0163 ± 0.0023 | -0.00223 ± 0.00028 |
| 2023-24 | p_sub | 19497 | 0.0889 → 0.1139 | 0.1100 | -0.0212 ± 0.0023 | +0.0039 ± 0.0023 | -0.00141 ± 0.00024 |
| 2023-24 | minutes | 19497 | 12.7636 → 13.2189 | 12.0376 | +0.7260 ± 0.1763 | +1.1812 ± 0.1729 | -2.17099 ± 0.47749 |
| 2024-25 | p_play | 17357 | 0.2500 → 0.2780 | 0.2534 | -0.0034 ± 0.0038 | +0.0246 ± 0.0036 | -0.00141 ± 0.00028 |
| 2024-25 | p_sub | 17357 | 0.1017 → 0.1296 | 0.1259 | -0.0243 ± 0.0014 | +0.0037 ± 0.0011 | -0.00152 ± 0.00030 |
| 2024-25 | minutes | 17357 | 13.6744 → 14.1923 | 12.1883 | +1.4861 ± 0.2636 | +2.0039 ± 0.2628 | -0.86109 ± 0.37430 |
| 2025-26 | p_play | 19077 | 0.2276 → 0.2541 | 0.2320 | -0.0044 ± 0.0030 | +0.0221 ± 0.0030 | -0.00159 ± 0.00029 |
| 2025-26 | p_sub | 19077 | 0.0885 → 0.1149 | 0.1104 | -0.0219 ± 0.0017 | +0.0045 ± 0.0019 | -0.00142 ± 0.00042 |
| 2025-26 | minutes | 19077 | 12.6421 → 13.1357 | 11.4507 | +1.1914 ± 0.2887 | +1.6850 ± 0.2898 | -1.02738 ± 0.77340 |
| alle | p_play | 55931 | 0.2347 → 0.2611 | 0.2403 | -0.0056 ± 0.0018 | +0.0208 ± 0.0018 | -0.00175 ± 0.00017 |
| alle | p_sub | 55931 | 0.0927 → 0.1191 | 0.1151 | -0.0224 ± 0.0011 | +0.0040 ± 0.0010 | -0.00145 ± 0.00018 |
| alle | minutes | 55931 | 13.0048 → 13.4926 | 11.8842 | +1.1206 ± 0.1504 | +1.6084 ± 0.1524 | -1.37443 ± 0.34210 |

P2 retter i stor grad innhoppsnivået: samlet predikert p_sub går fra 0.0927 til 0.1191, mot faktisk 0.1151. Samtidig øker overvurderingen av samlet p_play og gjennomsnittsminutter. Brier-score og minutt-MSE blir likevel lavere; nivåbias og kvadratfeil måler ulike egenskaper. Mekanismen er derfor ikke bedre kalibrert på alle mål.

En bedre mekanismediagnose erstatter ikke kravene til total-MSE og topp-k. Historiske tilgjengelighetsflagg mangler fortsatt; alle modeller har samme begrensning og samme rekonstruksjon av roster/priorer.

## B1 med låst tau: totalpoeng, bonus og topp-k

| Sesong | N | Total-MSE før → etter | Δ total-MSE ± SE | MSE-reduksjon | Forbedring/SE | Topp10 før → etter (Δ ± SE) | Topp20 før → etter (Δ ± SE) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2023-24 | 24845 | 3.717964 → 3.711798 | -0.006166 ± 0.006424 | +0.166 % | 0.96 | 4.997 → 5.139 (+0.141935 ± 0.110337) | 4.608 → 4.782 (+0.174194 ± 0.080525) |
| 2024-25 | 23064 | 4.464954 → 4.449972 | -0.014982 ± 0.006089 | +0.336 % | 2.46 | 5.365 → 5.239 (-0.125806 ± 0.104257) | 4.663 → 4.605 (-0.058065 ± 0.074591) |
| 2025-26 | 24674 | 3.785241 → 3.780718 | -0.004523 ± 0.003793 | +0.119 % | 1.19 | 4.884 → 4.632 (-0.251613 ± 0.142075) | 4.363 → 4.402 (+0.038710 ± 0.061224) |
| alle | 72583 | 3.978198 → 3.969789 | -0.008409 ± 0.003201 | +0.211 % | 2.63 | 5.082 → 5.003 (-0.078495 ± 0.074362) | 4.545 → 4.596 (+0.051613 ± 0.045137) |

| Sesong | Bonus-MSE før | Etter | Δ ± blokk-SE | Reduksjon |
| --- | --- | --- | --- | --- |
| 2023-24 | 0.174138 | 0.169963 | -0.004175 ± 0.000993 | +2.40 % |
| 2024-25 | 0.184733 | 0.177196 | -0.007537 ± 0.001432 | +4.08 % |
| 2025-26 | 0.178449 | 0.171182 | -0.007267 ± 0.001274 | +4.07 % |
| alle | 0.178970 | 0.172676 | -0.006295 ± 0.000757 | +3.52 % |

### Premiumkalibrering før/etter

Pris er siste observerte pris fra en tidligere GW. Kun FWD/MID i [8,10) og ≥10 m; ukjent tidligere pris utelates. «Bias» er predikert minus faktisk. Absolutt bias sammenligner størrelsen, slik at både over- og undervurdering straffes. CSV-en inneholder før/etter-bias, tilhørende blokk-SE, parvis biasendring og bonus-/total-MSE per celle.

| Sesong | Pris | Pos | N | Faktisk bonus / total | Pred. bonus før → etter | Pred. total før → etter | Δ absolutt bonusbias ± SE | Δ absolutt totalbias ± SE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2023-24 | 8-10 | FWD | 57 | 0.526 / 4.544 | 0.455 → 0.257 | 4.027 → 3.830 | +0.198 ± 0.028 | +0.198 ± 0.028 |
| 2023-24 | 8-10 | MID | 188 | 0.516 / 4.505 | 0.420 → 0.257 | 4.317 → 4.154 | +0.163 ± 0.010 | +0.163 ± 0.010 |
| 2023-24 | >=10 | FWD | 62 | 0.371 / 2.645 | 0.536 → 0.278 | 3.481 → 3.224 | -0.072 ± 0.252 | -0.257 ± 0.089 |
| 2023-24 | >=10 | MID | 68 | 0.485 / 4.279 | 0.333 → 0.206 | 3.771 → 3.644 | +0.127 ± 0.030 | +0.127 ± 0.030 |
| 2024-25 | 8-10 | FWD | 78 | 0.808 / 4.846 | 0.707 → 0.391 | 4.805 → 4.490 | +0.315 ± 0.045 | +0.315 ± 0.045 |
| 2024-25 | 8-10 | MID | 167 | 0.425 / 3.760 | 0.435 → 0.271 | 3.814 → 3.650 | +0.144 ± 0.170 | +0.057 ± 0.575 |
| 2024-25 | >=10 | FWD | 31 | 0.387 / 3.677 | 1.560 → 0.817 | 6.539 → 5.796 | -0.743 ± 0.155 | -0.743 ± 0.155 |
| 2024-25 | >=10 | MID | 93 | 0.860 / 5.398 | 1.753 → 0.880 | 6.935 → 6.062 | -0.873 ± 0.073 | -0.873 ± 0.073 |
| 2025-26 | 8-10 | FWD | 98 | 0.541 / 3.612 | 0.153 → 0.140 | 2.892 → 2.879 | +0.013 ± 0.006 | +0.013 ± 0.006 |
| 2025-26 | 8-10 | MID | 260 | 0.354 / 2.869 | 0.317 → 0.191 | 2.820 → 2.694 | +0.126 ± 0.030 | +0.126 ± 0.030 |
| 2025-26 | >=10 | FWD | 62 | 0.484 / 3.258 | 1.109 → 0.561 | 4.305 → 3.757 | -0.548 ± 0.047 | -0.548 ± 0.047 |
| 2025-26 | >=10 | MID | 88 | 0.420 / 3.773 | 0.501 → 0.275 | 4.178 → 3.952 | +0.064 ± 0.215 | -0.227 ± 0.070 |
| alle | 8-10 | FWD | 233 | 0.627 / 4.253 | 0.412 → 0.253 | 3.810 → 3.651 | +0.159 ± 0.032 | +0.159 ± 0.032 |
| alle | 8-10 | MID | 615 | 0.423 / 3.611 | 0.381 → 0.233 | 3.548 → 3.400 | +0.148 ± 0.015 | +0.148 ± 0.015 |
| alle | >=10 | FWD | 155 | 0.419 / 3.097 | 0.970 → 0.499 | 4.422 → 3.951 | -0.471 ± 0.062 | -0.471 ± 0.062 |
| alle | >=10 | MID | 249 | 0.602 / 4.518 | 0.923 → 0.482 | 5.097 → 4.656 | -0.200 ± 0.169 | -0.441 ± 0.081 |

For å avgjøre «bedre premiumkalibrering» ble følgende oppsummering skrevet ned før målingen: **WACE = antallsvektet absolutt gjennomsnittsbias i de fire pris-/posisjonscellene**. Dette hindrer at overvurdering i én celle skjules av undervurdering i en annen. Kravet vurderes på bonus; totalpoeng rapporteres samtidig, slik oppdraget krever. SE for endring i absolutt bias/WACE bruker delta-metodens påvirkningsverdier i de samme fire-runders blokkene; nær null bias er denne lineariseringen usikker. Ingen ny signifikansgrense for kalibrering er lagt til.

| Sesong | Kalibrering | N | Vektet absolutt cellebias før → etter | Δ ± blokk-SE |
| --- | --- | --- | --- | --- |
| 2023-24 | bonus | 375 | 0.113884 → 0.236804 | +0.122920 ± 0.043516 |
| 2023-24 | total | 375 | 0.403213 → 0.495548 | +0.092335 ± 0.015131 |
| 2024-25 | bonus | 369 | 0.349477 → 0.198852 | -0.150626 ± 0.082598 |
| 2024-25 | total | 369 | 0.660664 → 0.470573 | -0.190091 ± 0.257803 |
| 2025-26 | bonus | 508 | 0.183815 → 0.195178 | +0.011363 ± 0.043461 |
| 2025-26 | total | 508 | 0.362247 → 0.323203 | -0.039044 ± 0.019357 |
| alle | bonus | 1252 | 0.192476 → 0.196570 | +0.004094 ± 0.033336 |
| alle | total | 1252 | 0.392966 → 0.349241 | -0.043726 ± 0.021929 |

**Konklusjon B1: UAVKLART.** Ikke oppfylt: Minst 0,5 % lavere total-MSE samlet; Minst 3 blokk-SE bedre total-MSE samlet; Bedre premium-bonuskalibrering på kontrollår og samlet.

Tau 7 reduserer særlig overvurderingen av ≥10 m-spillere samlet, men gjør undervurderingen i 8–10 m-gruppene større. Premium-bonus-WACE går samlet fra 0.192476 til 0.196570, og på kontrollåret fra 0.183815 til 0.195178. Endringene er små relativt til SE, så dette beviser ikke skade, men oppfyller heller ikke kravet om bedre premiumkalibrering. Topp10 på kontrollåret faller med 0.252 poeng per valgt spiller (±0.142); det er innenfor 2-SE-vernet, uten å være en rangeringseffekt i ønsket retning.

Det forhåndsskrevne unntaket lyder: «Hvis B1 bare forbedrer bonus-MSE, men ikke total-MSE med 3 SE … Da avgjør vi ut fra kalibreringen og topp-k, og skriver eksplisitt at det primære kravet ikke ble nådd.» Unntaket er ikke brukt. Alle enkeltceller vises; en bedre samlet WACE betyr ikke at hver spillergruppe eller hvert års celle må bli bedre.

## Kontroll mot forhåndsregistrerte krav

| Forhåndsregistrert krav / vern | P2 | B1 |
| --- | --- | --- |
| Minst 0,5 % lavere total-MSE samlet | **NEI** | **NEI** |
| Minst 3 blokk-SE bedre total-MSE samlet | JA | **NEI** |
| Lavere total-MSE i hver sesong | JA | JA |
| Topp10/20-vern samlet (≤2 SE forverring) | JA | JA |
| Lavere total-MSE på låst kontrollår | – | JA |
| Topp10/20-vern på kontrollåret | – | JA |
| Lavere bonus-MSE på kontrollår og samlet | – | JA |
| Bedre premium-bonuskalibrering på kontrollår og samlet | – | **NEI** |

GODKJENT betyr at ordinære krav består, eller at det eksplisitte B1-unntaket er brukt og forklart. AVVIST brukes ved tydelig samlet primærforverring eller brudd på de vurderte vernene. UAVKLART betyr at kravene til godkjenning ikke er møtt; det betyr ikke at det mangler enhver målt gevinst eller at skade er bevist. For B1 vises topp-k-vern både samlet og på det låste kontrollåret. Ingen krav er justert ved å velge en annen tau etter kontrollen.

## Kombinasjon og B2

**Ikke kjørt:** begge kandidatene måtte være godkjent hver for seg først.

B1 bestod ikke; B2 skal derfor ikke testes etter forhåndsregistreringen.

## Etterprøvbarhet

Alle målinger er kjørt fra `kjor_p1p2.py`, hele testsuiten er grønn: **18 tester, 3.53 s** (`p1p2_tests.log`). Beregningen tok **533.3 s**; ingen sesonger eller runder kuttet. Flaggene er gjenopprettet til `False` og `None`, med kontroll i `p1p2_manifest.json`. Ingen nett, installasjon, commit eller skriving av produksjonsutdata.

Hovedfiler: `p1p2_tau_utvikling.csv`, `p1p2_nivaer.csv`, `p1p2_parvis.csv`, `p1p2_minuttkalibrering.csv`, `p1p2_premium.csv`, `p1p2_premium_wace.csv`, `p1p2_beslutning.json`, `p1p2_prediksjoner.csv.gz`. Sesongfilene og kjøringsloggen bevarer utviklings-/kontrollfasene hver for seg.

```sh
export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH
PYTHONDONTWRITEBYTECODE=1 python3 samarbeid/modell/codex/kjor_p1p2.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' python3 -m pytest -q tests/ > samarbeid/modell/codex/p1p2_tests.log
PYTHONDONTWRITEBYTECODE=1 python3 samarbeid/modell/codex/skriv_p1p2.py
```
