"""
M1 — lagstyrke. Erstatter FPLs FDR.

FDR er et heltall 1-5 satt før sesongen, oppdateres aldri, og skiller ikke
angrep fra forsvar. At Coventry har FDR 2 betyr både "lett å score på" og
"scorer lite" — to helt ulike ting, og for en forsvarsspiller er det andre
som teller.

Her estimeres i stedet en angrepsrating og en forsvarsrating per lag:

    log λ(i mot j) = μ + att_i − def_j + h·[i spiller hjemme]

λ er forventede mål i den kampen. Da faller alt annet ut av seg selv:
P(clean sheet) = P(motstander scorer 0) = exp(−λ_motstander) under Poisson.

TO TING SOM GJØR DENNE BRUKBAR I SEPTEMBER

1. Den tilpasses på xG, ikke mål. xG har mye lavere varians per kamp, så den
   sier mer om laget etter tre runder enn resultatene gjør.

2. Den krymper mot forrige sesong. Uten det er modellen ubrukelig tidlig:
   på data fra to runder rangerer rå xG-differanse Manchester United som
   ligaens beste lag. Det er småtallsstøy, og en modell som tror på det
   kjøper dyrt rett før tallene faller mot normalen.

Krympingen er en straffeterm i optimeringen, ikke et etterpå-snitt. Det gir
riktig oppførsel automatisk: straffen har fast vekt mens datamengden vokser,
så priorens innflytelse avtar av seg selv utover sesongen.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"
PRIOR = ROOT / "data" / "prior"

# Hvor mange kamper prioren er "verdt". Med k=8 teller tre spilte runder ca. 27 %
# data og 73 % prior; ved 24 kamper er forholdet snudd. Verdien er et valg, ikke
# en sannhet — den bør kalibreres i M9 når vi har nok runder å teste mot.
PRIOR_WEIGHT_MATCHES = 8.0

# Halveringstid i kamper for tidsvekting av inneværende sesong.
HALF_LIFE_MATCHES = 10.0


def _fit(
    home_idx: np.ndarray,
    away_idx: np.ndarray,
    goals_home: np.ndarray,
    goals_away: np.ndarray,
    n_teams: int,
    weights: np.ndarray,
    prior_att: np.ndarray,
    prior_def: np.ndarray,
    penalty: float,
    fixed_home_adv: float | None = None,
):
    """
    Penalisert quasi-Poisson. y kan være xG (kontinuerlig) — Poisson-
    loglikelihooden er fortsatt en gyldig quasi-likelihood da, og gir samme
    estimater som en log-lineær regresjon med Poisson-varians.
    """

    def unpack(p):
        att = p[:n_teams]
        dfn = p[n_teams : 2 * n_teams]
        # Sentrer for identifikasjon — ellers kan man flytte en konstant fritt
        # mellom att, def og μ uten å endre likelihooden.
        home = p[-2] if fixed_home_adv is None else fixed_home_adv
        return att - att.mean(), dfn - dfn.mean(), home, p[-1]

    def neg_ll(p):
        att, dfn, home_adv, mu = unpack(p)
        log_lh = mu + att[home_idx] - dfn[away_idx] + home_adv
        log_la = mu + att[away_idx] - dfn[home_idx]
        lh, la = np.exp(log_lh), np.exp(log_la)

        ll = np.sum(weights * (goals_home * log_lh - lh))
        ll += np.sum(weights * (goals_away * log_la - la))

        pen = penalty * (np.sum((att - prior_att) ** 2) + np.sum((dfn - prior_def) ** 2))
        return -ll + pen

    x0 = np.concatenate([prior_att, prior_def, [0.25, np.log(1.35)]])
    res = minimize(neg_ll, x0, method="L-BFGS-B",
                   options={"maxiter": 5000, "ftol": 1e-10})
    att, dfn, home_adv, mu = unpack(res.x)
    return att, dfn, home_adv, mu, res


PRIOR_SOURCE = ("https://raw.githubusercontent.com/vaastav/"
                "Fantasy-Premier-League/master/data/2025-26")


def ensure_prior_files() -> None:
    """
    Forrige sesongs kampresultater. Statiske data, så de lastes ned én gang og
    committes — ikke hentet på nytt hver kjøring.
    """
    import urllib.request
    PRIOR.mkdir(parents=True, exist_ok=True)
    for name, src in (("fixtures_2025-26.csv", "fixtures.csv"),
                      ("teams_2025-26.csv", "teams.csv")):
        target = PRIOR / name
        if target.exists() and target.stat().st_size > 0:
            continue
        print(f"  laster ned {name}")
        urllib.request.urlretrieve(f"{PRIOR_SOURCE}/{src}", target)


def fit_prior_from_last_season() -> tuple[pd.DataFrame, float]:
    """
    Rating fra forrige sesong, tilpasset på faktiske mål over 380 kamper.
    Mål er støyete per kamp, men over en hel sesong er datamengden rikelig.

    Lag-ID-er endres mellom sesonger (FPL nummererer alfabetisk hvert år), så
    sammenkoblingen må skje på lagkode, aldri på ID.
    """
    ensure_prior_files()
    fx = pd.read_csv(PRIOR / "fixtures_2025-26.csv")
    tm = pd.read_csv(PRIOR / "teams_2025-26.csv")
    fx = fx[fx["finished"] & fx["team_h_score"].notna()].copy()

    ids = sorted(set(fx.team_h) | set(fx.team_a))
    pos = {t: i for i, t in enumerate(ids)}
    n = len(ids)

    att, dfn, home_adv, mu, res = _fit(
        fx.team_h.map(pos).to_numpy(),
        fx.team_a.map(pos).to_numpy(),
        fx.team_h_score.to_numpy(float),
        fx.team_a_score.to_numpy(float),
        n,
        np.ones(len(fx)),
        np.zeros(n),
        np.zeros(n),
        penalty=0.5,          # svak regularisering, bare for numerisk stabilitet
    )

    code = dict(zip(tm.id, tm.short_name))
    frame = pd.DataFrame({
        "short_name": [code[t] for t in ids],
        "prior_att": att,
        "prior_def": dfn,
    })
    return frame, float(home_adv)


def build_priors(teams_now: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """
    Kobler forrige sesongs rating til årets lag. Opprykkslag fantes ikke i
    Premier League i fjor og får derfor snittet av forrige sesongs tre svakeste
    lag — det er den beste tilgjengelige gjetningen, og den er konservativ.
    """
    prior, home_adv = fit_prior_from_last_season()
    merged = teams_now.merge(prior, on="short_name", how="left")

    bottom = prior.assign(net=prior.prior_att - prior.prior_def).nsmallest(3, "net")
    fallback_att, fallback_def = bottom.prior_att.mean(), bottom.prior_def.mean()

    promoted = merged.prior_att.isna()
    if promoted.any():
        print(f"  opprykkslag uten fjorårsdata: {', '.join(merged.loc[promoted, 'short_name'])}"
              f" → prior satt til snittet av fjorårets tre svakeste")
    merged["prior_att"] = merged.prior_att.fillna(fallback_att)
    merged["prior_def"] = merged.prior_def.fillna(fallback_def)
    return merged, home_adv


def load_current_matches() -> pd.DataFrame:
    """
    Lag-kamper fra inneværende sesong, KUN ferdigspilte.

    En kamp som pågår har ufullstendig xG og ville dratt laget kunstig ned.
    Sjekken må gå på at kampen er `finished` i fixtures — ikke på at det finnes
    minutter, for en kamp i 20. minutt har også minutter.
    """
    tm = pd.read_csv(DERIVED / "team_matches.csv")
    fixtures = pd.DataFrame(json.loads((RAW / "fixtures.json").read_text()))
    done = set(fixtures.loc[fixtures["finished"] == True, "id"])  # noqa: E712
    before = tm.fixture.nunique()
    tm = tm[tm.fixture.isin(done)]
    print(f"  kamper: {tm.fixture.nunique()} ferdigspilte (av {before} med data)")
    return tm


def fit_current(matches: pd.DataFrame, priors: pd.DataFrame, home_adv_prior: float) -> pd.DataFrame:
    teams = priors.short_name.tolist()
    idx = {t: i for i, t in enumerate(priors.team_id)}
    n = len(teams)

    home = matches[matches.was_home].copy()
    pair = home.merge(
        matches[~matches.was_home][["fixture", "xg_for"]].rename(columns={"xg_for": "xg_away"}),
        on="fixture", how="inner",
    )

    # Nyere kamper veier mer.
    order = pair.sort_values("gw").reset_index(drop=True)
    age = order.gw.max() - order.gw
    weights = 0.5 ** (age / HALF_LIFE_MATCHES)

    n_matches = matches.groupby("team").fixture.nunique().mean()
    penalty = PRIOR_WEIGHT_MATCHES / 2.0   # per lag, per retning (att og def)

    att, dfn, home_adv, mu, res = _fit(
        order.team.map(idx).to_numpy(),
        order.opponent.map(idx).to_numpy(),
        order.xg_for.to_numpy(float),
        order.xg_away.to_numpy(float),
        n,
        weights.to_numpy(),
        priors.prior_att.to_numpy(),
        priors.prior_def.to_numpy(),
        penalty=penalty,
        # Hjemmefordel er en ligakonstant, ikke en lagegenskap, og den endrer seg
        # lite fra sesong til sesong. Estimert på 20 kamper blir den ren støy —
        # den låses derfor til fjorårets verdi, tilpasset på 380 kamper.
        fixed_home_adv=home_adv_prior,
    )

    out = priors.copy()
    out["att"], out["def"] = att, dfn
    out["home_adv"], out["mu"] = home_adv, mu
    out["n_matches"] = out.team_id.map(matches.groupby("team").fixture.nunique()).fillna(0)
    # Forventede mål mot et gjennomsnittslag på nøytral bane — tolkbar skala.
    out["xg_vs_avg"] = np.exp(mu + out.att)
    out["xga_vs_avg"] = np.exp(mu - out["def"])
    out["net"] = out.xg_vs_avg - out.xga_vs_avg
    print(f"  konvergerte: {res.success} | hjemmefordel: {np.exp(home_adv):.3f}× "
          f"| snitt {np.exp(mu):.2f} mål/lag/kamp | {n_matches:.1f} kamper per lag")
    return out.sort_values("net", ascending=False).reset_index(drop=True)


def project_fixtures(ratings: pd.DataFrame, n_gw: int = 8) -> pd.DataFrame:
    """
    Forventede mål og clean sheet-sannsynlighet for hver kommende kamp.

    Dette er raden som erstatter FDR. I stedet for ett heltall får hvert lag to
    tall per kamp: hvor mye de ventes å score, og hvor mye de ventes å slippe
    inn. En forsvarsspiller bryr seg om det andre, en angrepsspiller om det
    første — FDR blandet dem sammen til ett tall.
    """
    fixtures = pd.DataFrame(json.loads((RAW / "fixtures.json").read_text()))
    upcoming = fixtures[(fixtures["finished"] != True) & fixtures["event"].notna()]  # noqa: E712
    if upcoming.empty:
        return pd.DataFrame()
    first = int(upcoming.event.min())
    upcoming = upcoming[upcoming.event < first + n_gw]

    r = ratings.set_index("team_id")
    mu, home_adv = float(ratings.mu.iloc[0]), float(ratings.home_adv.iloc[0])
    rows = []
    for _, f in upcoming.iterrows():
        h, a = int(f.team_h), int(f.team_a)
        lam_h = np.exp(mu + r.att[h] - r["def"][a] + home_adv)
        lam_a = np.exp(mu + r.att[a] - r["def"][h])
        for team, opp, lam_for, lam_ag, is_home, fdr in (
            (h, a, lam_h, lam_a, True, f.team_h_difficulty),
            (a, h, lam_a, lam_h, False, f.team_a_difficulty),
        ):
            rows.append({
                "gw": int(f.event), "fixture": int(f.id),
                "team": r.short_name[team], "opponent": r.short_name[opp],
                "home": is_home, "fdr": int(fdr),
                "xg_for": round(float(lam_for), 3),
                "xg_against": round(float(lam_ag), 3),
                # Poisson: P(motstander scorer 0). Dixon-Coles-korreksjon for
                # lave resultater er ikke lagt inn ennå — den flytter denne noen
                # prosentpoeng og hører hjemme i M4.
                "p_clean_sheet": round(float(np.exp(-lam_ag)), 4),
            })
    return pd.DataFrame(rows).sort_values(["gw", "fixture"]).reset_index(drop=True)


def main() -> None:
    bs = json.loads((RAW / "bootstrap.json").read_text())
    teams_now = pd.DataFrame([{"team_id": t["id"], "short_name": t["short_name"]}
                              for t in bs["teams"]])

    print("Prior fra 2025-26:")
    priors, home_adv_prior = build_priors(teams_now)
    print(f"  hjemmefordel fra 380 kamper: {np.exp(home_adv_prior):.3f}×")
    print("Inneværende sesong:")
    matches = load_current_matches()
    ratings = fit_current(matches, priors, home_adv_prior)

    DERIVED.mkdir(parents=True, exist_ok=True)
    cols = ["team_id", "short_name", "att", "def", "prior_att", "prior_def",
            "n_matches", "xg_vs_avg", "xga_vs_avg", "net", "home_adv", "mu"]
    ratings[cols].to_csv(DERIVED / "team_ratings.csv", index=False)

    proj = project_fixtures(ratings)
    if not proj.empty:
        proj.to_csv(DERIVED / "fixture_projections.csv", index=False)
        print(f"\n  {len(proj)} lag-kamper projisert over GW{proj.gw.min()}-{proj.gw.max()}")

    print("\n--- lagstyrke etter krymping (forventede mål mot et snittlag) ---")
    show = ratings[["short_name", "xg_vs_avg", "xga_vs_avg", "net"]].round(2)
    print(show.to_string(index=False))


if __name__ == "__main__":
    main()
