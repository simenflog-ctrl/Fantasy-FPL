"""Forventet lagpoeng for én runde med eksakte autobytter, kaptein og visekaptein.

Flyttet uendret fra samarbeid/gw10/codex/modell.py linje 151-290.

Forutsetning: spillerne spiller eller spiller ikke uavhengig av hverandre, med sannsynlighet pp.
xp er ubetinget forventet poeng; en spiller som kommer inn fra benken gir xp/pp (poeng gitt at han spiller).

Troppen `s` er alltid 15 interne indekser sortert på (posisjon, indeks): plass 0-1 keepere, 2-6 forsvar,
7-11 midtbane, 12-14 angrep. `xi` og `bn` er plasser (0-14) i troppen, ikke spillerindekser.
"""
import itertools

import numpy as np
from numba import njit

FORMS = [(d, m, 10 - d - m) for d in range(3, 6) for m in range(2, 6) if 1 <= 10 - d - m <= 3]
PERMS = np.array(list(itertools.permutations(range(3))), dtype=np.int64)


def bygg_lut():
    """Oppslagstabell for lovlige autobytter.

    LUT[formasjon, benkens posisjoner, antall fraværende per linje, hvilke benkespillere som spiller]
    = bitmaske over de tre utespillerne på benken som kommer inn.
    Regel: første benkespiller som kan gi en lovlig formasjon (minst 3 forsvar, 2 midtbane, 1 spiss) går inn først.
    """
    LUT = np.zeros((144, 27, 144, 8), dtype=np.int8)
    for d, m, f in FORMS:
        fi = d * 24 + m * 4 + f
        benchpos = [0] * (5 - d) + [1] * (5 - m) + [2] * (3 - f)
        for bp in set(itertools.permutations(benchpos)):
            bi = bp[0] * 9 + bp[1] * 3 + bp[2]
            for miss in itertools.product(range(d + 1), range(m + 1), range(f + 1)):
                mi = miss[0] * 24 + miss[1] * 4 + miss[2]
                feasible = []
                for sm in range(8):
                    add = [sum(bool(sm & (1 << j)) and bp[j] == k for j in range(3)) for k in range(3)]
                    n = sum(add)
                    ok = False
                    for rem in itertools.product(*(range(z + 1) for z in miss)):
                        if sum(rem) != n:
                            continue
                        final = np.array([d, m, f]) - rem + add
                        if all(final >= np.array([3, 2, 1])) and all(final <= np.array([5, 5, 3])):
                            ok = True
                            break
                    if ok:
                        feasible.append(sm)
                for av in range(8):
                    choices = [sm for sm in feasible if sm & av == sm]
                    best = max(choices, key=lambda sm: ((sm & 1) > 0, (sm & 2) > 0, (sm & 4) > 0))
                    LUT[fi, bi, mi, av] = best
    return LUT


LUT = bygg_lut()


@njit
def benchweights(s, xi, bn, pp, pos, lut):
    """Per utespiller på benken: forventet antall ganger han teller, delt på pp (altså vekten som ganges med xp)."""
    counts = np.zeros(3, np.int64)
    prob = np.zeros((3, 6))
    prob[:, 0] = 1.
    for j in xi:
        if pos[s[j]] == 1:
            continue
        k = pos[s[j]] - 2
        q = 1 - pp[s[j]]
        n = counts[k]
        for z in range(n + 1, -1, -1):
            prob[k, z] = (prob[k, z] * (1 - q) if z <= n else 0) + (prob[k, z - 1] * q if z > 0 else 0)
        counts[k] += 1
    fi = counts[0] * 24 + counts[1] * 4 + counts[2]
    bi = (pos[s[bn[0]]] - 2) * 9 + (pos[s[bn[1]]] - 2) * 3 + pos[s[bn[2]]] - 2
    out = np.zeros(3)
    for a in range(counts[0] + 1):
        for b_ in range(counts[1] + 1):
            for c in range(counts[2] + 1):
                pr = prob[0, a] * prob[1, b_] * prob[2, c]
                if pr < 1e-15:
                    continue
                mi = a * 24 + b_ * 4 + c
                for av in range(8):
                    joint = pr
                    for j in range(3):
                        joint *= pp[s[bn[j]]] if av & (1 << j) else 1 - pp[s[bn[j]]]
                    chosen = lut[fi, bi, mi, av]
                    for j in range(3):
                        if chosen & (1 << j) and pp[s[bn[j]]] > 0:
                            out[j] += joint / pp[s[bn[j]]]
    return out


