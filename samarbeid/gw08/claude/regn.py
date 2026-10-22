"""Claudes enkle kontrollregning: beste ellever og kaptein per runde R8-R13 for noen kandidattropper.

Bruker repoets data/derived/expected_points.csv uendret, unntatt følsomhetsjusteringer som er
oppgitt eksplisitt nedenfor. Ingen benkpoeng eller autobytter er regnet med (nedre grense for verdien av benken).
Kjør fra repoets rot: python3 samarbeid/gw08/claude/regn.py
"""
import itertools
import pandas as pd

EP = pd.read_csv("data/derived/expected_points.csv")
XP = EP.groupby(["element", "gw"]).xp.sum().unstack(fill_value=0.0)
POS = EP.drop_duplicates("element").set_index("element").pos.replace({"GK": "GKP"})
NAME = EP.drop_duplicates("element").set_index("element").web_name

BASE = [109, 8, 418, 469, 31, 427, 426, 542, 124, 411, 106, 111, 368, 175, 272]
SZOB, TAV, DH, THIAGO, JP, KUSI, TA = 368, 68, 236, 106, 165, 272, 194

FORMATIONS = [(d, m, f) for d in (3, 4, 5) for m in (2, 3, 4, 5) for f in (1, 2, 3) if d + m + f == 10]


def best_xi(squad, xp):
    by = {p: sorted((e for e in squad if POS[e] == p), key=lambda e: -xp[e]) for p in ("GKP", "DEF", "MID", "FWD")}
    best = None
    for d, m, f in FORMATIONS:
        if len(by["DEF"]) < d or len(by["MID"]) < m or len(by["FWD"]) < f:
            continue
        xi = by["GKP"][:1] + by["DEF"][:d] + by["MID"][:m] + by["FWD"][:f]
        tot = sum(xp[e] for e in xi) + max(xp[e] for e in xi)  # kaptein dobles
        if best is None or tot > best[0]:
            best = (tot, xi)
    return best


def evaluate(squad, gws, adj=None, hit=0):
    total = -hit
    for gw in gws:
        xp = XP[gw].copy()
        for e, f in (adj or {}).items():
            xp[e] *= f
        total += best_xi(squad, xp)[0]
    return total


def swap(squad, *pairs):
    s = list(squad)
    for out, inn in pairs:
        s[s.index(out)] = inn
    return s


PLANS = {
    "A spar (0 bytter)": (BASE, 0),
    "B Szoboszlai->Tavernier": (swap(BASE, (SZOB, TAV)), 0),
    "B2 Szoboszlai->Dewsbury-Hall": (swap(BASE, (SZOB, DH)), 0),
    "C B + Thiago->João Pedro": (swap(BASE, (SZOB, TAV), (THIAGO, JP)), 0),
    "C2 B + Kusi-Asare->Thomas-Asante": (swap(BASE, (SZOB, TAV), (KUSI, TA)), 0),
}
SCEN = {
    "modell": {},
    "Fernandes x0.7": {426: 0.7},
    "Tavernier x0.8": {TAV: 0.8},
    "Thiago x1.2 (xG-regresjon)": {THIAGO: 1.2},
}

if __name__ == "__main__":
    gws = sorted(XP.columns)
    rows = []
    for name, (sq, hit) in PLANS.items():
        r = {"plan": name}
        r["R8"] = round(evaluate(sq, [8], hit=hit), 1)
        for sname, adj in SCEN.items():
            r[f"R8-13 {sname}"] = round(evaluate(sq, gws, adj, hit), 1)
        rows.append(r)
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    df.to_csv("samarbeid/gw08/claude/regn_resultat.csv", index=False)
    sq = swap(BASE, (SZOB, TAV))
    tot, xi = best_xi(sq, XP[8])
    print("\nR8 ellever (plan B):", [NAME[e] for e in xi], "kaptein:", NAME[max(xi, key=lambda e: XP[8][e])])
