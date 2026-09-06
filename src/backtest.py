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

# Hvor mange minutter en spiller må ha spilt før hans egne xG- og xA-rater veier
# like mye som posisjonsprioren. Lav verdi lar en heldig måned overdøve alt vi
# vet fra før; høy verdi gjør at Haaland ser ut som en gjennomsnittsspiss ut
# sesongen.
#
# MÅLT 5. sep 2026, til slutt på 72 189 parvise prediksjoner over TRE sesonger:
#
#   verdi   MAE mot 270        topp 10 mot 270
#    135    +0.00042 (3.0 se)  —                  klart verre
#    270     grunnlinje         grunnlinje
#    400    -0.00023 (2.5 se)  -0.033 (1.2 se)
#    540    -0.00036 (2.2 se)  +0.032 (0.9 se)
#    700    -0.00043 (1.8 se)  +0.069 (1.4 se)
#    900    -0.00050 (1.3 se)  +0.023 (0.3 se)   (to sesonger)
#   1500    -0.00029 (0.5 se)  -0.034 (0.4 se)   (to sesonger)
#
# HVA SOM ER ETABLERT OG HVA SOM IKKE ER DET. At 270 er for lavt, er etablert:
# alle verdier over slår den på feil, og alle tre sesongene peker samme vei.
# Hvilken verdi over 270 som er best, er IKKE etablert — 400, 540 og 700 kan
# ikke skilles.
#
# På to sesonger så 540 ut til å vinne klart på topp 10 (+0.087, 2.3 se). Med
# den tredje sesongen falt det til +0.032 (0.9 se). Den delen av funnet var
# altså delvis flaks. 540 beholdes fordi den ligger midt i båndet som slår 270,
# ikke fordi den er målt best.
SHRINK_MINUTES = 540.0
PRIOR_MATCHES_MIN = 0.7
# Vekten på spillerens EGEN startrate fra i fjor, målt i kamper. Samme navn og
# verdi som i minutes.py, slik at backtesten måler produksjonens minuttmodell
# og ikke en forenkling av den.
PRIOR_MATCHES_PERSONAL = 1.5
PRIOR_WEIGHT_AFTER_TRANSFER = 0.35   # klubbskifte gjør fjorårets rolle mindre relevant
# Satt til 8.0 for å matche produksjonsmodellen (team_strength.PRIOR_WEIGHT_MATCHES).
#
# Målt 5. sep 2026, tre kjøringer per konfigurasjon (sesongtotal, 2025-26):
#   uinformativ prior, vekt 4 : 2122 ± 26
#   informativ prior,  vekt 8 : 2099 ± 16   ← 1.3 se fra over, ikke skillbar
#   uinformativ prior, vekt 8 : 2076 ± 20
#   informativ prior,  vekt 4 : 2074 ±  2
#
# Mønsteret er ikke monotont og lar seg ikke avgjøre med denne presisjonen.
# Valget her er derfor troskap mot produksjonen, ikke en påstand om at det er
# optimalt. Skal spørsmålet avgjøres, trengs flere sesonger i evalueringen.
PRIOR_WEIGHT_TEAM = 8.0


def load() -> pd.DataFrame:
    d = pd.read_csv(f"{HIST}/gws/merged_gw.csv")
    keep = ["name", "position", "team", "GW", "fixture", "opponent_team", "was_home",
            "minutes", "starts", "total_points", "goals_scored", "assists",
            "clean_sheets", "goals_conceded", "saves", "bonus", "bps",
            "expected_goals", "expected_assists", "defensive_contribution",
            "yellow_cards", "red_cards"]
    # defensive_contribution kom først i 2025-26. For tidligere sesonger settes
    # den til null — det er riktig, for kategorien fantes ikke og ga null poeng.
    for col in keep:
        if col not in d.columns:
            d[col] = 0
    d = d[keep].copy()
    d["pos"] = d.position.map({"GKP": "GK", "GK": "GK", "DEF": "DEF", "MID": "MID",
                               "FWD": "FWD", "AM": "MID"}).fillna("MID")
    return d


