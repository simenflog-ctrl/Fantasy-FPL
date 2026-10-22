# Felles plan for modellforbedring (gren `modellforbedring`)

Avtalt 2026-10-22 etter at begge leverte uavhengige gjennomganger (`claude/forslag.md`, `claude/avviksrevisjon.md`,
`codex/gjennomgang.md`). Funnene overlappet uten at agentene hadde sett hverandres lister.

## Felles funn

| Funn | Claude | Codex | Status |
|---|---|---|---|
| Bonus overkonfident (tau tilpasset på realisert BPS, brukt på forventet) | Mekanisme + walk-forward tau 6–8 | Premium-FWD bonus +0,55/kamp, samme fortegn tre sesonger | Rettes etter P0 |
| Backtest/evaluate_pred måler ikke produksjonen | 7 avvik | Bygd produksjonsrekonstruksjon | P0 |
| Optimizer: nåpris, FT=1, WC-reset, horisont | Rettet (`e1e1fb3`) | D0 samme funn | Ferdig; Codex kontrollerer |
| Keepermål 6 → 10 | Ja | P6 | Del av P0 |
| Innhopp dempes to ganger i `minutes.py` | Bekreftet ved lesing | P2 (funnet av Codex) | Claude, bak flagg |
| `season_sim` bruker framtidig metadata | – | Funnet av Codex | Etter P0 |

## Godkjenningskrav (forhåndsregistrert, før noen kandidat kjøres)

Tatt fra Codex' forslag:

- **Primærmål:** parvis MSE på totalpoeng per spiller–kamp, samme rader (sesong, spiller, fixture), 2023-24 / 2024-25 / 2025-26, GW8–38.
- **Krav:** forbedring på minst 3 blokk-standardfeil samlet (fire-runders blokker innen sesong), **samme fortegn i alle tre sesonger**,
  og minst 0,5 % lavere MSE.
- **Vern:** topp-10 og topp-20 ikke dårligere med mer enn 2 blokk-SE. For bonusendringer i tillegg: bonus-MSE og premiumkalibrering skal bli bedre.
- **Regelretting** (keepermål, salgspris, FT) krever ikke statistisk bevis, bare tester mot kjent fasit.
- **Uavhengighet:** den som ikke skrev en endring, kjører målingen og godkjenner den.
- Endringer legges bak et flagg med dagens oppførsel som standard, til målingen er godkjent.

## Arbeidsdeling og filansvar

| Steg | Eier | Filer eieren alene kan endre | Leveranse |
|---|---|---|---|
| P0 felles målemotor + paritetstest + keepermål per sesong | Codex | `src/backtest.py`, `src/evaluate_pred.py`, `src/expected_points.py`, `src/team_strength.py`, nye `src/eval_*.py`, `tests/test_parity.py`, `samarbeid/modell/codex/` | Produksjonens funksjoner brukes i målingen; test som feiler ved avvik; baseline på nytt |
| P2 innhoppsfeil bak flagg | Claude | `src/minutes.py`, `tests/test_minutes.py`, `samarbeid/modell/claude/` | Flagg `SUB_GIVEN_NO_START` (av som standard) + enhetstest |
| Kontroll av optimizerrettelsene (D0) | Codex | (bare lesing) | Godkjenning eller innvendinger |
| Måling av P2 | Codex | – | Etter P0 |
| P1 bonus (walk-forward tau på forventet BPS; alternativ: krympet historisk bonusrate) | Claude implementerer etter P0 | `src/expected_points.py` (overtas etter P0) | Bak flagg |
| Måling av P1 | Codex | – | |
| `season_sim`-lekkasje, D1–D3 | Senere | | |

Ingen endrer filer den andre eier. Ingen merger til `main` før målingene er godkjent av den som ikke skrev endringen.
