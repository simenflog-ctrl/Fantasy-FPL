"""
M8 — beslutningsoptimizer.

De foregående modellene svarer på "hvor mange poeng er denne spilleren verdt".
Denne svarer på det som faktisk skal gjøres: hvilke bytter, i hvilken rekkefølge,
med hvilket lag hver runde, hvem som er kaptein, og når chipsene skal brukes.

HVORFOR DET KREVER EN SOLVER

Å bytte den spilleren med lavest xP mot den beste man har råd til, er ikke
optimalt. Beslutningene henger sammen: budsjettet frigjort i én runde bestemmer
hva som er mulig i neste, tre-per-klubb-grensen binder på tvers av runder, og
et hit på −4 kan lønne seg hvis det åpner en oppgradering to runder fram.

Dette er et heltallsprogram over hele horisonten. Løseren ser sekvenser et
menneske ikke regner ut for hånd.

    maksimer  Σ (xP for ellevern + xP for kaptein + vekt · xP for benk) − 4·hits

under bibetingelsene: 15 spillere fordelt 2/5/5/3, gyldig formasjon hver runde,
maks 3 per klubb, budsjett, og FPLs transferregler.

BENKEVEKTEN

Ren ellever-optimering ville fylt benken med de billigste spillerne i spillet,
siden benkepoeng ikke teller. Det er feil av to grunner: benken fanger opp
spillere som ikke starter, og Bench Boost krever en benk som faktisk spiller.
Benken teller derfor med en lav vekt.

HVA DEN IKKE MODELLERER ENNÅ

Free Hit. Chipen bytter laget for én runde og tilbakestiller det etterpå, noe
som krever et parallelt troppspor gjennom hele horisonten. Wildcard og Bench
Boost er med. Prisendringer er heller ikke modellert — salgspris antas lik
kjøpspris, som stemmer så lenge spilleren ikke har steget.

BRUK RESULTATET MED SKJØNN

Optimizeren maksimerer forventede poeng. Den vet ingenting om eierskap, og
dermed ingenting om rank. Å selge en spiller 71 % av feltet eier er et aktivt
veddemål mot sju av ti managere — det kan være riktig, men det er en annen
beslutning enn den løseren har regnet på.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pulp

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"

HORIZON = 5              # antall runder framover
# Liten straff per bytte. Uten den bytter løseren spillere fram og tilbake
# mellom runder når det er gratis — matematisk likegyldig, men urealistisk:
# i praksis koster hvert bytte salgsgebyr, prisrisiko og en låst beslutning.
TRANSFER_FRICTION = 0.05
POOL_PER_POS = 26        # kandidater per posisjon, i tillegg til egen tropp
BENCH_WEIGHT = 0.15      # hvor mye en benkeplass er verdt mot en ellever-plass
HIT_COST = 4
MAX_BANKED_FT = 5
SOLVER_SECONDS = 90

FORMATION = {"GK": (1, 1), "DEF": (3, 5), "MID": (2, 5), "FWD": (1, 3)}
SQUAD_SIZE = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}


def load_state():
    bs = json.loads((RAW / "bootstrap.json").read_text())
    entry = json.loads((RAW / "entry.json").read_text())
    cur = next((e for e in bs["events"] if e["is_current"]), None)
    gw = cur["id"] if cur else 1
    picks_file = RAW / f"picks_gw{gw}.json"
    picks = json.loads(picks_file.read_text()) if picks_file.exists() else None
    squad = [p["element"] for p in picks["picks"]] if picks else []
    bank = entry["last_deadline_bank"] / 10.0
    chips_used = {c["name"] for c in json.loads((RAW / "entry_history.json").read_text())["chips"]}
    return squad, bank, chips_used, gw


def build_pool(xp: pd.DataFrame, squad: list[int], first_gw: int):
    """
    Horisonten må starte på NESTE runde, ikke inneværende.

    Inneværende runde er allerede låst — deadline har passert og laget kan ikke
    endres. Tar man den med, planlegger løseren bytter som er umulige, og i
    første kjøring foreslo den Wildcard i en runde som allerede var i gang.
    """
    xp = xp[xp.gw >= first_gw]
    horizon_gws = sorted(xp.gw.unique())[:HORIZON]
    h = xp[xp.gw.isin(horizon_gws)]
    tot = h.groupby(["element", "web_name", "team", "pos", "price"], as_index=False).xp.sum()

    keep = set(squad)
    for pos in SQUAD_SIZE:
        keep |= set(tot[tot.pos == pos].nlargest(POOL_PER_POS, "xp").element)
    pool = tot[tot.element.isin(keep)].reset_index(drop=True)

    grid = h[h.element.isin(keep)].pivot_table(index="element", columns="gw", values="xp", aggfunc="sum")
    grid = grid.reindex(pool.element).fillna(0.0)
    return pool, grid, horizon_gws


def solve(pool: pd.DataFrame, grid: pd.DataFrame, gws: list[int],
          squad: list[int], bank: float, chips_available: set[str]):
    P = pool.element.tolist()
    price = dict(zip(pool.element, pool.price))
    pos = dict(zip(pool.element, pool.pos))
    club = dict(zip(pool.element, pool.team))
    xp = {(p, t): float(grid.loc[p, t]) for p in P for t in gws}

    missing = [p for p in squad if p not in price]
    if missing:
        # En spiller i troppen kan mangle xP (f.eks. nettopp solgt ut av ligaen).
        # Da blir troppen feil gjengitt, og vi sier fra i stedet for å regne videre.
        print(f"  ADVARSEL: {len(missing)} spillere i troppen mangler i kandidatlista")

    m = pulp.LpProblem("fpl", pulp.LpMaximize)
    x = pulp.LpVariable.dicts("squad", (P, gws), cat="Binary")     # i troppen
    y = pulp.LpVariable.dicts("xi", (P, gws), cat="Binary")        # i ellevern
    c = pulp.LpVariable.dicts("cap", (P, gws), cat="Binary")       # kaptein
    buy = pulp.LpVariable.dicts("buy", (P, gws), cat="Binary")
    sell = pulp.LpVariable.dicts("sell", (P, gws), cat="Binary")
    hits = pulp.LpVariable.dicts("hits", gws, lowBound=0, cat="Integer")
    ft = pulp.LpVariable.dicts("ft", gws, lowBound=0, upBound=MAX_BANKED_FT, cat="Integer")
    bankv = pulp.LpVariable.dicts("bank", gws, lowBound=0)

    wc = {t: pulp.LpVariable(f"wc_{t}", cat="Binary") for t in gws} if "wildcard" in chips_available else {}
    bb = {t: pulp.LpVariable(f"bb_{t}", cat="Binary") for t in gws} if "bboost" in chips_available else {}
    # Benkepoeng som teller fullt når Bench Boost er aktiv. Produktet av to
    # binærvariabler linjæriseres på standard vis.
    z = pulp.LpVariable.dicts("bboost_bench", (P, gws), cat="Binary") if bb else None

    objective = []
    for t in gws:
        for p in P:
            objective += [xp[p, t] * y[p][t], xp[p, t] * c[p][t],
                          BENCH_WEIGHT * xp[p, t] * (x[p][t] - y[p][t])]
            if z is not None:
                objective.append((1 - BENCH_WEIGHT) * xp[p, t] * z[p][t])
        objective.append(-HIT_COST * hits[t])
        objective.append(-TRANSFER_FRICTION * pulp.lpSum(buy[p][t] for p in P))
    m += pulp.lpSum(objective)

    prev = {p: (1 if p in squad else 0) for p in P}
    for i, t in enumerate(gws):
        m += pulp.lpSum(x[p][t] for p in P) == 15
        for ps, n in SQUAD_SIZE.items():
            m += pulp.lpSum(x[p][t] for p in P if pos[p] == ps) == n
        m += pulp.lpSum(y[p][t] for p in P) == 11
        for ps, (lo, hi) in FORMATION.items():
            sel = [y[p][t] for p in P if pos[p] == ps]
            m += pulp.lpSum(sel) >= lo
            m += pulp.lpSum(sel) <= hi
        for cl in set(club.values()):
            m += pulp.lpSum(x[p][t] for p in P if club[p] == cl) <= 3
        m += pulp.lpSum(c[p][t] for p in P) == 1
        for p in P:
            m += y[p][t] <= x[p][t]
            m += c[p][t] <= y[p][t]
            if z is not None:
                m += z[p][t] <= x[p][t] - y[p][t]
                m += z[p][t] <= bb[t]

        # Troppen endrer seg bare gjennom kjøp og salg.
        for p in P:
            m += x[p][t] == (prev[p] if i == 0 else x[p][gws[i - 1]]) + buy[p][t] - sell[p][t]
            m += buy[p][t] + sell[p][t] <= 1
        n_transfers = pulp.lpSum(buy[p][t] for p in P)
        m += n_transfers == pulp.lpSum(sell[p][t] for p in P)

        # Transferbudsjett. Wildcard opphever begrensningen i sin runde.
        free_now = ft[t] + hits[t] + (15 * wc[t] if wc else 0)
        m += n_transfers <= free_now

        # Penger. Salgspris antas lik kjøpspris. Budsjettet håndheves ved at
        # banken aldri kan bli negativ.
        spend = pulp.lpSum(price[p] * buy[p][t] for p in P)
        income = pulp.lpSum(price[p] * sell[p][t] for p in P)
        m += bankv[t] == (bank if i == 0 else bankv[gws[i - 1]]) + income - spend

        # Frie transfers: én ny per runde, tak på 5. Ulikhet er trygt fordi
        # flere frie transfers aldri er en ulempe — løseren presser den opp av
        # seg selv, men kan ikke overskride det reglene tillater.
        if i == 0:
            m += ft[t] == 1
        else:
            prev_t = gws[i - 1]
            m += ft[t] <= ft[prev_t] - pulp.lpSum(buy[p][prev_t] for p in P) \
                 + hits[prev_t] + (15 * wc[prev_t] if wc else 0) + 1
            # Etter Wildcard får man ÉN fri transfer neste runde, ikke fem.
            # Uten denne linjen krediterer regnestykket over wildcardets bytter
            # som opptjente frie transfers, og løseren fikk et helt gratis
            # byttebudsjett i rundene etter.
            if wc:
                m += ft[t] <= 1 + MAX_BANKED_FT * (1 - wc[prev_t])

    if wc:
        m += pulp.lpSum(wc.values()) <= 1
    if bb:
        m += pulp.lpSum(bb.values()) <= 1
    # FPL tillater bare ÉN chip per runde. Uten denne la løseren Wildcard og
    # Bench Boost i samme uke — en plan som ikke kan gjennomføres.
    for t in gws:
        terms = [v[t] for v in (wc, bb) if v]
        if len(terms) > 1:
            m += pulp.lpSum(terms) <= 1

    status = m.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=SOLVER_SECONDS))
    return m, dict(x=x, y=y, c=c, buy=buy, sell=sell, hits=hits, wc=wc, bb=bb), pulp.LpStatus[status]


def report(pool, gws, v, status):
    name = dict(zip(pool.element, pool.web_name))
    price = dict(zip(pool.element, pool.price))
    pos = dict(zip(pool.element, pool.pos))
    val = lambda var: int(round(var.value() or 0))

    print(f"\nLøserstatus: {status}")
    plan = []
    for t in gws:
        ins = [p for p in pool.element if val(v["buy"][p][t])]
        outs = [p for p in pool.element if val(v["sell"][p][t])]
        xi = [p for p in pool.element if val(v["y"][p][t])]
        cap = next((p for p in pool.element if val(v["c"][p][t])), None)
        h = val(v["hits"][t])
        chip = ("WILDCARD" if v["wc"] and val(v["wc"][t]) else
                "BENCH BOOST" if v["bb"] and val(v["bb"][t]) else "")
        print(f"\n── GW{t} {chip}")
        if ins:
            print("   inn : " + ", ".join(f"{name[p]} ({price[p]})" for p in ins))
            print("   ut  : " + ", ".join(f"{name[p]} ({price[p]})" for p in outs))
        else:
            print("   ingen bytter")
        if h:
            print(f"   hit : -{h * HIT_COST} poeng")
        print(f"   kaptein: {name[cap] if cap else '?'}")
        order = {"GK": 0, "DEF": 1, "MID": 2, "FWD": 3}
        xi_sorted = sorted(xi, key=lambda p: (order[pos[p]], -price[p]))
        print("   lag: " + ", ".join(name[p] for p in xi_sorted))
        plan.append({"gw": int(t), "chip": chip, "in": [name[p] for p in ins],
                     "out": [name[p] for p in outs], "hits": h,
                     "captain": name[cap] if cap else None,
                     "xi": [name[p] for p in xi_sorted]})
    return plan


def main() -> None:
    xp = pd.read_csv(DERIVED / "expected_points.csv")
    squad, bank, chips_used, gw = load_state()
    if not squad:
        print("Fant ingen tropp — hopper over optimering.")
        return

    available = {"wildcard", "bboost"} - chips_used
    print(f"Utgangspunkt: GW{gw} · bank £{bank:.1f}m · chips tilgjengelig: "
          f"{', '.join(sorted(available)) or 'ingen'}")

    bs = json.loads((RAW / "bootstrap.json").read_text())
    nxt = next((e for e in bs["events"] if e["is_next"]), None)
    first_gw = nxt["id"] if nxt else gw + 1
    pool, grid, gws = build_pool(xp, squad, first_gw)
    print(f"  kandidater: {len(pool)} spillere · horisont GW{gws[0]}-{gws[-1]}")
    m, v, status = solve(pool, grid, gws, squad, bank, available)
    plan = report(pool, gws, v, status)

    (DERIVED / "plan.json").write_text(json.dumps(
        {"generated_for_gw": int(gws[0]), "status": status,
         "objective": round(pulp.value(m.objective), 2), "plan": plan},
        ensure_ascii=False, indent=1))
    print(f"\n✓ målfunksjon: {pulp.value(m.objective):.1f} forventede poeng over {len(gws)} runder")


if __name__ == "__main__":
    main()
