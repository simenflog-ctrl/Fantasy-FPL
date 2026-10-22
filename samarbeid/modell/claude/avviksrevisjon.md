# Avviksrevisjon: backtest.py mot produksjonen

Skrevet 2026-10-22 av Claude, mens Codex målte baseline. Kun lesing av `src/`; ingenting er endret.

## Hovedfunn: bonusmodellen er overkonfident (verifisert)

`expected_points.fit_bonus_temperature` tilpasser `tau` ved å fordele 6 poeng med softmax over **faktisk BPS i kampen**
(standardavvik ≈ 11,6 per kamp i år). Produksjonen bruker så samme `tau` på **forventet BPS** (`bps90 × minuttandel`), som er
mye jevnere, og fordeler med Plackett-Luce. En temperatur tilpasset realiserte utfall gjør fordelingen over forventninger altfor skarp.

Målt på dagens data (`tau = 4,0`):

| Spiller | Predikert bonus per kamp R8–13 | Faktisk bonus per 60+-kamp i år |
|---|---|---|
| Haaland | 2,79 | 1,71 |
| B.Fernandes | 2,07 | 0,43 |
| Groß | 1,48 | 1,29 |
| João Pedro | 1,37 | 1,50 |
| Dewsbury-Hall | 1,36 | 0,86 |
| Tavernier | 1,20 | 1,43 |
| Rogers | 0,93 | 0,29 |

Historisk for Haaland: 0,8–1,3 per start over tre sesonger. Fernandes' xP på 7,3 i gw08 kom i stor grad herfra.

**Riktig tilpasning:** walk-forward. For hver runde t: beregn forventet BPS fra data før t, fordel med Plackett-Luce for en gitt `tau`,
og velg `tau` som minimerer feil mot faktisk bonus i runde t (log-tap eller MAE per spiller). Dette kan bare gjøres i backtest-riggen.

## Andre avvik (backtest måler ikke det produksjonen gjør)

| # | Område | Produksjon (`expected_points.py`, `minutes.py`) | Backtest (`backtest.py`) | Konsekvens |
|---|---|---|---|---|
| 1 | Bonus | `tau` tilpasset på faktisk BPS (= 4,0 nå) | `tau` hardkodet 4,0 (`bps90*share/4.0`) | Samme tall i dag, men av ulike grunner; driver fra hverandre |
| 2 | Personlig angrepsprior | Fjorårets mål/assist/BPS/bonus per 90 fra `cleaned_players.csv` | Bare posisjonsprior for xG/xA | Backtesten mangler produksjonens viktigste prior for toppspillere |
| 3 | Redninger | Poisson med gulv (`k // 3`) | Lineær `saves90 / 3` | Gammel feil (docstring: «41 poeng mot fasit 12») lever videre i backtesten |
| 4 | Nullet / innslupne | `goal_scale` (xG → mål) og `p_cs ≤ 0,95` | Ingen `goal_scale`, ingen tak | Ulik forsvarspoeng |
| 5 | Minutter | `minutes.py` (egen modell, flagg fra API) | Egen kopi i `per90` med konstanter kopiert for hånd | Synkroniseres manuelt |
| 6 | Keepermål | 6 | 6 | Begge feil for 2026/27 (API: 10) |
| 7 | Lagstyrke | `team_strength` med fjorårsprior | `_fit` delt, men `prior=None` i `main()` | Avhenger av kaller |

Felles: `_fit` (lagstyrke) og `bonus_expectation` (Plackett-Luce) importeres fra produksjonen.

## Konsekvens

Målingene i repoet (krympevekt 540, innbytterminutter, priorvekt) gjelder backtestens variant. De er sannsynligvis retningsriktige,
men kan ikke overføres ukritisk. Før nye endringer måles, bør backtesten bruke produksjonens funksjoner for rater, minutter og poeng,
med data inn som argument i stedet for filstier.

## Forslag til arbeidsdeling

1. **Codex:** paritetsrefaktorering (produksjonen eksponerer rene funksjoner som tar data inn; backtesten kaller dem) + en paritetstest.
   Berører `backtest.py`, `expected_points.py`, `minutes.py`, `evaluate_pred.py`.
2. **Claude, parallelt og i egen mappe:** walk-forward-tilpasning av bonus-`tau` på historiske sesonger med dagens backtest-funksjoner
   (kun lesing), slik at riktig verdi og effektstørrelse er klar når refaktoreringen lander.
3. Deretter: bonusrettelsen inn i produksjonen, målt i den nye paritetsriggen av den som ikke skrev den.

## Måling: walk-forward-tau (backtestens rater, 72 189 spillerrader, 2023-24 til 2025-26)

Skript: `bonus_tau.py`, resultat: `bonus_tau.csv`. «Topp» = spilleren med høyest predikert bonus i hver kamp.

| tau | MSE (alle) | Topp: predikert | Topp: faktisk |
|---|---|---|---|
| 4 (i dag) | 0,1812 | 1,16 | 0,62 |
| 5 | 0,1756 | 0,86 | 0,62 |
| **6** | **0,1737** | 0,66 | 0,62 |
| 8 | 0,1741 | 0,44 | 0,62 |
| 12 | 0,1768 | 0,26 | 0,62 |

Beste tau per sesong: 6 (2023-24), 6 (2024-25), 8 (2025-26). **tau = 4 er overkonfident i alle tre sesongene.**
Forbehold: backtestens rater har bare posisjonsprior for BPS. Produksjonen har personlig BPS-prior og dermed større spredning i
forventet BPS, som trolig krever enda høyere tau. Endelig verdi må tilpasses i paritetsriggen, med produksjonens rater.
Tilpasningen skal skje walk-forward på forventet BPS, ikke på realisert BPS som i dag.
