"""Walk-forward-tilpasning av bonustemperaturen tau.

For hver runde t >= 8 i hver sesong: rater fra runde < t (backtest.per90), forventet BPS = bps90 x forventede minutter / 90,
Plackett-Luce-bonus per kamp (produksjonens bonus_expectation) for hver tau, sammenlignet med faktisk bonus i runde t.
Bare lesing av src/. Kjør fra repoets rot: python3 samarbeid/modell/claude/bonus_tau.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
import backtest as B  # noqa: E402
from expected_points import bonus_expectation  # noqa: E402

CACHE = Path("data/cache/vaastav")
SEASONS = ["2023-24", "2024-25", "2025-26"]
TAUS = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40]
OUT = Path("samarbeid/modell/claude")


def season_rows(season: str) -> pd.DataFrame:
    B.HIST = str(CACHE / season)
    d = B.load()
    rows = []
    for t in sorted(g for g in d.GW.unique() if g >= B.FIRST_TEST_GW):
        train, test = d[d.GW < t], d[d.GW == t]
        rates = B.per90(train).set_index("name")
        test = test[test.name.isin(rates.index)]
        exp_bps = rates.bps90.reindex(test.name).to_numpy() * rates.exp_min.reindex(test.name).to_numpy() / 90.0
        rows.append(pd.DataFrame({"season": season, "gw": t, "fixture": test.fixture.to_numpy(),
                                  "name": test.name.to_numpy(), "exp_bps": exp_bps,
                                  "bonus": test.bonus.to_numpy(), "mins": test.minutes.to_numpy()}))
    return pd.concat(rows, ignore_index=True)


def predict(df: pd.DataFrame, tau: float) -> np.ndarray:
    out = np.zeros(len(df))
    for _, idx in df.groupby(["season", "fixture"]).indices.items():
        out[idx] = bonus_expectation(np.exp(df.exp_bps.to_numpy()[idx] / tau))
    return out


def main():
    df = pd.concat([season_rows(s) for s in SEASONS], ignore_index=True)
    res = []
    for tau in TAUS:
        p = predict(df, tau)
        err = p - df.bonus.to_numpy()
        top = df.assign(p=p).loc[lambda x: x.groupby(["season", "fixture"]).p.transform("max") == x.p]
        for s in SEASONS + ["alle"]:
            m = (df.season == s).to_numpy() if s != "alle" else np.ones(len(df), bool)
            tm = top if s == "alle" else top[top.season == s]
            res.append({"tau": tau, "sesong": s, "MSE": float(np.mean(err[m] ** 2)), "MAE": float(np.mean(np.abs(err[m]))),
                        "topp_pred": float(tm.p.mean()), "topp_faktisk": float(tm.bonus.mean()), "n": int(m.sum())})
    r = pd.DataFrame(res)
    r.to_csv(OUT / "bonus_tau.csv", index=False)
    print(r[r.sesong == "alle"].round(4).to_string(index=False))
    best = r[r.sesong != "alle"].loc[lambda x: x.groupby("sesong").MSE.idxmin()]
    print("\nbeste tau per sesong (MSE):\n", best[["sesong", "tau", "MSE", "topp_pred", "topp_faktisk"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