@njit
def evaluate_selection(s, xi, bn, gkb, xp, pp, pos, lut, bb=False):
    """Forventet poeng for en gitt ellever (xi), benkerekkefølge (bn, tre utespillere) og reservekeeper (gkb).

    Returnerer (verdi, vekter per plass i troppen, kapteinens plass, visekapteinens plass).
    Verdi = sum av vekt * xp. Med bb=True (Bench Boost) teller alle 15.
    """
    weights = np.zeros(15)
    for j in xi:
        weights[j] = 1.
    if bb:
        weights[:] = 1.
    else:
        bw = benchweights(s, xi, bn, pp, pos, lut)
        for k in range(3):
            weights[bn[k]] = bw[k]
        gk = 1 - gkb
        weights[gkb] = 1 - pp[s[gk]]
    # Kaptein + vise: visen arver doblingen når kapteinen ikke spiller.
    cap = -1
    vice = -1
    extra = -1.
    for c in xi:
        for v in xi:
            if c == v:
                continue
            ev = xp[s[c]] + (1 - pp[s[c]]) * xp[s[v]]
            if ev > extra + 1e-12 or (abs(ev - extra) < 1e-12 and cap >= 0 and xp[s[c]] > xp[s[cap]]):
                extra = ev
                cap = c
                vice = v
    weights[cap] += 1.
    weights[vice] += 1 - pp[s[cap]]
    value = 0.
    for j in range(15):
        value += weights[j] * xp[s[j]]
    return value, weights, cap, vice


@njit
def select(s, xp, pp, pos, lut, perms, exhaustive=False, bb=False):
    """Beste ellever, benkerekkefølge, kaptein og vise for troppen s i én runde.

    exhaustive=True prøver alle lovlige ellevere og benkerekkefølger (brukes i hovedtabellene).
    exhaustive=False prøver en kort liste (brukes i simuleringer); hver kandidat regnes like eksakt.
    Returnerer (verdi, vekter, xi-plasser, benk-plasser [keeper, 1., 2., 3.], kaptein-plass, vise-plass).
    """
    masks = np.zeros((400, 3), np.int64)
    nm = 0
    if exhaustive:
        for a in range(2, 13):
            for b_ in range(a + 1, 14):
                for c in range(b_ + 1, 15):
                    masks[nm] = np.array([a, b_, c])
                    nm += 1
    else:
        for mode in range(4):
            ranks = np.zeros((3, 5), np.int64)
            nn = np.zeros(3, np.int64)
            for k in range(3):
                scores = np.full(15, -1e8)
                for j in range(2, 15):
                    if pos[s[j]] != k + 2:
                        continue
                    if mode == 0:
                        v = xp[s[j]]
                    elif mode == 1:
                        v = xp[s[j]] / max(pp[s[j]], .05)
                    else:
                        v = xp[s[j]] + (1 - pp[s[j]]) * (2 if mode == 2 else 4)
                    scores[j] = v
                order = np.argsort(-scores)
                for j in order:
                    if scores[j] > -1e7:
                        ranks[k, nn[k]] = j
                        nn[k] += 1
            for d in range(3, 6):
                for m in range(2, 6):
                    f = 10 - d - m
                    if f < 1 or f > 3:
                        continue
                    bslots = np.zeros(3, np.int64)
                    cnt = 0
                    for k, n in enumerate((d, m, f)):
                        for jj in range(n, nn[k]):
                            bslots[cnt] = ranks[k, jj]
                            cnt += 1
                    bslots.sort()
                    duplicate = False
                    for old in range(nm):
                        if np.all(masks[old] == bslots):
                            duplicate = True
                            break
                    if not duplicate:
                        masks[nm] = bslots
                        nm += 1
    best = -1.
    besttie = -1.
    bestw = np.zeros(15)
    bestxi = np.zeros(11, np.int64)
    bestbn = np.zeros(4, np.int64)
    bestc = bestv = 0
    for z in range(nm):
        raw = masks[z]
        counts = np.array([5, 5, 3])
        for j in raw:
            counts[pos[s[j]] - 2] -= 1
        if counts[0] < 3 or counts[1] < 2 or counts[2] < 1:
            continue
        for gk in range(2):
            xi = np.zeros(11, np.int64)
            xi[0] = gk
            nn = 1
            for j in range(2, 15):
                if j != raw[0] and j != raw[1] and j != raw[2]:
                    xi[nn] = j
                    nn += 1
            for perm in perms:
                bn = raw[perm]
                val, w, cap, vice = evaluate_selection(s, xi, bn, 1 - gk, xp, pp, pos, lut, bb)
                tie = 1e-6 * (3 * xp[s[bn[0]]] + 2 * xp[s[bn[1]]] + xp[s[bn[2]]])
                for j in xi:
                    tie += xp[s[j]] + .001 * pp[s[j]]
                if val > best + 1e-12 or (abs(val - best) < 1e-12 and tie > besttie):
                    best = val
                    besttie = tie
                    bestw = w
                    bestxi = xi.copy()
                    bestbn = np.array([1 - gk, bn[0], bn[1], bn[2]])
                    bestc = cap
                    bestv = vice
                if bb:
                    break
    return best, bestw, bestxi, bestbn, bestc, bestv


@njit
def obj_batch(squads, pred, pp, cols, bb, pos, lut, perms):
    """Sum over rundene i `cols` av beste lagpoeng (kort liste) for hver tropp. bb = kolonnen med Bench Boost."""
    vv = np.zeros(len(squads))
    for j in range(len(squads)):
        for t in cols:
            z = select(squads[j], pred[:, t], pp[:, t], pos, lut, perms, False, t == bb)
            vv[j] += z[0]
    return vv
