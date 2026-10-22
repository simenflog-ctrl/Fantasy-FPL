# Claudes forslag til modellforbedring (runde 1)

Skrevet 2026-10-22 mens Codex jobbet med sin uavhengige gjennomgang. Codex har ikke sett dette.

## Utgangspunkt

- Produksjonen: `src/` (minutter → lagstyrke → xP → optimizer), kjøres av GitHub Actions.
- Måleverktøy finnes: `backtest.py` (walk-forward), `evaluate_pred.py` (parvis MAE / Spearman / topp-k, SE ≈ 0,0004 MAE),
  `evaluate.py` + `season_sim.py` (parvis sesongsimulering, SE 6–15 poeng). Regel i repoet: prediksjonsendringer måles i
  `evaluate_pred` først.
- I gw08 fant vi at repoet og Codex' modell var uenige med ~12 poeng per runde, mest på bonus og toppspillere.

## Funn før måling (antakelser som skal testes)

1. **Bonus ser for konsentrert ut.** Repoets xP gir Haaland ≈ 2,8 bonus per kamp i R8–13. Historisk: 29 bonus / 29 starter (2023/24),
   26 / 31 (2024/25), 43 / 34 (2025/26) ⇒ 0,8–1,3 per start. Plackett-Luce-fordelingen er riktig konstruert (maks 3, sum 6),
   men temperaturen `tau` tilpasses i `fit_bonus_temperature` på inneværende sesong. Med sju runder kan den bli for lav (for spiss).
2. **`backtest.py` er en speilkopi, ikke produksjonen.** Den deler `_fit` og `bonus_expectation`, men har egen `predict` og egne
   konstanter (kopiert for hånd, f.eks. `GOAL_POINTS["GK"] = 6`). Når produksjonen endres, måler backtesten noe annet med mindre noen
   husker å synkronisere. Alle målte funn i repoet gjelder derfor speilet.
3. **Keepermål = 10** i 2026/27 (API), 6 i koden begge steder. Liten effekt, men feil.
4. **Beslutningslaget har kjente feil** (fra gw08): nåpris i stedet for salgspris, hardkodet 1 FT, wildcard-reset til 1 FT
   (ikke verifisert), horisont 5. Dette er korrekthetsfeil og trenger ikke statistisk bevis.

## Rangert liste

| # | Tiltak | Type | Forventet gevinst | Måling | Kostnad / risiko |
|---|---|---|---|---|---|
| 1 | **Paritet:** la backtesten kalle produksjonens funksjoner (eller en paritetstest som feiler ved avvik) | Infrastruktur | Ingen direkte; gjør alle senere målinger gyldige | Test som sammenligner xP fra begge veier på samme data | Middels kode, lav risiko |
| 2 | **Bonuskalibrering:** tilpass `tau` over flere sesonger og/eller krymp mot spillerens historiske bonus per start | Prediksjon | Stor for kapteinsvalg og toppspillere; liten for MAE totalt | `evaluate_pred` (MAE, topp-10) + kalibreringstabell bonus per prisgruppe | Lav |
| 3 | **Etterkalibrering av xP per posisjon og prisgruppe** (lineær eller isotonisk, walk-forward) | Prediksjon | Middels; fjerner systematisk nivåfeil som gjorde modellene 12 poeng uenige | `evaluate_pred` | Lav; risiko for overtilpasning, krever samme fortegn i tre sesonger |
| 4 | **Ensemble** av repoets xP og Codex' gw08-modell (vektet snitt) | Prediksjon | Ofte bedre enn hver enkelt; gw08 viste at feilene er ulike | `evaluate_pred`, bare hvis Codex-modellen kan kjøres walk-forward | Middels |
| 5 | **Beslutningslaget:** salgspris, faktisk FT, chipvinduer til R19, ingen hardkodet WC-reset | Beslutning | Korrekthet; unngår ugyldige planer som i gw08 | Enhetstester; sesongsimulering for bekreftelse | Middels |
| 6 | **Minutter etter europacup** og gradvis comeback etter skade | Prediksjon | Usikker; vanskelig å måle uten europacupdata | Ikke målbart med dagens data | Høy |
| 7 | **Autobytter og benkverdi** i beslutningslaget | Beslutning | Liten–middels for BB-planlegging | Sesongsimulering | Middels |

## Forslag til i dag

1. **Paritet (1)** først, ellers måler vi feil ting.
2. **Bonus (2)** og **etterkalibrering (3)**, målt i `evaluate_pred` på 2023-24, 2024-25 og 2025-26.
   Godkjenningskrav: forbedring i MAE på minst 2 standardfeil samlet, **samme fortegn i alle tre sesongene**,
   og ikke dårligere topp-10.
3. **Beslutningslagets korrekthetsfeil (5)** kan rettes parallelt fordi de ikke krever statistisk bevis, bare tester.
4. Keepermål = 10 rettes som en del av (1).
