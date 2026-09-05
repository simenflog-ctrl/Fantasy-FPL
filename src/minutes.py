"""
M2 — minuttmodell.

Den viktigste modellen i systemet, og den mest oversette. Forventede poeng
skalerer nesten lineært med sannsynligheten for å spille: en spiller som starter
halvparten av kampene er verdt omtrent halvparten så mye, uansett hvor god han er.
De fleste FPL-katastrofer er rotasjon, ikke feilvurdert kvalitet.

Modellen gir tre tall per spiller:

    p_start      sannsynlighet for å starte neste kamp
    p_60         sannsynlighet for å spille 60+ minutter (poenggrensa)
    exp_minutes  forventede minutter

TO KILDER SOM MÅ KOMBINERES

Historikken sier hva som har skjedd. Skadeflagg og spilletidsprosent fra API-et
sier hva klubben har meldt. Det siste overstyrer alltid det første: en spiller
med tre strake starter og et ferskt skadeflagg har p_start 0, ikke 1.

DET MODELLEN IKKE KAN SE

API-et fanger ikke pressekonferanser. "Arteta sier Konsa starter framover" finnes
ikke i noe felt. Derfor er dette laget der Claudes ukentlige nyhetssøk skal
overstyre manuelt — modellen leverer utgangspunktet, ikke fasiten.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"

# Halveringstid i kamper. Kort, fordi rolleendringer skjer raskt: en spiller som
# mistet plassen for tre runder siden er mindre relevant enn forrige helg.
HALF_LIFE = 4.0

# Styrken på krympingen, i "antall kamper prioren er verdt".
#
# To slags prior:
#
# GENERISK — ligaens ubetingede startrate. Sier ingenting om spilleren, så den
# skal veie lite. Satt for høyt (2.0 ble prøvd) kollapser modellen: da fikk hver
# eneste startende spiller identisk p_start.
#
# PERSONLIG — spillerens egen startrate fra i fjor. Den er informativ og skiller
# det årets to runder ikke kan: Haaland startet 34 av 38, Maguire 19 av 38.
#
# Vekten på den personlige ble først satt til 2.5. Det var for høyt: prioren fikk
# over halve vekten etter to runder og overkjørte ferske bevis — De Cuyper startet
# begge kampene med 77 og 90 minutter og fikk likevel p_start 0.67. Målt på en
# hel simulert sesong ga 2.5 bare +3 poeng, mens 1.5 ga +61.
PRIOR_MATCHES_GENERIC = 0.7
PRIOR_MATCHES_PERSONAL = 1.5

LAST_SEASON_GWS = ("https://raw.githubusercontent.com/vaastav/"
                   "Fantasy-Premier-League/master/data/2025-26/gws/merged_gw.csv")

# Minste spilletid i fjor for at spillerens egen rate skal brukes.
MIN_PRIOR_MINUTES = 450

# Krymping AV selve fjorårsprioren, i pseudo-kamper mot ligagrunnraten. En
# spiller som startet 38 av 38 skal ikke få prior 1.00 — ingen starter med
# sikkerhet. Det finnes alltid hvile, skader og karantener.
PRIOR_SELF_SHRINK = 4.0

# Klubbytte gjør fjorårets rolle mindre overførbar: ny klubb, ny konkurranse,
# ofte ny rolle. Konsa er eksempelet — høy startrate i fjor, ny klubb, null
# starter i år. Uten nedvektingen trakk prioren ham opp til 0.52 stikk i strid
# med det som faktisk har skjedd.
PRIOR_WEIGHT_AFTER_TRANSFER = 0.35

# Status-koder i FPL-API-et som betyr at spilleren ikke er tilgjengelig.
UNAVAILABLE = {"i", "s", "u", "n"}


def _norm(s: pd.Series) -> pd.Series:
    return (s.astype(str).str.normalize("NFKD").str.encode("ascii", "ignore")
            .str.decode("ascii").str.lower().str.strip())


def last_season_minutes(bs: dict) -> pd.DataFrame:
    """
    Spillerens egen startrate og typiske spilletid fra forrige sesong.

    Uten dette krympes alle mot ligagjennomsnittet, og da får hver spiller med
    to starter av to nøyaktig samme p_start — modellen kan ikke skille en fast
    starter fra en rotasjonsspiller før langt uti sesongen.
    """
    try:
        ls = pd.read_csv(LAST_SEASON_GWS)
    except Exception as exc:  # noqa: BLE001
        print(f"  fant ikke fjorårsdata ({exc}) — bruker bare ligaprior")
        return pd.DataFrame(columns=["element"])

    agg = ls.groupby("name", as_index=False).agg(
        starts=("starts", "sum"), rounds=("starts", "size"),
        mins=("minutes", "sum"))
    started = ls[ls.starts == 1].groupby("name", as_index=False).agg(
        min_given_start=("minutes", "mean"))
    agg = agg.merge(started, on="name", how="left")
    agg = agg[agg.mins >= MIN_PRIOR_MINUTES].copy()
    agg["key"] = _norm(agg.name)
    league = float((ls.starts == 1).mean())
    agg["prior_p_start"] = ((agg.starts + PRIOR_SELF_SHRINK * league)
                            / (agg.rounds + PRIOR_SELF_SHRINK))
    agg["prior_team"] = agg.name.map(ls.groupby("name").team.last())

    # MÅ sammenlignes mot lagets fulle navn, ikke forkortelsen: fjorårsdataene
    # bruker "Aston Villa", API-et har begge former. Sammenligning mot
    # forkortelsen ga falske klubbytter for nesten halve ligaen.
    teams_now = {t["id"]: t["name"] for t in bs["teams"]}
    now = pd.DataFrame([{"element": e["id"], "team_now": teams_now[e["team"]],
                         "key": f"{e['first_name']} {e['second_name']}"}
                        for e in bs["elements"]])
    now["key"] = _norm(now.key)
    out = now.merge(agg[["key", "prior_p_start", "min_given_start", "prior_team"]],
                    on="key", how="inner").drop_duplicates("element")
    out["moved"] = out.prior_team.astype(str).str.strip().str.lower() != \
        out.team_now.astype(str).str.strip().str.lower()
    print(f"  fjorårsprior for spilletid: {len(out)} av {len(now)} spillere "
          f"({int(out.moved.sum())} har byttet klubb — prior nedvektet)")
    return out[["element", "prior_p_start", "min_given_start", "moved"]]


def load() -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    pm = pd.read_csv(DERIVED / "player_matches.csv")
    bs = json.loads((RAW / "bootstrap.json").read_text())
    fixtures = pd.DataFrame(json.loads((RAW / "fixtures.json").read_text()))
    done = set(fixtures.loc[fixtures["finished"] == True, "id"])  # noqa: E712
    return pm[pm.fixture.isin(done)].copy(), bs, fixtures


def league_rates(pm: pd.DataFrame) -> dict:
    """
    Grunnrater estimert fra data i stedet for gjettet. Disse brukes både som
    prior og til å oversette p_start til forventede minutter.
    """
    started = pm[pm.starts == 1]
    subbed = pm[(pm.starts == 0) & (pm.minutes > 0)]
    appeared = pm[pm.minutes > 0]
    # Prioren må være den ubetingede sannsynligheten for at en registrert
    # spiller starter en gitt kamp — altså 11 av tropplista, ikke 11 av dem som
    # faktisk spilte. Bruker man den betingede raten (~0.71), blir en spiller som
    # aldri har spilt behandlet som en halvveis starter.
    n_players_per_team = len(pm.element.unique()) / 20 if len(pm) else 25
    return {
        "p_start_prior": float(np.clip(11.0 / max(n_players_per_team, 11.0), 0.05, 0.95)),
        "p_start_given_appeared": float((appeared.starts == 1).mean()),
        "min_given_start": float(started.minutes.mean()) if len(started) else 80.0,
        "p60_given_start": float((started.minutes >= 60).mean()) if len(started) else 0.85,
        "min_given_sub": float(subbed.minutes.mean()) if len(subbed) else 20.0,
    }


def availability(el: dict) -> tuple[float, str]:
    """
    Oversetter klubbmeldingene til en multiplikator. Returnerer også en kort
    grunn, slik at et null-tall alltid kan forklares.
    """
    status = el.get("status", "a")
    if status in UNAVAILABLE:
        return 0.0, f"status={status}"

    chance = el.get("chance_of_playing_next_round")
    if chance is not None:
        return float(chance) / 100.0, f"{int(chance)}% sjanse"
    if status == "d":
        return 0.5, "tvilsom, ingen prosent oppgitt"
    return 1.0, ""


def build(pm: pd.DataFrame, bs: dict, rates: dict) -> pd.DataFrame:
    pos = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
    teams = {t["id"]: t["short_name"] for t in bs["teams"]}

    latest_gw = pm.gw.max()
    prior = last_season_minutes(bs).set_index("element")
    rows = []

    by_player = {pid: g.sort_values("gw") for pid, g in pm.groupby("element")}

    for el in bs["elements"]:
        pid = el["id"]
        hist = by_player.get(pid)

        # Personlig prior der den finnes, ellers ligaens grunnrate.
        if pid in prior.index and not np.isnan(prior.prior_p_start.get(pid, np.nan)):
            p_prior = float(prior.prior_p_start[pid])
            k = (PRIOR_MATCHES_PERSONAL * PRIOR_WEIGHT_AFTER_TRANSFER
                 if bool(prior.moved.get(pid, False)) else PRIOR_MATCHES_PERSONAL)
            mgs = prior.min_given_start.get(pid, np.nan)
            prior_min = float(mgs) if not np.isnan(mgs) else rates["min_given_start"]
        else:
            p_prior, k = rates["p_start_prior"], PRIOR_MATCHES_GENERIC
            prior_min = rates["min_given_start"]

        # Typisk spilletid gitt start MÅ blandes med årets faktiske minutter,
        # ikke hentes rått fra i fjor. En spiller som nettopp har gått fra
        # innhopper til å spille 90 hver kamp skal ikke bære fjorårets snitt.
        own_starts = hist[hist.starts == 1] if hist is not None else None
        if own_starts is not None and len(own_starts):
            obs_min = float(own_starts.minutes.mean())
            wm = len(own_starts) / (len(own_starts) + 2.0)
            personal_min = wm * obs_min + (1 - wm) * prior_min
        else:
            personal_min = prior_min

        if hist is None or hist.empty:
            n, p_raw, weight = 0, p_prior, 0.0
        else:
            age = latest_gw - hist.gw
            w = 0.5 ** (age / HALF_LIFE)
            weight = float(w.sum())
            p_raw = float((np.sum(w * (hist.starts == 1)) + k * p_prior) / (weight + k))
            n = int(len(hist))

        mult, reason = availability(el)
        p_start = p_raw * mult

        # Innbytterrolle: spilte, men startet ikke.
        if hist is not None and len(hist):
            # NB: w er bare definert i grenen over. Uten denne innrykkingen leste
            # koden w fra forrige spiller i løkka — en feil som ikke krasjer,
            # men gir gale tall for alle uten historikk.
            p_sub_given_no_start = float(
                np.sum(w * ((hist.starts == 0) & (hist.minutes > 0))) / max(weight, 1e-9)
            )
        else:
            p_sub_given_no_start = 0.0
        p_sub = (1 - p_raw) * p_sub_given_no_start * mult

        exp_min = p_start * personal_min + p_sub * rates["min_given_sub"]
        p60 = p_start * rates["p60_given_start"]

        rows.append({
            "element": pid,
            "web_name": el["web_name"],
            "team": teams[el["team"]],
            "pos": pos[el["element_type"]],
            "price": el["now_cost"] / 10,
            "n_matches": n,
            "p_start": round(p_start, 3),
            # p_play inkluderer innbytte. Uten denne mister xP-modellen ALLE
            # innbytterpoeng — målt til 108 poeng per runde på ligabasis, som
            # var den største enkeltfeilen i første versjon av xP.
            "p_play": round(p_start + p_sub, 3),
            "p_60": round(p60, 3),
            "exp_minutes": round(exp_min, 1),
            "avail_mult": mult,
            "flag": reason or ("" if mult == 1.0 else "se news"),
            "news": (el.get("news") or "")[:80],
        })

    return pd.DataFrame(rows).sort_values("p_start", ascending=False).reset_index(drop=True)


def main() -> None:
    pm, bs, _ = load()
    rates = league_rates(pm)
    print("Grunnrater estimert fra data:")
    print(f"  andel startende blant involverte : {rates['p_start_prior']:.3f}")
    print(f"  minutter gitt start              : {rates['min_given_start']:.1f}")
    print(f"  P(60+ | start)                   : {rates['p60_given_start']:.3f}")
    print(f"  minutter gitt innbytte           : {rates['min_given_sub']:.1f}")

    out = build(pm, bs, rates)
    DERIVED.mkdir(parents=True, exist_ok=True)
    out.to_csv(DERIVED / "minutes.csv", index=False)

    flagged = out[out.avail_mult < 1.0]
    print(f"\n{len(out)} spillere · {len(flagged)} med redusert tilgjengelighet")
    print("\n--- mest sikre startere ---")
    print(out.head(8)[["web_name", "team", "pos", "p_start", "exp_minutes"]].to_string(index=False))


if __name__ == "__main__":
    main()
