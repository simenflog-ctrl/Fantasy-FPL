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
Boost er med. Framtidige prisendringer er ikke modellert: spillere i dagens
tropp selges til faktisk salgspris (kjøpspris + halve økningen), alle andre
kjøpes og selges til dagens pris.

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

# Antall runder framover. Settes høyere enn xP-filen dekker, slik at alle
# rundene expected_points.py leverer blir brukt (i gw08 dekket den seks, men
# optimizeren så bare fem).
HORIZON = 8
# Liten straff per bytte. Uten den bytter løseren spillere fram og tilbake
# mellom runder når det er gratis — matematisk likegyldig, men urealistisk:
# i praksis koster hvert bytte salgsgebyr, prisrisiko og en låst beslutning.
TRANSFER_FRICTION = 0.05
POOL_PER_POS = 26        # kandidater per posisjon, i tillegg til egen tropp
BENCH_WEIGHT = 0.15      # hvor mye en benkeplass er verdt mot en ellever-plass
HIT_COST = 4
# Ekstra terskel for å ta et hit, utover de fire poengene FPL trekker.
#
# Et hit er en sikker kostnad mot en usikker gevinst. Modellen har rundt 4 %
# skjevhet på totalnivå og betydelig større usikkerhet per spiller, så en plan
# som "tjener" noen få poeng på et hit ligger innenfor støyen.
#
# Konkret tilfelle: optimizeren ville tatt −12 i GW4 for en plan verdt 331,0
# mot 329,0 uten. Tolv poeng for to. Med denne marginen kreves det at hitet
# tjener inn 8 poeng per ekstra bytte før det velges — da faller slike planer
# bort av seg selv, uten at hits forbys.
HIT_UNCERTAINTY_MARGIN = 4
MAX_BANKED_FT = 5
# Fra 2024/25 beholdes lagrede frie transfers når Wildcard eller Free Hit
# brukes, men chiprunden gir ingen ny. Før 2024/25 ble de nullstilt til én.
# Kilde: Premier Leagues regelendring 2024/25; ikke eksplisitt bekreftet for
# 2026/27 i API-et. Sett til False for den gamle regelen.
CHIP_PRESERVES_FT = True
SOLVER_SECONDS = 90

# Chips låses opp først når modellen har nok data til å velge klokt.
#
# Wildcard, Bench Boost og Free Hit er engangsressurser: de kan brukes én gang,
# og et dårlig tidspunkt kan ikke angres. Tidlig i sesongen er modellens egne
# innsatsfaktorer for tynne til å bære en slik beslutning — minuttmodellen kan
# ikke skille faste startere fra hverandre før den har flere runder, og
# lagratingene hviler tungt på fjorårets prior.
#
# Optimizeren ville brukt Wildcard i GW4 etter to spilte runder. Det var
# matematisk riktig gitt tallene, men tallene var ikke gode nok ennå: den ville
# låst femten valg på et grunnlag som forbedrer seg raskt de neste ukene.
#
# Regelen er derfor generell, ikke et unntak for én uke: ingen chips før
# modellen har sett nok. Sett til 0 for å slå av sperren.
MIN_FINISHED_GW_FOR_CHIPS = 6

FORMATION = {"GK": (1, 1), "DEF": (3, 5), "MID": (2, 5), "FWD": (1, 3)}
SQUAD_SIZE = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}


def purchase_prices(bootstrap: dict, transfers: list[dict] | None, squad: list[int]) -> dict[int, float]:
    """
    Kjøpsprisen for hver spiller i troppen, i millioner.

    Spillere kjøpt etter sesongstart står i transfers.json; siste kjøp gjelder.
    Resten ble valgt før første frist, da prisene ennå var startprisene:
    now_cost − cost_change_start. Kontrollert mot rekonstruksjon fra
    element-summary for laget i gw08 (alle 15 like).
    """
    el = {e["id"]: e for e in bootstrap["elements"]}
    bought = {}
    for t in sorted(transfers or [], key=lambda t: t["time"]):
        bought[t["element_in"]] = t["element_in_cost"]
    return {p: (bought[p] if p in bought else el[p]["now_cost"] - el[p]["cost_change_start"]) / 10.0
            for p in squad}


