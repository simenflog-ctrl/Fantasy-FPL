"""
M3-M6 + xP — forventede poeng per spiller per runde.

Dette er stedet der lagstyrke (M1) og minutter (M2) blir til et tall man kan
handle på: hvor mange poeng er denne spilleren verdt i denne kampen?

POENGFUNKSJONEN ER VERIFISERT, IKKE ANTATT

Reglene under er ikke hentet fra en artikkel. De ble utledet ved å rekonstruere
faktiske FPL-poeng fra komponentene for hver eneste spiller-kamp denne sesongen.
Restleddet var utelukkende 0 eller 2, og de som fikk 2 var nøyaktig dem med
minst 10 (forsvar) eller 12 (midtbane/angrep) defensive handlinger.

Det gjør `defensive_contribution` til en bekreftet poengkilde. Den er verdt å
modellere nettopp fordi de fleste vurderer spillere på xGI alene og overser
den helt — en defensiv midtbanespiller kan hente 2 poeng i uka uten å komme
i nærheten av mål eller assist.

HVA MODELLEN GJØR

For hver spiller og hver kommende kamp:

    xP = opptreden + mål + assist + clean sheet − innslupne
         + redninger + defensive handlinger + bonus − kort

Hvert ledd skaleres med forventede minutter fra M2, og alt som avhenger av
motstanderen skaleres med kampens λ fra M1. En spiller med p_start 0.1 får
omtrent en tiendedel av poengene til en identisk spiller som alltid starter.

KRYMPING, IGJEN

Alle rater per 90 krympes mot posisjonsgjennomsnittet. Uten det får en spiller
som scoret i sin eneste kamp en xG90 som sier at han scorer hver kamp resten
av sesongen.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import poisson

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"

# Verifisert empirisk 5. sep 2026 — se docstring.
GOAL_POINTS = {"GK": 6, "DEF": 6, "MID": 5, "FWD": 4}
CS_POINTS = {"GK": 4, "DEF": 4, "MID": 1, "FWD": 0}
DC_THRESHOLD = {"GK": None, "DEF": 10, "MID": 12, "FWD": 12}
DC_POINTS = 2
ASSIST_POINTS = 3

# Krymping av rater per 90: prioren veier like mye som dette antall minutter.
SHRINK_MINUTES = 270.0

LAST_SEASON = ("https://raw.githubusercontent.com/vaastav/"
               "Fantasy-Premier-League/master/data/2025-26/cleaned_players.csv")

# Minste spilletid i fjor for at en spillers egne tall skal brukes som prior.
PRIOR_MIN_MINUTES = 450


def load():
    pm = pd.read_csv(DERIVED / "player_matches.csv")
    fx = pd.DataFrame(json.loads((RAW / "fixtures.json").read_text()))
    pm = pm[pm.fixture.isin(set(fx.loc[fx["finished"] == True, "id"]))]  # noqa: E712
    return (
        pm[pm.minutes > 0].copy(),
        pd.read_csv(DERIVED / "minutes.csv"),
        pd.read_csv(DERIVED / "team_ratings.csv"),
        pd.read_csv(DERIVED / "fixture_projections.csv"),
        json.loads((RAW / "bootstrap.json").read_text()),
    )


def _norm(s: pd.Series) -> pd.Series:
    return (s.astype(str).str.normalize("NFKD").str.encode("ascii", "ignore")
            .str.decode("ascii").str.lower().str.strip())


def last_season_priors(bs: dict) -> pd.DataFrame:
    """
    Spillerens egne tall fra i fjor, som prior for i år.

    Uten dette krympes alle mot posisjonsgjennomsnittet, og da forsvinner
    forskjellen på en elitespiss og en gjennomsnittlig en. Konkret: med bare
    posisjonsprior havnet Haaland på tiendeplass i xP bak Nketiah, fordi 60 %
    av xG-raten hans var snittet av alle spisser.

    Fjorårsfila har mål og assists, ikke xG. Over en full sesong er mål per 90
    en akseptabel prior for xG per 90 — det er støyet i ETT år, ikke i tre
    kamper, som er problemet vi løser her.
    """
    try:
        ls = pd.read_csv(LAST_SEASON)
    except Exception as exc:  # noqa: BLE001
        print(f"  fant ikke fjorårsdata ({exc}) — faller tilbake på posisjonsprior")
        return pd.DataFrame(columns=["element"])

    ls = ls[ls.minutes >= PRIOR_MIN_MINUTES].copy()
    ls["key"] = _norm(ls.first_name) + " " + _norm(ls.second_name)
    for col, new in (("goals_scored", "p_goals"), ("assists", "p_assists"),
                     ("bps", "p_bps"), ("bonus", "p_bonus"),
                     ("yellow_cards", "p_yellow")):
        ls[new] = ls[col] / ls.minutes * 90

    now = pd.DataFrame([{"element": e["id"],
                         "key": f"{e['first_name']} {e['second_name']}"}
                        for e in bs["elements"]])
    now["key"] = _norm(now.key)

    merged = now.merge(ls[["key", "p_goals", "p_assists", "p_bps", "p_bonus", "p_yellow"]],
                       on="key", how="inner").drop_duplicates("element")
    print(f"  fjorårsprior funnet for {len(merged)} av {len(now)} spillere")
    return merged


def per90_rates(pm: pd.DataFrame, minutes: pd.DataFrame, bs: dict) -> pd.DataFrame:
    """
    Rater per 90 minutter, krympet mot posisjonsgjennomsnittet.

    Krympevekten er i minutter, ikke kamper: en spiller med 30 spilte minutter
    skal trekkes mye hardere mot snittet enn en som har spilt 270.
    """
    stats = ["expected_goals", "expected_assists", "saves", "defensive_contribution",
             "bps", "yellow_cards", "bonus"]
    agg = pm.groupby("element").agg(
        mins=("minutes", "sum"), **{s: (s, "sum") for s in stats}
    ).reset_index()

    agg = agg.merge(minutes[["element", "pos", "team", "web_name", "price",
                             "p_start", "p_play", "p_60", "exp_minutes"]],
                    on="element", how="right")
    agg[["mins"] + stats] = agg[["mins"] + stats].fillna(0.0)

    for s in stats:
        raw = np.where(agg.mins > 0, agg[s] / agg.mins.clip(lower=1) * 90, np.nan)
        agg[f"{s}_raw90"] = raw

    # Posisjonsprior som grunnlinje for alle.
    played = agg[agg.mins >= 90]
    pos_prior = {s: played.groupby("pos")[f"{s}_raw90"].mean().to_dict() for s in stats}

    # Spillerens egne fjorårstall overstyrer posisjonssnittet der de finnes.
    ls = last_season_priors(bs)
    if not ls.empty:
        agg = agg.merge(ls, on="element", how="left")
    for c in ("p_goals", "p_assists", "p_bps", "p_bonus", "p_yellow"):
        if c not in agg:
            agg[c] = np.nan

    # defensive_contribution og saves fantes ikke i fjorårsfila, så de beholder
    # posisjonsprior. DC stabiliserer seg raskt på årets data uansett.
    personal = {"expected_goals": "p_goals", "expected_assists": "p_assists",
                "bps": "p_bps", "bonus": "p_bonus", "yellow_cards": "p_yellow"}

    for s in stats:
        prior = agg.pos.map(pos_prior[s]).fillna(0.0)
        if s in personal:
            prior = agg[personal[s]].fillna(prior)
        w = agg.mins / (agg.mins + SHRINK_MINUTES)
        agg[f"{s}90"] = w * agg[f"{s}_raw90"].fillna(0.0) + (1 - w) * prior

    return agg


def calibrate_goals(pm: pd.DataFrame, teams_matches: pd.DataFrame,
                    proj: pd.DataFrame) -> tuple[float, float, float]:
    """
    To kalibreringer som begge går på forsvarspoeng.

    1. xG-til-mål. FPL gir poeng for MÅL, ikke for xG. Denne sesongen ligger
       xG over faktiske mål (1.63 mot 1.45 per lag-kamp), så λ fra M1 må
       skaleres ned før den brukes til å regne innslupne mål og clean sheets.

    2. Clean sheet-inflasjon. Ren Poisson undervurderer 0-0: observert andel
       er 0.275 mot 0.235 som Poisson tilsier ved samme λ. Det er den kjente
       skjevheten Dixon-Coles-korreksjonen finnes for. Her måles den direkte
       i stedet, som én faktor.

    BEGGE ER PROVISORISKE. De hviler på 40 lag-kamper og skal kalibreres på
    nytt i M9 når det finnes nok runder. Faktorene klippes derfor til et
    smalt intervall, slik at de korrigerer uten å kunne løpe løpsk.
    """
    played = teams_matches[teams_matches.player_minutes > 0]
    actual_goals = float(played.goals_against.mean())
    model_xg = float(proj.xg_against.mean())
    goal_scale = float(np.clip(actual_goals / max(model_xg, 1e-6), 0.80, 1.20))

    obs_cs = float((played.goals_against == 0).mean())
    poisson_cs = float(np.exp(-actual_goals))
    cs_inflation = float(np.clip(obs_cs / max(poisson_cs, 1e-6), 1.0, 1.35))

    # 3. Innslupne mål. Samme årsak som punkt 2, motsatt hale: målfordelingen
    #    er overspredt, så det er BÅDE flere 0-0 og flere storseiere enn
    #    Poisson tilsier. Da undervurderes straffen for innslupne mål med
    #    samme logikk som clean sheets undervurderes.
    #
    #    Den riktige løsningen er å bytte Poisson mot negativ binomial i hele
    #    modellen. Det hører hjemme i M9 sammen med kalibreringen — her måles
    #    skjevheten i stedet direkte som én faktor.
    k = np.arange(0, 12)
    poisson_pen = float(np.sum((k // 2) * poisson.pmf(k, actual_goals)))
    obs_pen = float((played.goals_against // 2).mean())
    conceded_inflation = float(np.clip(obs_pen / max(poisson_pen, 1e-6), 1.0, 1.60))

    print(f"  xG→mål: {goal_scale:.3f} | clean sheet-inflasjon: {cs_inflation:.3f} "
          f"| innslupne-inflasjon: {conceded_inflation:.3f}")
    return goal_scale, cs_inflation, conceded_inflation


def bonus_expectation(weights: np.ndarray) -> np.ndarray:
    """
    Forventet bonus per spiller i én kamp, gitt vekter avledet fra BPS.

    Bonus er 3-2-1 til de tre beste. Første versjon fordelte 6 poeng med en
    softmax, men det er ubundet: Fernandes fikk 4.31 forventede bonuspoeng i
    en kamp der maksimum er 3.

    Her regnes sannsynligheten for hver plassering i stedet (Plackett-Luce).
    Da er forventningen per definisjon under 3, og summen i kampen blir 6.
    P(tredjeplass) tilnærmes med P(andreplass) — leddet veier bare 1 poeng,
    og feilen er liten mot kostnaden ved å regne det eksakt.
    """
    w = np.asarray(weights, dtype=float)
    W = w.sum()
    if W <= 0 or len(w) < 3:
        return np.zeros_like(w)
    p1 = w / W
    # P(i på andreplass) = sum over j som blir nummer én
    denom = W - w
    p2 = np.array([np.sum(np.delete(p1, i) * (w[i] / np.delete(denom, i))) for i in range(len(w))])
    p2 = p2 / max(p2.sum(), 1e-9)
    p3 = p2
    return 3 * p1 + 2 * p2 + 1 * p3


def dc_hit_rates(pm: pd.DataFrame, rates: pd.DataFrame) -> pd.Series:
    """
    Sannsynligheten for å nå terskelen for defensive handlinger, estimert
    direkte fra hvor ofte spilleren faktisk har gjort det.

    Første versjon modellerte antall handlinger som Poisson og regnet ut
    P(X >= 10). Det ga bare 26 % av de faktiske DC-poengene: antallet er
    overspredt, og Poisson-halen kollapser når snittet trekkes ned av
    krymping og av at forventede minutter er under 90.

    Å estimere sannsynligheten direkte unngår hele fordelingsantagelsen.
    """
    started = pm[pm.minutes >= 60].copy()
    pos_map = rates.set_index("element").pos
    started["pos"] = started.element.map(pos_map)
    started["hit"] = started.defensive_contribution >= started.pos.map(
        {k: v for k, v in DC_THRESHOLD.items() if v}).fillna(999)

    pos_rate = started.groupby("pos").hit.mean().to_dict()
    per_player = started.groupby("element").hit.agg(["sum", "count"])

    # Beta-krymping mot posisjonsraten, prior verdt 3 kamper.
    k = 3.0
    out = {}
    for el in rates.element:
        prior = pos_rate.get(pos_map.get(el), 0.0)
        if el in per_player.index:
            hits, n = per_player.loc[el, "sum"], per_player.loc[el, "count"]
            out[el] = (hits + k * prior) / (n + k)
        else:
            out[el] = prior
    return pd.Series(out)


def fit_bonus_temperature(pm: pd.DataFrame) -> float:
    """
    Finner spredningsparameteren for bonusfordelingen.

    Bonus er et nullsumspill: nøyaktig 6 poeng (3+2+1) deles ut i hver kamp.
    Første versjon tilpasset en kurve fra BPS-rate til bonus-rate og traff
    15 % av de faktiske bonuspoengene — den hadde ingen mekanisme som sikret
    at summen stemte.

    Her fordeles de 6 poengene i stedet innenfor hver kamp, etter en softmax
    over forventet BPS. Temperaturen styrer hvor konsentrert fordelingen er,
    og tilpasses slik at modellen gjenskaper den observerte konsentrasjonen.
    """
    best, best_err = 8.0, 1e9
    for tau in np.arange(2.0, 30.0, 0.5):
        err = 0.0
        for _, g in pm[pm.minutes > 0].groupby("fixture"):
            w = np.exp(g.bps.to_numpy() / tau)
            pred = 6 * w / w.sum()
            err += np.abs(pred - g.bonus.to_numpy()).sum()
        if err < best_err:
            best, best_err = float(tau), err
    return best


def expected_points(rates, teams, proj, bonus_tau, goal_scale, cs_inflation,
                    conceded_inflation, n_gw=6) -> pd.DataFrame:
    team_avg = teams.set_index("short_name").xg_vs_avg.to_dict()
    gws = sorted(proj.gw.unique())[:n_gw]
    proj = proj[proj.gw.isin(gws)]

    rows = []
    for _, f in proj.iterrows():
        squad = rates[rates.team == f.team]
        if squad.empty:
            continue
        # Hvor mye bedre/verre enn lagets snittkamp er denne kampen?
        att_scale = f.xg_for / max(team_avg.get(f.team, 1.0), 1e-6)
        lam_ag = f.xg_against * goal_scale
        mins = squad.exp_minutes.to_numpy()
        share = mins / 90.0

        goals = squad.expected_goals90.to_numpy() * share * att_scale
        assists = squad.expected_assists90.to_numpy() * share * att_scale

        gp = squad.pos.map(GOAL_POINTS).to_numpy()
        csp = squad.pos.map(CS_POINTS).to_numpy()

        # Clean sheet krever 60 minutter.
        p_cs = min(float(np.exp(-lam_ag) * cs_inflation), 0.95)
        cs = p_cs * squad.p_60.to_numpy() * csp

        # Innslupne mål: -1 per 2, kun GK og DEF. Forventningen tas over
        # Poisson-fordelingen, ikke som -0.5*λ, fordi gulvfunksjonen ikke er lineær.
        k = np.arange(0, 12)
        pen_per_match = float(np.sum((k // 2) * poisson.pmf(k, lam_ag)))
        pen_per_match *= conceded_inflation
        conceded = np.where(squad.pos.isin(["GK", "DEF"]), -pen_per_match * squad.p_60.to_numpy(), 0.0)

        # Redninger gir 1 poeng per TRE redninger — en gulvfunksjon, ikke en
        # deling. Første versjon brukte saves/3 og ga 41 poeng per runde der
        # fasiten er 12, fordi to redninger ble til 0.67 poeng i stedet for 0.
        sv_mean = squad.saves90.to_numpy() * share
        save_pts = np.array([
            float(np.sum((np.arange(0, 25) // 3) * poisson.pmf(np.arange(0, 25), m)))
            if m > 0 else 0.0 for m in sv_mean
        ])
        saves = np.where(squad.pos == "GK", save_pts, 0.0)

        # Defensive handlinger: treffraten gjelder gitt at spilleren spiller
        # 60+, derfor skaleres den med p_60 og ikke med minuttandelen.
        dc = squad.dc_rate.to_numpy() * squad.p_60.to_numpy() * DC_POINTS

        # Bonus fordeles innenfor kampen, slik at summen alltid blir 6 poeng.
        exp_bps = squad.bps90.to_numpy() * share
        bonus_raw = np.exp(exp_bps / bonus_tau)

        cards = -squad.yellow_cards90.to_numpy() * share
        # Opptreden: 1 poeng for å spille, 2 for 60+. Forventningen er
        # P(spiller) + P(60+) — og P(spiller) MÅ inkludere innbytte.
        appear = squad.p_play.to_numpy() + squad.p_60.to_numpy()

        rows.append(pd.DataFrame({
            "gw": int(f.gw), "fixture": int(f.fixture), "element": squad.element.to_numpy(),
            "_bonus_w": bonus_raw,
            "_base": (appear + goals * gp + assists * ASSIST_POINTS + cs + conceded
                      + saves + dc + cards),
            "web_name": squad.web_name.to_numpy(), "team": f.team,
            "opponent": f.opponent, "pos": squad.pos.to_numpy(),
            "price": squad.price.to_numpy(),
            "xp_attack": goals * gp + assists * ASSIST_POINTS,
            "xp_defence": cs + conceded + saves, "xp_dc": dc,
            "exp_minutes": mins,
        }))

    out = pd.concat(rows, ignore_index=True)
    # Nøyaktig 6 bonuspoeng per kamp, fordelt mellom begge lag.
    out["xp_bonus"] = (out.groupby("fixture")._bonus_w
                       .transform(lambda w: pd.Series(bonus_expectation(w.to_numpy()), index=w.index)))
    out["xp"] = out._base + out.xp_bonus
    out = out.drop(columns=["_bonus_w", "_base"])
    return out.sort_values(["gw", "xp"], ascending=[True, False]).reset_index(drop=True)


def main() -> None:
    pm, minutes, teams, proj, bs = load()
    rates = per90_rates(pm, minutes, bs)
    rates["dc_rate"] = rates.element.map(dc_hit_rates(pm, rates)).fillna(0.0)
    tau = fit_bonus_temperature(pm)
    print(f"  bonus-temperatur tilpasset: {tau:.1f}")
    tmatch = pd.read_csv(DERIVED / "team_matches.csv")
    goal_scale, cs_infl, con_infl = calibrate_goals(pm, tmatch, proj)
    xp = expected_points(rates, teams, proj, tau, goal_scale, cs_infl, con_infl)

    xp.to_csv(DERIVED / "expected_points.csv", index=False)
    horizon = (xp.groupby(["element", "web_name", "team", "pos", "price"], as_index=False)
               .agg(xp_total=("xp", "sum"), gws=("gw", "nunique")))
    horizon["xp_per_gw"] = horizon.xp_total / horizon.gws
    horizon["value"] = horizon.xp_total / horizon.price
    horizon.sort_values("xp_total", ascending=False).to_csv(
        DERIVED / "expected_points_horizon.csv", index=False)

    print(f"✓ {len(xp)} spiller-kamper over GW{xp.gw.min()}-{xp.gw.max()}")
    print("\n--- høyest xP over horisonten ---")
    top = horizon.nlargest(12, "xp_total")[["web_name", "team", "pos", "price", "xp_total", "xp_per_gw"]]
    print(top.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
