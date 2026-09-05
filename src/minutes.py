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

# Styrken på krympingen, i "antall kamper prioren er verdt". Uten den får en
# spiller med 2/2 starter p_start = 1.0, som er en påstand data ikke bærer.
#
# Denne er bevisst lav. Spilletid er mye mer vedvarende fra kamp til kamp enn
# xG er: en spiller som har startet alt starter nesten alltid igjen. Satt for
# høyt (2.0 ble prøvd først) kollapser modellen — da fikk hver eneste startende
# spiller identisk p_start, og Konsa fikk 0.37 til tross for null starter.
PRIOR_MATCHES = 0.7

# Status-koder i FPL-API-et som betyr at spilleren ikke er tilgjengelig.
UNAVAILABLE = {"i", "s", "u", "n"}


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
    rows = []

    by_player = {pid: g.sort_values("gw") for pid, g in pm.groupby("element")}

    for el in bs["elements"]:
        pid = el["id"]
        hist = by_player.get(pid)

        if hist is None or hist.empty:
            n, p_raw, weight = 0, rates["p_start_prior"], 0.0
        else:
            age = latest_gw - hist.gw
            w = 0.5 ** (age / HALF_LIFE)
            weight = float(w.sum())
            # Beta-krymping mot ligagrunnraten.
            p_raw = float(
                (np.sum(w * (hist.starts == 1)) + PRIOR_MATCHES * rates["p_start_prior"])
                / (weight + PRIOR_MATCHES)
            )
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

        exp_min = p_start * rates["min_given_start"] + p_sub * rates["min_given_sub"]
        p60 = p_start * rates["p60_given_start"]

        rows.append({
            "element": pid,
            "web_name": el["web_name"],
            "team": teams[el["team"]],
            "pos": pos[el["element_type"]],
            "price": el["now_cost"] / 10,
            "n_matches": n,
            "p_start": round(p_start, 3),
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