def selling_price(bought: float, now: float) -> float:
    """FPL beholder halve prisøkningen, rundet ned til 0,1. Fall tas fullt."""
    b, n = round(bought * 10), round(now * 10)
    return (n if n <= b else b + (n - b) // 2) / 10.0


def free_transfers(history: dict, next_gw: int) -> int:
    """
    Frie transfers til neste runde, regnet fra lagets historikk.

    Én ny etter hver runde fra og med runde 1, tak på MAX_BANKED_FT. Brukte
    transfers trekkes fra (aldri under null; resten ble betalt med hits).
    I en runde med Wildcard eller Free Hit brukes ingen, og ingen ny opptjenes
    (CHIP_PRESERVES_FT). Ekstraordinære påfyll, som AFCON-runden i 2025/26,
    er ikke med.
    """
    chip_gws = {c["event"] for c in history.get("chips", []) if c["name"] in ("wildcard", "freehit")}
    ft = 0
    for r in sorted(history["current"], key=lambda r: r["event"]):
        if r["event"] >= next_gw:
            break
        if r["event"] == 1:
            ft = 1                       # førsterundens tropp er gratis
            continue
        if r["event"] in chip_gws:
            ft = ft if CHIP_PRESERVES_FT else 1
            continue
        ft = min(MAX_BANKED_FT, max(0, ft - r["event_transfers"]) + 1)
    return ft


def chip_windows(bootstrap: dict, history: dict) -> dict[str, list[tuple[int, int]]]:
    """
    Ubrukte chipvinduer per chip, som (første, siste runde).

    Fra 2025/26 har hver halvdel sitt eget sett (bootstrap['chips'] har
    start_event/stop_event per vindu). Et vindu er brukt når chipen er spilt i
    en runde innenfor det. Før sto det `{"wildcard", "bboost"} - chips_used`:
    da forsvant andre halvdels wildcard så snart den første var brukt, og
    optimizeren visste ikke at første halvdels chips utløper etter runde 19.
    """
    used = [(c["name"], c["event"]) for c in history.get("chips", [])]
    out: dict[str, list[tuple[int, int]]] = {}
    for ch in bootstrap.get("chips", []):
        lo, hi = int(ch["start_event"]), int(ch["stop_event"])
        if any(n == ch["name"] and lo <= e <= hi for n, e in used):
            continue
        out.setdefault(ch["name"], []).append((lo, hi))
    return out


def load_state():
    bs = json.loads((RAW / "bootstrap.json").read_text())
    entry = json.loads((RAW / "entry.json").read_text())
    history = json.loads((RAW / "entry_history.json").read_text())
    cur = next((e for e in bs["events"] if e["is_current"]), None)
    gw = cur["id"] if cur else 1
    picks_file = RAW / f"picks_gw{gw}.json"
    picks = json.loads(picks_file.read_text()) if picks_file.exists() else None
    squad = [p["element"] for p in picks["picks"]] if picks else []
    bank = entry["last_deadline_bank"] / 10.0
    chips_used = {c["name"] for c in history["chips"]}

    transfers_file = RAW / "transfers.json"
    if not transfers_file.exists():
        print("  ADVARSEL: transfers.json mangler — kjøpspris antas lik startpris for alle")
    transfers = json.loads(transfers_file.read_text()) if transfers_file.exists() else None
    now = {e["id"]: e["now_cost"] / 10.0 for e in bs["elements"]}
    bought = purchase_prices(bs, transfers, squad)
    sell = {p: selling_price(bought[p], now[p]) for p in squad}
    ft = free_transfers(history, gw + 1)
    return squad, bank, chips_used, gw, sell, ft


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
          squad: list[int], bank: float, chips_available: set[str],
          sell_price: dict[int, float] | None = None, ft_start: int = 1):
    P = pool.element.tolist()
    price = dict(zip(pool.element, pool.price))
    # Det laget eier i dag selges til salgspris; alt annet til dagens pris.
    sellp = {p: (sell_price or {}).get(p, price[p]) for p in P}
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

    # chips_available: {chip: [(første, siste runde), ...]} for ubrukte vinduer.
    # Et sett med navn (eldre kallere) tolkes som tilgjengelig i hele horisonten.
    if not isinstance(chips_available, dict):
        chips_available = {c: [(min(gws), max(gws))] for c in chips_available}
    windows = {c: [(lo, hi) for lo, hi in w if any(lo <= t <= hi for t in gws)]
               for c, w in chips_available.items()}
    in_window = lambda c, t: any(lo <= t <= hi for lo, hi in windows.get(c, []))  # noqa: E731
    wc = {t: pulp.LpVariable(f"wc_{t}", cat="Binary") for t in gws if in_window("wildcard", t)}
    bb = {t: pulp.LpVariable(f"bb_{t}", cat="Binary") for t in gws if in_window("bboost", t)}
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
        objective.append(-(HIT_COST + HIT_UNCERTAINTY_MARGIN) * hits[t])
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
                m += z[p][t] <= bb.get(t, 0)

        # Troppen endrer seg bare gjennom kjøp og salg.
        for p in P:
            m += x[p][t] == (prev[p] if i == 0 else x[p][gws[i - 1]]) + buy[p][t] - sell[p][t]
            m += buy[p][t] + sell[p][t] <= 1
        n_transfers = pulp.lpSum(buy[p][t] for p in P)
        m += n_transfers == pulp.lpSum(sell[p][t] for p in P)

        # Transferbudsjett. Wildcard opphever begrensningen i sin runde.
        free_now = ft[t] + hits[t] + 15 * wc.get(t, 0)
        m += n_transfers <= free_now

        # Penger. Budsjettet håndheves ved at banken aldri kan bli negativ.
        # Salgsprisen for dagens tropp er lavere enn nåprisen når en spiller
        # har steget; i gw08 manglet planen 0,9 m fordi dette ble ignorert.
        # (Gjenkjøp av en solgt spiller og salg igjen innen horisonten gis
        # salgspris — en liten, konservativ forenkling.)
        spend = pulp.lpSum(price[p] * buy[p][t] for p in P)
        income = pulp.lpSum(sellp[p] * sell[p][t] for p in P)
        m += bankv[t] == (bank if i == 0 else bankv[gws[i - 1]]) + income - spend

        # Frie transfers: én ny per runde, tak på 5. Ulikhet er trygt fordi
        # flere frie transfers aldri er en ulempe — løseren presser den opp av
        # seg selv, men kan ikke overskride det reglene tillater.
        if i == 0:
            m += ft[t] == min(ft_start, MAX_BANKED_FT)
        else:
            prev_t = gws[i - 1]
            big = 20
            # Vanlig runde: ubrukte frie transfers + én ny. I en wildcardrunde
            # oppheves denne grensen og erstattes av de to linjene under.
            m += ft[t] <= ft[prev_t] - pulp.lpSum(buy[p][prev_t] for p in P) \
                 + hits[prev_t] + 1 + big * wc.get(prev_t, 0)
            if wc:
                if CHIP_PRESERVES_FT:
                    # Fra 2024/25: lagrede beholdes, men chiprunden gir ingen ny.
                    m += ft[t] <= ft[prev_t] + big * (1 - wc.get(prev_t, 0))
                else:
                    m += ft[t] <= 1 + MAX_BANKED_FT * (1 - wc.get(prev_t, 0))

    # Én bruk per ubrukt vindu. Spenner horisonten over to vinduer (runde 19
    # til 20), kan chipen brukes én gang i hvert.
    for name, var in (("wildcard", wc), ("bboost", bb)):
        for lo, hi in windows.get(name, []):
            ts = [t for t in var if lo <= t <= hi]
            if ts:
                m += pulp.lpSum(var[t] for t in ts) <= 1
    # FPL tillater bare ÉN chip per runde. Uten denne la løseren Wildcard og
    # Bench Boost i samme uke — en plan som ikke kan gjennomføres.
    for t in gws:
        terms = [v[t] for v in (wc, bb) if t in v]
        if len(terms) > 1:
            m += pulp.lpSum(terms) <= 1

    status = m.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=SOLVER_SECONDS))
    return m, dict(x=x, y=y, c=c, buy=buy, sell=sell, hits=hits, wc=wc, bb=bb), pulp.LpStatus[status]