def team_ratings(train: pd.DataFrame,
                 prior: tuple[dict, dict] | None = None) -> tuple[dict, dict, float, float]:
    """
    Angreps- og forsvarsrating fra xG, med samme estimator som i produksjon.

    `prior` er forrige sesongs ratinger. Uten den krympes lagene mot
    ligagjennomsnittet, altså mot "alle er like gode" — det er en uinformativ
    prior, og da må vekten være lav for ikke å viske ut reelle forskjeller.
    Produksjonsmodellen krymper mot fjorårets faktiske ratinger og kan derfor
    bruke høyere vekt. Simuleringen skal etterligne produksjonen, ikke en
    enklere variant av den.
    """
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
    if prior is None:
        pa, pd_ = np.zeros(n), np.zeros(n)
    else:
        pa = np.array([prior[0].get(t, 0.0) for t in teams])
        pd_ = np.array([prior[1].get(t, 0.0) for t in teams])
    att, dfn, home_adv, mu, _ = _fit(
        pair.h.map(idx).to_numpy(), pair.a.map(idx).to_numpy(),
        pair.xg_h.to_numpy(float), pair.xg_a.to_numpy(float),
        n, np.ones(len(pair)), pa, pd_,
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


def start_prior(prev_season: pd.DataFrame) -> pd.DataFrame:
    """
    Startrate per spiller fra forrige sesong, krympet mot ligagrunnraten slik
    at den aldri blir 0 eller 1.
    """
    agg = prev_season.groupby("name", as_index=False).agg(
        starts=("starts", "sum"), rounds=("starts", "size"), mins=("minutes", "sum"))
    agg = agg[agg.mins >= 450].copy()
    league = float((prev_season.starts == 1).mean())
    agg["prior_p_start"] = (agg.starts + 4.0 * league) / (agg.rounds + 4.0)
    team = prev_season.groupby("name").team.last()
    agg["prior_team"] = agg.name.map(team)
    return agg[["name", "prior_p_start", "prior_team"]]


# Dødball- og straffeansvar. MÅLT TIL Å IKKE VIRKE — ikke slå på uten ny test.
#
# FPL-API-et har `penalties_order`, `direct_freekicks_order` og
# `corners_and_indirect_freekicks_order`. Tillegget legges på PRIOREN, ikke på
# observerte rater, for ikke å dobbelttelle straffer som allerede ligger i
# spillerens xG-historikk.
#
# Størrelsen er utledet, ikke tilpasset: ~100 straffer på 380 kamper = 0.13 per
# lag-kamp, førstevalget tar ~85 %, en straffe har xG ~0.79 → ~0.087 per 90.
#
# RESULTAT (5. sep 2026, fire kjøringer per konfigurasjon): −10 ± 12 poeng over
# en sesong. Ingen målbar effekt. Sannsynlig årsak: historisk xG fanger allerede
# de etablerte takerne, og prioren betyr lite for spillere med spilletid.
# Funksjonen er derfor avslått som standard (roles=None) og beholdes bare for
# å dokumentere forsøket.
PEN_XG90 = 0.087
FK_XG90 = 0.020        # direkte frispark, førstevalg
CORNER_XA90 = 0.030    # corner og indirekte frispark, førstevalg


def setpiece_bonus(names: pd.Series, roles: pd.DataFrame | None):
    """Returnerer (xg-tillegg, xa-tillegg) per spiller ut fra dødballansvar."""
    if roles is None or roles.empty:
        z = pd.Series(0.0, index=names.index)
        return z, z
    r = roles.set_index("name")
    xg = names.map(lambda n: (PEN_XG90 if r.get("pen", {}).get(n, 9) == 1 else 0.0)
                   + (FK_XG90 if r.get("fk", {}).get(n, 9) == 1 else 0.0)).fillna(0.0)
    xa = names.map(lambda n: CORNER_XA90 if r.get("ck", {}).get(n, 9) == 1 else 0.0).fillna(0.0)
    return xg, xa


def per90(train: pd.DataFrame, sprior: pd.DataFrame | None = None,
          roles: pd.DataFrame | None = None) -> pd.DataFrame:
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

    sp_xg, sp_xa = setpiece_bonus(agg.name, roles)
    for s in stats:
        raw = np.where(agg.mins > 0, agg[s] / agg.mins.clip(lower=1) * 90, np.nan)
        prior = pd.Series(raw).groupby(agg.pos.values).transform("mean").fillna(0)
        if s == "expected_goals":
            prior = prior + sp_xg.values
        elif s == "expected_assists":
            prior = prior + sp_xa.values
        w = agg.mins / (agg.mins + SHRINK_MINUTES)
        agg[f"{s}90"] = w * pd.Series(raw).fillna(0) + (1 - w) * prior

    # Minutter: startandel med krymping, som i M2.
    #
    # Med en personlig prior fra forrige sesong veier prioren mye mer (2.5
    # kamper mot 0.7), fordi den faktisk sier noe om spilleren. Uten den er
    # prioren bare ligagjennomsnittet og skal veie lite. Spillere som har
    # byttet klubb får prioren nedvektet — fjorårets rolle er mindre
    # overførbar da.
    base = float((train[train.minutes > 0].starts == 1).mean()) * 0.5
    now_team = train.groupby("name").team.last()
    # NB: den lokale variabelen `prior` er allerede i bruk i sløyfen over,
    # derfor heter parameteren `sprior`.
    if sprior is not None and not sprior.empty:
        pr = sprior.set_index("name")
        p_prior, k = [], []
        for nm in agg.name:
            if nm in pr.index:
                p_prior.append(float(pr.prior_p_start[nm]))
                moved = str(pr.prior_team.get(nm, "")).lower() != str(now_team.get(nm, "")).lower()
                k.append(PRIOR_MATCHES_PERSONAL * (PRIOR_WEIGHT_AFTER_TRANSFER if moved else 1.0))
            else:
                p_prior.append(base); k.append(PRIOR_MATCHES_MIN)
        p_prior, k = np.array(p_prior), np.array(k)
    else:
        p_prior, k = np.full(len(agg), base), np.full(len(agg), PRIOR_MATCHES_MIN)
    agg["p_start"] = ((agg.starts + k * p_prior) / (agg.apps + k)).clip(0, 1)

    if not SUB_MINUTES:
        agg["p_play"] = agg.p_start
        agg["p_60"] = agg.p_start * 0.95
        agg["exp_min"] = agg.p_start * 82.0
        return agg

    # Innbyttere. Uten dette leddet er en spiller som aldri starter, men alltid
    # kommer inn etter en time, verdt null — han får hverken oppmøtepoeng eller
    # noen andel av angrepstallene sine. Det er feil på to måter: det
    # undervurderer rotasjonsspillere, og det gjør benken i optimeringen
    # kunstig verdiløs, slik at billige spillere som faktisk spiller ikke får
    # den kreditten de skal ha.
    #
    # Ratene under hentes fra treningsdataene i stedet for å gjettes, slik at
    # de følger sesongen: hvor ofte en start blir til 60 minutter, og hvor mye
    # et innhopp faktisk gir.
    starts_rows = train[train.starts == 1]
    sub_rows = train[(train.starts == 0) & (train.minutes > 0)]
    p60_start = float((starts_rows.minutes >= 60).mean()) if len(starts_rows) else 0.95
    min_start = float(starts_rows.minutes.mean()) if len(starts_rows) else 82.0
    p60_sub = float((sub_rows.minutes >= 60).mean()) if len(sub_rows) else 0.02
    min_sub = float(sub_rows.minutes.mean()) if len(sub_rows) else 20.0

    played = train[train.minutes > 0].groupby("name").size()
    agg["sub_apps"] = (agg.name.map(played).fillna(0) - agg.starts).clip(lower=0)
    league_sub = float(len(sub_rows) / max(len(train), 1))
    agg["p_sub"] = ((agg.sub_apps + PRIOR_MATCHES_MIN * league_sub)
                    / (agg.apps + PRIOR_MATCHES_MIN))
    # Start og innhopp utelukker hverandre i samme kamp.
    agg["p_sub"] = np.minimum(agg.p_sub, (1 - agg.p_start).clip(lower=0))

    agg["p_play"] = (agg.p_start + agg.p_sub).clip(0, 1)
    agg["p_60"] = agg.p_start * p60_start + agg.p_sub * p60_sub
    agg["exp_min"] = agg.p_start * min_start + agg.p_sub * min_sub
    return agg


# Skalering av angrepstall etter motstander.
#
# En spillers xG per 90 er et snitt over kampene han har spilt — mot gode og
# dårlige lag om hverandre. Brukes det tallet rått, får en spiss nøyaktig samme
# forventning hjemme mot Wolves som borte mot Arsenal. Det er åpenbart feil, og
# lagmodellen vet allerede bedre: den gir λ_for for akkurat den kampen.
#
# Skaleringen er λ_for delt på hva laget ville hatt mot en gjennomsnittlig
# motstander. Nevneren gjør den nøytral i snitt, slik at totalnivået ikke
# flyttes — bare fordelingen mellom lette og tunge kamper.
#
# Produksjonsmodellen (expected_points.att_scale) har alltid gjort dette.
# Simuleringen gjorde det ikke, og målte derfor en svakere modell enn den som
# faktisk kjøres. Flagget finnes for å kunne måle forskjellen parvis.
ATT_SCALING = True

# Innbytterminutter — se per90(). AV I PÅVENTE AV MÅLING PÅ SESONGNIVÅ.
#
# Målt 5. sep 2026, parvis over 47 500 prediksjoner i to sesonger:
#   MAE       1.0539 → 1.0862   (30 se DÅRLIGERE)
#   RMSE      2.0803 → 2.0586   (bedre)
#   Spearman  0.3368 → 0.3387   (bedre)
#   topp 10   4.78 → 4.69       (1.8 se dårligere)
#
# At MAE blir verre mens RMSE blir bedre er ikke en selvmotsigelse. To
# tredjedeler av radene er spillere som ikke spilte. For dem er null det som
# minimerer absoluttfeilen, og enhver positiv forventning straffes. Men FPL
# summerer poeng, og da er forventningen det riktige — og en fast innbytter har
# ikke forventning null. MAE er altså feil målestokk her, RMSE den rette.
#
# Verdien av leddet ligger uansett ikke blant topp 10; der er alle faste
# startere. Den ligger på benken og blant billige spillere som faktisk kommer
# inn — og dét ser bare sesongsimuleringen. Til det er målt, står den av, slik
# at ingen umålt endring går i produksjon.
SUB_MINUTES = False


def _fixture_scale(att: dict, dfn: dict, home_adv: float, mu: float) -> dict:
    """Lagets forventede xG mot en gjennomsnittsmotstander, halvparten hjemme."""
    if not att or not dfn:
        return {}
    mean_def = float(np.mean(list(dfn.values())))
    return {t: float(np.exp(mu + a - mean_def + 0.5 * home_adv)) for t, a in att.items()}


def predict(test: pd.DataFrame, rates: pd.DataFrame, att, dfn, home_adv, mu,
            disp: float) -> pd.DataFrame:
    r = rates.set_index("name")
    base_lam = _fixture_scale(att, dfn, home_adv, mu) if ATT_SCALING else {}
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
        a_scale = lam_for / base_lam[row.team] if row.team in base_lam else 1.0
        xp = (p.p_play + p.p_60
              + p.expected_goals90 * share * a_scale * GOAL_POINTS[p.pos]
              + p.expected_assists90 * share * a_scale * 3
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
