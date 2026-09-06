"""
Sesongsimulering — hvordan ville systemet gjort det i praksis?

Backtesten (M9) måler om prediksjonene er gode. Dette måler noe annet og
vanskeligere: om SYSTEMET gir poeng. Det krever å faktisk spille sesongen —
velge tropp innenfor budsjett, bytte uke for uke under transferreglene, sette
ellever og kaptein, og telle det spillerne virkelig scoret.

REGLENE SOM FØLGES

    £100,0m · 15 spillere (2/5/5/3) · maks 3 per klubb
    1 fri transfer per runde, banking opptil 5, −4 per ekstra
    gyldig formasjon hver runde, kaptein teller dobbelt
    automatiske innbytter når en spiller i ellevern ikke spiller

INGEN FRAMTIDSINFORMASJON

Beslutningen før runde t bruker kun runde 1 til t−1, pluss forrige sesong som
prior. Prisene som brukes er prisene den runden. Det er den samme
informasjonen systemet ville hatt på torsdagen.

CHIPS

Kjøres i to varianter: uten chips (nedre grense), og med enkle chip-regler.
Free Hit er ikke modellert.

Målt 6. sep 2026, etter at doble runder ble telt riktig: chips er verdt
+53,5 ± 4,5 poeng (11,9 se), to par. Det er en NEDRE grense — reglene her er
grove og Free Hit mangler. Den tidligere konklusjonen om at chip-timing var
verdt maks 28 poeng ble målt mens doble runder ble halvtelt, og er forkastet.

DET SIMULERINGEN IKKE FANGER

Pressekonferanser og lagnytt. I virkeligheten overstyrer Claudes ukentlige
nyhetssøk minuttmodellen — en spiller som er meldt skadet fredag settes til
null. Simuleringen har ingen slik overstyring, så den spiller med dårligere
informasjon enn systemet faktisk har. Resultatet er dermed konservativt.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pulp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest import (DC_THRESHOLD, GOAL_POINTS, CS_POINTS, HIST,
                      team_ratings, fit_dispersion, per90, predict, start_prior)

PRIOR_SEASON = ("https://raw.githubusercontent.com/vaastav/"
                "Fantasy-Premier-League/master/data/2024-25/gws/merged_gw.csv")

BUDGET = 100.0
SQUAD = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}
FORMATION = {"GK": (1, 1), "DEF": (3, 5), "MID": (2, 5), "FWD": (1, 3)}
HORIZON = 3
MAX_FT = 5
HIT = 4
CAND_PER_POS = 45      # hvor mange kandidater som vurderes ved bytte
# Hvor stor gevinst over horisonten som kreves før et bytte gjøres. Lav verdi
# gjør modellen ivrig: den bruker den frie transferen nesten hver uke i stedet
# for å spare den.
#
# MÅLT 5. sep 2026, seks parvise kjøringer over to sesonger, 0.5 mot 2.0:
#   2024-25   +11.3 ± 0.3   (34 se — alle tre parene peker samme vei)
#   2025-26   -11.0 ± 4.0   ( 2.7 se — alle tre parene peker motsatt vei)
#   samlet     +0.2 ± 5.3   (ingen effekt)
#
# Effekten er stor og entydig innenfor hver sesong, men bytter fortegn mellom
# dem. Med bare én sesong ville dette sett ut som et sikkert funn på 34
# standardfeil. Det er hele grunnen til at evalueringen kjører to sesonger.
# Verdien står derfor uendret: det finnes ingen verdi som er best på forhånd.
TRANSFER_MIN_GAIN = 0.5

# Hvor mange bytter simuleringen kan gjøre i én runde. Se sløyfen i run().
#
# Med 1 forsvinner oppsparte frie bytter ubrukt, og simuleringen gjør altså noe
# annet enn produksjonens optimizer, som planlegger flere bytter samtidig. Det
# taler for 2. MÅLINGEN GJØR DET IKKE:
#
#   ett bytte    snitt 2055, standardavvik 15   [2043 2043 2043 2054 2069 2078]
#   inntil to    snitt 2050, standardavvik 50   [1993 2028 2038 2049 2049 2142]
#
#   parvis differanse −5 ± 21 poeng, seks par over to sesonger
#
# Ingen gevinst i snitt, og spredningen mer enn tredobles. Det andre byttet er
# grådig — det tar det beste enkeltbyttet en gang til — og et grådig andrebytte
# er nettopp den kjente feilen «bruk transferen fordi du har den». Målet er
# høyest mulig poeng med lavest mulig sannsynlighet for et dårlig år, og da er
# en endring som er nøytral i snitt og verre i haledelen ikke verdt å ha.
#
# Koden for flere bytter står igjen, slik at spørsmålet kan tas opp igjen hvis
# søket en gang blir bedre enn grådig.
MAX_MOVES_PER_GW = 1

# Doble runder. En spiller med to kamper i samme runde har TO rader i dataene.
# Oppslaget som var her beholdt bare den siste og kastet den andre kampen.
#
# Feilen var stille og skjev på verst tenkelige måte: xP summerte begge kampene
# og valgte derfor riktig spiller, men fasiten ga uttelling for bare én av dem.
# Simuleringen ble altså straffet for å gjøre det riktige — og hardest nettopp
# i de rundene chips er til for.
#
# MÅLT 6. sep 2026, fem parvise kjøringer over tre sesonger:
#   2023-24 frø 11   1924 → 2053   (+129)
#   2024-25 frø 11   2018 → 2097   ( +79)
#   2024-25 frø 12   1984 → 2052   ( +68)
#   2025-26 frø 11   2040 → 2076   ( +36)
#   2025-26 frø 12   2033 → 2069   ( +36)
#   samlet +69,6 ± 17,1 (4,1 se) — alle fem samme vei
#
# Utslaget følger antall doble runder i sesongen, som det skal. Simuleringen har
# altså undervurdert systemet med rundt 70 poeng, og alle nivåtall målt før
# 6. sep er for lave. Parvise sammenligninger er derimot uberørt: begge sidene
# hadde feilen.
#
# Flagget står igjen bare for å kunne måle dette på nytt. Skru det aldri av i
# annet enn en måling.
COUNT_ALL_FIXTURES = True


def load_with_prices() -> pd.DataFrame:
    """
    Som backtest.load(), men beholder `value` — prisen slik den var den runden.

    Å bruke sluttprisen ville gitt framtidsinformasjon: en spiller som steg fra
    4.5 til 6.0 gjennom sesongen ville sett uoverkommelig dyr ut i runde 1, og
    en som falt ville sett gratis ut. Simuleringen må handle til datidens priser.
    """
    d = pd.read_csv(f"{HIST}/gws/merged_gw.csv")
    # `defensive_contribution` ble innført som poengkategori i 2025-26. For
    # tidligere sesonger settes den til null — som er riktig, ikke en lapp:
    # spillerne fikk faktisk ingen poeng for den da.
    if "defensive_contribution" not in d.columns:
        d["defensive_contribution"] = 0
    if "selected" not in d.columns:
        d["selected"] = 0
    keep = ["name", "position", "team", "GW", "fixture", "opponent_team", "was_home",
            "minutes", "starts", "total_points", "goals_scored", "assists",
            "clean_sheets", "goals_conceded", "saves", "bonus", "bps",
            "expected_goals", "expected_assists", "defensive_contribution",
            "yellow_cards", "red_cards", "value", "selected"]
    d = d[keep].copy()
    d["pos"] = d.position.map({"GKP": "GK", "GK": "GK", "DEF": "DEF", "MID": "MID",
                               "FWD": "FWD", "AM": "MID"}).fillna("MID")
    return d


def ownership_at(d: pd.DataFrame, gw: int) -> dict:
    """
    Andelen av alle managere som eide hver spiller den runden.

    `selected` er antall managere som eide spilleren. Antallet managere er ikke
    oppgitt, men hver av dem eier nøyaktig 15 spillere, så summen delt på 15 gir
    det. Den utregningen er selvkorrigerende: den følger sesongen når feltet
    vokser eller krymper, i stedet for å hvile på et tall jeg må slå opp.
    """
    g = d[d.GW == gw]
    managers = g.selected.sum() / 15.0
    if managers <= 0:
        return {}
    return (g.selected / managers).groupby(g.name).max().to_dict()


def prices_at(d: pd.DataFrame, gw: int) -> dict:
    """Prisen slik den var den runden, ikke slik den endte."""
    g = d[d.GW == gw]
    return (g.value / 10.0).groupby(g.name).max().to_dict()


def horizon_xp(d: pd.DataFrame, t: int, rates, att, dfn, ha, mu, disp) -> pd.Series:
    """Sum xP over de neste rundene, brukt til byttebeslutninger."""
    fut = d[(d.GW >= t) & (d.GW < t + HORIZON)]
    if fut.empty:
        return pd.Series(dtype=float)
    p = predict(fut, rates, att, dfn, ha, mu, disp)
    return p.groupby("name").xp.sum() if not p.empty else pd.Series(dtype=float)


def pick_squad(cand: pd.DataFrame, budget: float) -> list[str]:
    """Beste lovlige 15-mannstropp innenfor budsjett — ren knapsack."""
    m = pulp.LpProblem("initial", pulp.LpMaximize)
    v = {n: pulp.LpVariable(f"p{i}", cat="Binary") for i, n in enumerate(cand.name)}
    xp = dict(zip(cand.name, cand.xp))
    pr = dict(zip(cand.name, cand.price))
    po = dict(zip(cand.name, cand.pos))
    cl = dict(zip(cand.name, cand.team))
    m += pulp.lpSum(xp[n] * v[n] for n in v)
    m += pulp.lpSum(pr[n] * v[n] for n in v) <= budget
    for ps, k in SQUAD.items():
        m += pulp.lpSum(v[n] for n in v if po[n] == ps) == k
    for c in set(cl.values()):
        m += pulp.lpSum(v[n] for n in v if cl[n] == c) <= 3
    m.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=60))
    return [n for n in v if (v[n].value() or 0) > 0.5]


def best_xi(squad: list[str], xp: pd.Series, pos: dict) -> tuple[list[str], float]:
    """Beste lovlige ellever etter forventede poeng."""
    have = {p: sorted([n for n in squad if pos.get(n) == p],
                      key=lambda n: -xp.get(n, 0.0)) for p in SQUAD}
    best, pick = -1.0, []
    for nd in range(3, 6):
        for nm in range(2, 6):
            nf = 10 - nd - nm
            if not (1 <= nf <= 3):
                continue
            if len(have["DEF"]) < nd or len(have["MID"]) < nm or len(have["FWD"]) < nf or not have["GK"]:
                continue
            sel = have["GK"][:1] + have["DEF"][:nd] + have["MID"][:nm] + have["FWD"][:nf]
            tot = sum(xp.get(n, 0.0) for n in sel)
            if tot > best:
                best, pick = tot, sel
    return pick, best


def score_gw(xi: list[str], captain: str, squad: list[str], actual: dict,
             played: dict, pos: dict, mult: int = 2) -> float:
    """
    Poeng for runden, med automatiske innbytter.

    FPL bytter automatisk inn en benkespiller når noen i ellevern ikke spiller,
    så lenge formasjonen forblir lovlig. Uten dette undervurderes poengene
    systematisk — særlig i runder med mange skader.
    """
    bench = [n for n in squad if n not in xi]
    final = [n for n in xi if played.get(n, 0) > 0]
    out = [n for n in xi if played.get(n, 0) == 0]

    for miss in out:
        need_gk = pos.get(miss) == "GK"
        for b in bench:
            if played.get(b, 0) == 0:
                continue
            if need_gk != (pos.get(b) == "GK"):
                continue
            trial = final + [b]
            cnt = {p: sum(1 for n in trial if pos.get(n) == p) for p in SQUAD}
            lo_ok = all(cnt[p] >= FORMATION[p][0] for p in SQUAD)
            hi_ok = all(cnt[p] <= FORMATION[p][1] for p in SQUAD)
            if hi_ok and (len(trial) < 11 or lo_ok):
                final.append(b)
                bench.remove(b)
                break

    pts = sum(actual.get(n, 0) for n in final)
    if captain in final:
        pts += actual.get(captain, 0) * (mult - 1)
    elif played.get(captain, 0) == 0:
        # Visekaptein: nest høyest forventet i ellevern som faktisk spilte.
        vice = next((n for n in xi if n != captain and played.get(n, 0) > 0), None)
        if vice:
            pts += actual.get(vice, 0) * (mult - 1)
    return pts


def run(use_chips: bool) -> dict:
    d = load_with_prices()
    sides = d.groupby(["fixture", "team"], as_index=False).size()
    opp = sides.merge(sides, on="fixture")
    opp = opp[opp.team_x != opp.team_y][["fixture", "team_x", "team_y"]]
    opp = opp.rename(columns={"team_x": "team", "team_y": "_opp_name"}).drop_duplicates()
    d = d.merge(opp, on=["fixture", "team"], how="left")

    prior = pd.read_csv(PRIOR_SEASON)
    if "defensive_contribution" not in prior.columns:
        prior["defensive_contribution"] = 0
    prior["pos"] = prior.position.map({"GKP": "GK", "GK": "GK", "DEF": "DEF", "MID": "MID",
                                       "FWD": "FWD", "AM": "MID"}).fillna("MID")
    prior["_opp_name"] = None
    # Personlig startrate fra forrige sesong — den viktigste enkeltinngangen
    # til minuttmodellen.
    sp = start_prior(prior)
    # Lagratinger fra forrige sesong, som informativ prior — samme opplegg som
    # produksjonsmodellen bruker. Uten dette krymper simuleringen mot
    # "alle lag er like gode", noe produksjonen ikke gjør.
    _pa, _pd, _, _ = team_ratings(prior)
    team_prior = (_pa, _pd)

    pos_map = dict(zip(d.name, d.pos))
    team_map = dict(zip(d.name, d.team))

    squad, bank, ft = [], 0.0, 1
    total, log = 0, []
    chips_left = {"wc": 2, "bb": 2, "tc": 2} if use_chips else {}

    for t in sorted(d.GW.unique()):
        hist = d[d.GW < t]
        train = pd.concat([prior, hist], ignore_index=True) if len(hist) < 6 * 380 else hist
        att, dfn, ha, mu = team_ratings(train if not hist.empty else prior, team_prior)
        if not att:
            att, dfn, ha, mu = team_ratings(prior, team_prior)
        disp = fit_dispersion(train)
        rates = per90(train, sp)
        # En spiller som byttet posisjon mellom sesongene får to rader når
        # prior og inneværende slås sammen. Behold raden med mest spilletid,
        # ellers returnerer oppslaget en tabell i stedet for én spiller.
        rates = rates.sort_values("mins", ascending=False).drop_duplicates("name")

        this = d[d.GW == t]
        p_now = predict(this, rates, att, dfn, ha, mu, disp)
        xp_now = p_now.groupby("name").xp.sum() if not p_now.empty else pd.Series(dtype=float)
        xp_hor = horizon_xp(d, t, rates, att, dfn, ha, mu, disp)
        price = prices_at(d, t)
        # Doble runder: en spiller med to kamper i samme runde har TO rader.
        # `dict(zip(...))` beholdt bare den siste og kastet den andre kampen.
        # Feilen var stille og systematisk, og den rammet nettopp det chips er
        # til for: xP summerte begge kampene og valgte riktig spiller, men
        # fasiten ga bare uttelling for én av dem. Derfor så doble runder — og
        # dermed Bench Boost og Triple Captain — kunstig verdiløse ut.
        if COUNT_ALL_FIXTURES:
            actual = this.groupby("name").total_points.sum().to_dict()
            played = this.groupby("name").minutes.sum().to_dict()
        else:
            actual = dict(zip(this.name, this.total_points))
            played = dict(zip(this.name, this.minutes))

        avail = pd.DataFrame({"name": list(price)})
        avail["price"] = avail.name.map(price)
        avail["pos"] = avail.name.map(pos_map)
        avail["team"] = avail.name.map(team_map)
        avail["xp"] = avail.name.map(xp_hor).fillna(0.0)
        avail = avail.dropna(subset=["pos", "team"])

        chip = ""
        if not squad:
            squad = pick_squad(avail, BUDGET)
            bank = BUDGET - sum(price.get(n, 0) for n in squad)
        else:
            # Bytter, ett om gangen, helt til neste bytte ikke lenger lønner seg.
            #
            # Tidligere kunne simuleringen bare gjøre ETT bytte i runden. Da ble
            # oppsparte frie bytter aldri brukt — de bare forsvant — og
            # simuleringen målte en annen strategi enn den optimeringen faktisk
            # kjører i produksjon, der flere bytter planlegges samtidig.
            #
            # Søket er grådig: beste enkeltbytte, så beste bytte fra det nye
            # laget. Det finner ikke alltid det optimale paret, men det er 2-3
            # forsøk i stedet for et par hundre tusen, og det er langt nærmere
            # produksjonen enn å nekte det andre byttet.
            #
            # Terskelen tar seg av stoppen av seg selv: når det frie byttet er
            # brukt opp, må neste bytte tjene inn HIT i tillegg, og det gjør de
            # færreste.
            pool_all = pd.concat([avail[avail.pos == p].nlargest(CAND_PER_POS, "xp")
                                  for p in SQUAD])
            for _ in range(MAX_MOVES_PER_GW):
                cur_xi, cur_val = best_xi(squad, xp_hor, pos_map)
                pool = pool_all[~pool_all.name.isin(squad)]
                best_gain, best_move = 0.0, None
                for out_n in squad:
                    budget = bank + price.get(out_n, 0)
                    for _, inn in pool[(pool.pos == pos_map.get(out_n)) &
                                       (pool.price <= budget)].iterrows():
                        trial = [n for n in squad if n != out_n] + [inn["name"]]
                        if sum(1 for n in trial if team_map.get(n) == inn.team) > 3:
                            continue
                        _, val = best_xi(trial, xp_hor, pos_map)
                        if val - cur_val > best_gain:
                            best_gain, best_move = val - cur_val, (out_n, inn["name"], inn.price)
                threshold = 0.0 if ft >= 1 else HIT
                if not (best_move and best_gain > threshold + TRANSFER_MIN_GAIN):
                    break
                out_n, in_n, in_p = best_move
                squad = [n for n in squad if n != out_n] + [in_n]
                bank += price.get(out_n, 0) - in_p
                if ft >= 1:
                    ft -= 1
                else:
                    total -= HIT
            ft = min(ft + 1, MAX_FT)

        xi, _ = best_xi(squad, xp_now, pos_map)
        captain = max(xi, key=lambda n: xp_now.get(n, 0.0)) if xi else None
        mult = 2
        if use_chips and chips_left.get("tc", 0) and xp_now.get(captain, 0) > 8.0:
            mult, chips_left["tc"], chip = 3, chips_left["tc"] - 1, "TC"

        pts = score_gw(xi, captain, squad, actual, played, pos_map, mult)
        if use_chips and chips_left.get("bb", 0) and not chip:
            benchpts = sum(actual.get(n, 0) for n in squad if n not in xi)
            if benchpts >= 12:
                pts += benchpts
                chips_left["bb"], chip = chips_left["bb"] - 1, "BB"
        total += pts
        # Diagnostikk: hvor poengene ble av, slik at gapene kan måles i stedet
        # for gjettes. Lagres per runde og brukes av gap-analysen.
        bench = [n for n in squad if n not in xi]
        xi_blank = [n for n in xi if played.get(n, 0) == 0]
        bench_played = [n for n in bench if played.get(n, 0) > 0]
        best_cap = max(xi, key=lambda n: actual.get(n, 0)) if xi else None
        # Eierskap. Rank avgjøres av differansen mot feltet, ikke av poeng
        # alene: en runde der alle får 80 og du får 80 flytter deg ingen steder.
        # Dette er ikke koblet til noen beslutning ennå — det er målingen som må
        # komme først, slik at størrelsen på gevinsten er kjent før noe bygges.
        own = ownership_at(d, t)
        xi_own = sum(own.get(n, 0.0) for n in xi) / max(1, len(xi))
        # Dekomponering med fasit i hånd: hva den samme troppen KUNNE gitt med
        # perfekt laguttak og perfekt kaptein. Differansen mot det vi faktisk
        # fikk er tapet i utvelgelse; resten av gapet til elitenivå ligger da i
        # selve troppen. Uten dette skillet er det umulig å vite om neste
        # innsats bør gå til prediksjon eller til laguttak.
        act = pd.Series(actual, dtype=float)
        hind_xi, hind_pts = best_xi(squad, act, pos_map)
        hind_cap = max((actual.get(n, 0) for n in hind_xi), default=0)
        xi_only = score_gw(xi, captain, squad, actual, played, pos_map, mult=1)

        # Laguttaket målt mot enklere regler, på samme måte som kapteinen.
        # Autobytter regnes med, ellers straffes reglene ulikt for blanke.
        alt_xi = {}
        if not hist.empty:
            f3 = hist[hist.GW >= t - 3].groupby("name").total_points.mean()
            sn = hist.groupby("name").total_points.mean()
            for lab, key in (("form", f3), ("snitt", sn)):
                sel, _ = best_xi(squad, key.reindex(squad).fillna(0.0), pos_map)
                alt_xi[lab] = score_gw(sel, captain, squad, actual, played,
                                       pos_map, mult=1)

        # Kapteinsvalget målt mot enklere regler. Modellen velger høyest xP,
        # og det er optimalt under modellens eget syn — men bare hvis modellen
        # ser bedre enn form gjør. Det er ikke gitt, og det er billig å måle.
        # Alle reglene bruker kun det som var kjent før runden.
        alt_caps = {"xp": captain}
        if xi:
            form3 = (hist[hist.GW >= t - 3].groupby("name").total_points.mean()
                     if not hist.empty else pd.Series(dtype=float))
            snitt = (hist.groupby("name").total_points.mean()
                     if not hist.empty else pd.Series(dtype=float))
            alt_caps["form"] = max(xi, key=lambda n: form3.get(n, 0.0))
            alt_caps["snitt"] = max(xi, key=lambda n: snitt.get(n, 0.0))
            alt_caps["eid"] = max(xi, key=lambda n: own.get(n, 0.0))
            # Mellomting: hold på xP-valget, men bytt til en mer eid spiller
            # når forskjellen i xP er liten. Poenget er ikke poeng — det er at
            # kapteinen er den enkeltbeslutningen som svinger rank mest, og en
            # nesten like god kaptein som halve feltet også har, koster lite og
            # demper svingningen kraftig.
            top = xp_now.get(captain, 0.0)
            for delta in (0.5, 1.0, 2.0):
                nær = [n for n in xi if top - xp_now.get(n, 0.0) <= delta]
                alt_caps[f"hybrid{delta}"] = max(
                    nær, key=lambda n: (own.get(n, 0.0), xp_now.get(n, 0.0)))
        log.append({"gw": int(t), "pts": pts, "total": total, "chip": chip,
                    "xi_own": round(xi_own, 4),
                    "cap_own": round(own.get(captain, 0.0), 4) if captain else 0.0,
                    # Poengsummen til en tropp trukket etter eierskap — et mål
                    # på hvordan malen gjorde det den runden.
                    "own_pts": round(sum(own.get(n, 0.0) * p
                                         for n, p in actual.items()), 2),
                    "xi_only": xi_only,            # vårt ellever, uten kaptein
                    "hind_xi": hind_pts,           # beste ellever med fasit
                    "hind_cap": hind_cap,          # beste kaptein i det laget
                    **{f"cap_{k}": actual.get(v, 0) for k, v in alt_caps.items()},
                    **{f"capown_{k}": round(own.get(v, 0.0), 4)
                       for k, v in alt_caps.items()},
                    **{f"xi_{k}": v for k, v in alt_xi.items()},
                    "captain": captain, "bank": round(bank, 1),
                    "cap_pts": actual.get(captain, 0) if captain else 0,
                    "best_cap_pts": actual.get(best_cap, 0) if best_cap else 0,
                    "n_xi_blank": len(xi_blank),
                    "n_bench_rescue": min(len(xi_blank), len(bench_played)),
                    "bench_pts": sum(actual.get(n, 0) for n in bench),
                    "xi_played_avg": (sum(actual.get(n,0) for n in xi if played.get(n,0)>0)
                                      / max(1, len(xi)-len(xi_blank)))})

    return {"total": total, "log": pd.DataFrame(log)}


def main() -> None:
    print("Simulerer 2025-26 fra runde 1, uten framtidsinformasjon.\n")
    base = run(use_chips=False)
    print(f"UTEN CHIPS : {base['total']} poeng")
    withc = run(use_chips=True)
    print(f"MED CHIPS  : {withc['total']} poeng")

    lg = withc["log"]
    print(f"\nSnitt per runde: {lg.pts.mean():.1f} | beste {lg.pts.max()} (GW{lg.loc[lg.pts.idxmax(),'gw']})"
          f" | svakeste {lg.pts.min()} (GW{lg.loc[lg.pts.min() == lg.pts,'gw'].iloc[0]})")
    print(f"Chips brukt: {', '.join(f'{r.chip} GW{r.gw}' for _, r in lg[lg.chip != ''].iterrows()) or 'ingen'}")
    lg.to_csv(Path(__file__).resolve().parents[1] / "data" / "derived" / "season_sim.csv", index=False)


if __name__ == "__main__":
    main()