def report(pool, gws, v, status, grid=None):
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
        chip = ("WILDCARD" if t in v["wc"] and val(v["wc"][t]) else
                "BENCH BOOST" if t in v["bb"] and val(v["bb"][t]) else "")
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
        squad_t = [p for p in pool.element if val(v["x"][p][t])]
        if grid is not None:
            pts = sum(grid.loc[p, t] for p in xi) + (grid.loc[cap, t] if cap else 0)
            if chip == "BENCH BOOST":
                pts += sum(grid.loc[p, t] for p in squad_t if p not in xi)
            pts -= h * HIT_COST
        else:
            pts = float("nan")
        print(f"   forventet: {pts:.1f} poeng")
        plan.append({"gw": int(t), "chip": chip, "in": [name[p] for p in ins],
                     "out": [name[p] for p in outs], "hits": h,
                     "expected_points": round(float(pts), 2),
                     "captain": name[cap] if cap else None,
                     "xi": [name[p] for p in xi_sorted]})
    return plan


def main() -> None:
    xp = pd.read_csv(DERIVED / "expected_points.csv")
    squad, bank, chips_used, gw, sell, ft_start = load_state()
    if not squad:
        print("Fant ingen tropp — hopper over optimering.")
        return

    bs_now = json.loads((RAW / "bootstrap.json").read_text())
    history = json.loads((RAW / "entry_history.json").read_text())
    # Free Hit og Triple Captain er ikke modellert ennå.
    available = {c: w for c, w in chip_windows(bs_now, history).items()
                 if c in ("wildcard", "bboost")}
    finished = sum(1 for e in bs_now["events"] if e["finished"])
    chip_note = ""
    if finished < MIN_FINISHED_GW_FOR_CHIPS and available:
        chip_note = (f"chips holdt tilbake: bare {finished} ferdigspilte runder, "
                     f"krever {MIN_FINISHED_GW_FOR_CHIPS}")
        available = {}
    print(f"Utgangspunkt: GW{gw} · bank £{bank:.1f}m · frie transfers {ft_start} · "
          f"salgsverdi £{sum(sell.values()):.1f}m · chips tilgjengelig: "
          f"{', '.join(f'{c} R{lo}-{hi}' for c, w in sorted(available.items()) for lo, hi in w) or 'ingen'}")
    if chip_note:
        print(f"  {chip_note}")

    bs = json.loads((RAW / "bootstrap.json").read_text())
    nxt = next((e for e in bs["events"] if e["is_next"]), None)
    first_gw = nxt["id"] if nxt else gw + 1
    pool, grid, gws = build_pool(xp, squad, first_gw)
    print(f"  kandidater: {len(pool)} spillere · horisont GW{gws[0]}-{gws[-1]}")
    m, v, status = solve(pool, grid, gws, squad, bank, available, sell, ft_start)
    plan = report(pool, gws, v, status, grid)

    (DERIVED / "plan.json").write_text(json.dumps(
        {"generated_for_gw": int(gws[0]), "status": status,
         # objective inneholder benkvekt, hit-margin og byttefriksjon og er
         # derfor IKKE forventede FPL-poeng. Det er expected_points.
         "objective": round(pulp.value(m.objective), 2),
         "expected_points": round(sum(r["expected_points"] for r in plan), 1),
         "free_transfers_start": ft_start,
         "chip_note": chip_note, "plan": plan},
        ensure_ascii=False, indent=1))
    print(f"\n✓ målfunksjon: {pulp.value(m.objective):.1f} forventede poeng over {len(gws)} runder")


if __name__ == "__main__":
    main()
