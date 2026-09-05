"""
M9 — backtest og kalibrering.

Dette er steget som avgjør om modellen er god eller bare virker god. Alt
foregående er antagelser til de er målt mot fasit.

METODEN: WALK-FORWARD

For hver runde t i forrige sesong trenes modellen KUN på runde 1 til t−1, og
predikerer så runde t. Ingen informasjon fra framtiden lekker inn. Det er den
eneste testen som ligner på hvordan modellen faktisk brukes: hver torsdag vet
den bare det som har skjedd.

BASELINE ER POENGET

En modell som treffer "bra" i absolutt forstand er verdiløs hvis den ikke slår
noe enklere. Derfor måles den mot to alternativer man kunne brukt gratis:

    sesongsnitt   spillerens poeng per kamp hittil
    form          snittet av de tre siste rundene

Slår ikke modellen begge, er den ikke verdt å kjøre.

RESULTAT (kjørt 5. sep 2026 på 2025-26, 24 577 prediksjoner over GW8-38)

    MAE                modell 1.023 | form 1.033 | sesongsnitt 1.049
    Spearman, alle     modell 0.648 | form 0.734 | sesongsnitt 0.686
    Spearman, spilte   modell 0.310 | form 0.261 | sesongsnitt 0.289
    topp 10 valgt      modell 4.32  | form 3.60  | snitt alle 1.14

Legg merke til de to Spearman-radene. Målt over ALLE rader ser "form" best ut,
men det er en illusjon: to tredjedeler av radene er spillere som ikke spilte,
og der treffer form perfekt uten å vite noe om fotball. Blant dem som faktisk
spilte, rangerer modellen best. Det er den raden som betyr noe.

HVA BACKTESTEN FANT

Fase 3 la inn to "Dixon-Coles"-korreksjoner som blåste opp clean sheets og
straffen for innslupne mål, begge basert på 40 lag-kamper fra inneværende
sesong. Testet mot 760 lag-kamper fra i fjor holdt antagelsen ikke:

    faktisk clean sheet-andel  0.255   Poisson forutsier  0.253
    faktisk innslupne-straff   0.454   Poisson forutsier  0.453
    varians/snitt = 0.940 — ingen overspredning

Korreksjonene var støytilpasning, og de var årsaken til +20 % skjevhet i
forsvarspoeng. Etter at de ble fjernet: +1 %.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from team_strength import _fit                  # samme estimator som i produksjon
from expected_points import bonus_expectation   # samme bonusfordeling

HIST = ("https://raw.githubusercontent.com/vaastav/"
        "Fantasy-Premier-League/master/data/2025-26")

GOAL_POINTS = {"GK": 6, "DEF": 6, "MID": 5, "FWD": 4}
CS_POINTS = {"GK": 4, "DEF": 4, "MID": 1, "FWD": 0}
DC_THRESHOLD = {"GK": 999, "DEF": 10, "MID": 12, "FWD": 12}

FIRST_TEST_GW = 8        # trenger noen runder å trene på først
SHRINK_MINUTES = 270.0
PRIOR_MATCHES_MIN = 0.7
PRIOR_WEIGHT_TEAM = 4.0


def load() -> pd.DataFrame:
    d = pd.read_csv(f"{HIST}/gws/merged_gw.csv")
    keep = ["name", "position", "team", "GW", "fixture", "opponent_team", "was_home",
            "minutes", "starts", "total_points", "goals_scored", "assists",
            "clean_sheets", "goals_conceded", "saves", "bonus", "bps",
            "expected_goals", "expected_assists", "defensive_contribution",
            "yellow_cards", "red_cards"]
    d = d[keep].copy()
    d["pos"] = d.position.map({"GKP": "GK", "GK": "GK", "DEF": "DEF",
                               "MID": "MID", "FWD": "FWD"}).fillna(d.position)
    return d


def team_ratings(train: pd.DataFrame) -> tuple[dict, dict, float, float]:
    """Angreps- og forsvarsrating fra xG, med samme estimator som i produksjon."""
    tm = (train.groupby(["fixture", "team", "was_home"], as_index=False)
          .agg(xg=("expected_goals", "sum")))
    home = tm[tm.was_home].rename(columns={"team": "h", "xg": "xg_h"})
    away = tm[~tm.was_home].rename(columns={"team": "a", "xg": "xg_a"})
    pair = home.merge(away, on="fixture")[["h", "a", "xg_h", "xg_a"]]
    if len(pair) < 20:
        return {}, {}, 0.0, np.log(1.4)

    teams = sorted(set(pair.h) | set(pair.a))
    idx = {t: i for i, t in enumerate(teams)}
    n = len(teams)
    att, dfn, home_adv, mu, _ = _fit(
        pair.h.map(idx).to_numpy(), pair.a.map(idx).to_numpy(),
        pair.xg_h.to_numpy(float), pair.xg_a.to_numpy(float),
        n, np.ones(len(pair)), np.zeros(n), np.zeros(n),
        penalty=PRIOR_WEIGHT_TEAM,
    )
    return dict(zip(teams, att)), dict(zip(teams, dfn)), float(home_adv), float(mu)


def negative_binomial_cs(lam: float, disp: float) -> tuple[float, float]:
    """Clean sheet-sannsynlighet og forventet innslupne-straff under negativ binomial."""
    r = disp
    p = r / (r + lam)
    k = np.arange(0, 15)
    from scipy.stats import nbinom
    pmf = nbinom.pmf(k, r, p)
    return float(pmf[0]), float(np.sum((k // 2) * pmf))


def fit_dispersion(train: pd.DataFrame) -> float:
    """Overspredning fra faktiske innslupne mål. Lav r = mye; r → ∞ gir Poisson."""
    conc = (train.groupby(["fixture", "team"], as_index=False)
            .agg(gc=("goals_conceded", "max"))).gc.to_numpy(float)
    m, v = conc.mean(), conc.var()
    if v <= m:
        return 1e6
    return float(np.clip(m ** 2 / (v - m), 0.5, 50.0))


def per90(train: pd.DataFrame) -> pd.DataFrame:
    stats = ["expected_goals", "expected_assists", "saves", "bps", "yellow_cards"]
    agg = train.groupby(["name", "pos"], as_index=False).agg(
        mins=("minutes", "sum"), apps=("minutes", "size"),
        starts=("starts", "sum"), **{s: (s, "sum") for s in stats})
    started = train[train.minutes >= 60]
    hit = (started.defensive_contribution >= started.pos.map(DC_THRESHOLD))
    dc = started.assign(hit=hit).groupby("name").hit.agg(["sum", "count"])

    pos_rate = started.assign(hit=hit).groupby("pos").hit.mean().to_dict()
    agg["dc_rate"] = [
        (dc.loc[nm, "sum"] + 3 * pos_rate.get(ps, 0)) / (dc.loc[nm, "count"] + 3)
        if nm in dc.index else pos_rate.get(ps, 0.0)
        for nm, ps in zip(agg.name, agg.pos)]

    for s in stats:
        raw = np.where(agg.mins > 0, agg[s] / agg.mins.clip(lower=1) * 90, np.nan)
        prior = pd.Series(raw).groupby(agg.pos.values).transform("mean")
        w = agg.mins / (agg.mins + SHRINK_MINUTES)
        agg[f"{s}90"] = w * pd.Series(raw).fillna(0) + (1 - w) * prior.fillna(0)

    # Minutter: startandel med krymping, som i M2.
    base = float((train[train.minutes > 0].starts == 1).mean()) * 0.5
    agg["p_start"] = ((agg.starts + PRIOR_MATCHES_MIN * base)
                      / (agg.apps + PRIOR_MATCHES_MIN)).clip(0, 1)
    agg["p_60"] = agg.p_start * 0.95
    agg["exp_min"] = agg.p_start * 82.0
    return agg


def predict(test: pd.DataFrame, rates: pd.DataFrame, att, dfn, home_adv, mu,
            disp: float) -> pd.DataFrame:
    r = rates.set_index("name")
    rows = []
    for _, row in test.iterrows():
        nm = row["name"]
        if nm not in r.index:
            continue
        p = r.loc[nm]
        a_t, d_o = att.get(row.team), dfn.get(row.team)
        opp_name = row.get("_opp_name")
        d_opp, a_opp = dfn.get(opp_name), att.get(opp_name)
        if None in (a_t, d_opp, a_opp, d_o):
            continue
        h = home_adv if row.was_home else 0.0
        lam_for = np.exp(mu + a_t - d_opp + h)
        lam_ag = np.exp(mu + a_opp - d_o + (0.0 if row.was_home else home_adv))

        share = p.exp_min / 90.0
        p_cs, pen = negative_binomial_cs(float(lam_ag), disp)
        xp = (p.p_start + p.p_60
              + p.expected_goals90 * share * GOAL_POINTS[p.pos]
              + p.expected_assists90 * share * 3
              + p_cs * p.p_60 * CS_POINTS[p.pos]
              - (pen * p.p_60 if p.pos in ("GK", "DEF") else 0.0)
              + (p.saves90 * share / 3.0 if p.pos == "GK" else 0.0)
              + p.dc_rate * p.p_60 * 2
              - p.yellow_cards90 * share)
        rows.append({"name": nm, "pos": p.pos, "gw": row.GW, "fixture": row.fixture,
                     "xp_base": float(xp), "bps_w": float(np.exp(p.bps90 * share / 4.0)),
                     "actual": row.total_points, "mins": row.minutes})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    # Bonus: 3-2-1 fordelt innenfor hver kamp, samme metode som i produksjon.
    # Uten dette mangler modellen ~0.08 poeng per rad og ser systematisk
    # pessimistisk ut i kalibreringen.
    out["bonus"] = out.groupby("fixture").bps_w.transform(
        lambda w: pd.Series(bonus_expectation(w.to_numpy()), index=w.index))
    out["xp"] = out.xp_base + out.bonus
    return out.drop(columns=["bps_w"])


def main() -> None:
    d = load()
    # Motstanderens navn utledes fra samme kamp: den andre siden av fixture-en.
    sides = d.groupby(["fixture", "team"], as_index=False).size()
    opp = sides.merge(sides, on="fixture")
    opp = opp[opp.team_x != opp.team_y][["fixture", "team_x", "team_y"]]
    opp = opp.rename(columns={"team_x": "team", "team_y": "_opp_name"}).drop_duplicates()
    d = d.merge(opp, on=["fixture", "team"], how="left")

    all_preds = []
    gws = sorted(g for g in d.GW.unique() if g >= FIRST_TEST_GW)
    for t in gws:
        train, test = d[d.GW < t], d[d.GW == t]
        if train.empty or test.empty:
            continue
        att, dfn, ha, mu = team_ratings(train)
        if not att:
            continue
        disp = fit_dispersion(train)
        rates = per90(train)
        preds = predict(test, rates, att, dfn, ha, mu, disp)
        if preds.empty:
            continue

        # Baselines, beregnet på nøyaktig samme treningsdata.
        season = train.groupby("name").total_points.mean()
        recent = (train[train.GW >= t - 3].groupby("name").total_points.mean())
        preds["b_season"] = preds.name.map(season).fillna(0)
        preds["b_form"] = preds.name.map(recent).fillna(preds.b_season)
        all_preds.append(preds)

    p = pd.concat(all_preds, ignore_index=True)
    print(f"Backtest: {len(p)} prediksjoner over GW{gws[0]}-{gws[-1]} ({p.gw.nunique()} runder)\n")

    def score(col, label):
        mae = (p[col] - p.actual).abs().mean()
        rmse = np.sqrt(((p[col] - p.actual) ** 2).mean())
        rho = spearmanr(p[col], p.actual).statistic
        print(f"  {label:14s} MAE {mae:5.3f} | RMSE {rmse:5.3f} | Spearman {rho:5.3f}")
        return mae

    print("NØYAKTIGHET (lavere MAE er bedre, høyere Spearman er bedre)")
    m_model = score("xp", "modellen")
    m_season = score("b_season", "sesongsnitt")
    m_form = score("b_form", "form (3 runder)")
    print(f"\n  modellen mot beste baseline: {100*(m_model - min(m_season, m_form))/min(m_season, m_form):+.1f} % MAE")

    print("\nKALIBRERING")
    print(f"  snitt predikert {p.xp.mean():.3f} mot faktisk {p.actual.mean():.3f} "
          f"({100*(p.xp.mean()-p.actual.mean())/p.actual.mean():+.1f} %)")
    p["bin"] = pd.qcut(p.xp, 5, labels=["lavest", "2", "3", "4", "høyest"])
    cal = p.groupby("bin", observed=True).agg(predikert=("xp", "mean"), faktisk=("actual", "mean"), n=("xp", "size"))
    print(cal.round(2).to_string())

    played = p[p.mins > 0]
    print("\nRANGERING BLANT DEM SOM FAKTISK SPILTE")
    print(f"  n = {len(played)} av {len(p)}  — resten spilte ikke, og der treffer")
    print("  'form' perfekt uten å vite noe. Denne raden er den som betyr noe.")
    for col, lab in (("xp", "modellen"), ("b_season", "sesongsnitt"), ("b_form", "form")):
        print(f"  {lab:14s} Spearman {spearmanr(played[col], played.actual).statistic:5.3f}")

    print("\nBESLUTNINGSVERDI — hva scoret de modellen ville valgt?")
    for k in (10, 20, 50):
        picked = p.groupby("gw", group_keys=False).apply(lambda g: g.nlargest(k, "xp"), include_groups=False)
        best = p.groupby("gw", group_keys=False).apply(lambda g: g.nlargest(k, "actual"), include_groups=False)
        form = p.groupby("gw", group_keys=False).apply(lambda g: g.nlargest(k, "b_form"), include_groups=False)
        print(f"  topp {k:2d}: modell {picked.actual.mean():5.2f} | form {form.actual.mean():5.2f} "
              f"| fasit {best.actual.mean():5.2f} | snitt alle {p.actual.mean():5.2f}")


if __name__ == "__main__":
    main()
