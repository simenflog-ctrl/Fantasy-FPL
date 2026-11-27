"""Spillerpoeng i to poengsett: `codex` (egen ratemodell) og `repo_hybrid` (repoets xP skalert med våre minutter).

Flyttet fra samarbeid/gw10/codex/modell.py linje 32-149. Formlene er uendret. Nytt er bare:
  * runde/horisont er parametre,
  * minuttantakelser kommer fra en grunntabell pluss en overstyringsfil (i gw10 sto de i koden),
  * dobbeltrunder og blanke runder er håndtert uttrykkelig (se `prognose`).
"""
import math
from collections import defaultdict
from types import SimpleNamespace

import numpy as np

from uke import KINDS, COUNTS, heltall, les_csv, skriv_csv

STATS = ['expected_goals', 'expected_assists', 'bonus', 'yellow_cards', 'red_cards', 'own_goals',
         'penalties_saved', 'penalties_missed', 'saves']


def lagstyrke(u):
    """xG-basert angreps- og forsvarsstyrke per lag, krympet mot ligasnittet med 7 kamper.

    Returnerer (snitt xG per lag per kamp, {lag: (angrep, forsvar)}, {lag: [xG, xGA, kamper]}).
    forsvar > 1 betyr at laget slipper til mer enn snittet.
    """
    tx = defaultdict(float)
    for r in u.pm:
        tx[int(r['fixture']), int(r['team'])] += float(r['expected_goals'])
    tm = defaultdict(lambda: [0., 0., 0])
    for f in u.fx:
        if not f['finished'] or not f['event'] or f['event'] > u.siste:
            continue
        for t, op in [(f['team_h'], f['team_a']), (f['team_a'], f['team_h'])]:
            tm[t][0] += tx[f['id'], t]
            tm[t][1] += tx[f['id'], op]
            tm[t][2] += 1
    mean = sum(v[0] for v in tm.values()) / sum(v[2] for v in tm.values())
    strength = {t: ((v[0] + 7 * mean) / (v[2] + 7) / mean, (v[1] + 7 * mean) / (v[2] + 7) / mean) for t, v in tm.items()}
    for t in u.T:                       # lag uten spilte kamper: ligasnitt
        strength.setdefault(t, (1., 1.))
    return mean, strength, dict(tm)


def blokkerte(u):
    """Spillere som er ute (status u/n/i/s eller 0 %). Null poeng i hele horisonten, og kan ikke kjøpes."""
    return {p for p, e in u.E.items()
            if e['status'] in ['u', 'n', 'i', 's'] or e.get('chance_of_playing_next_round') == 0}


def roller(u):
    """Per spiller: (P(start), minutter gitt start, P(innhopp | ikke start), minutter gitt innhopp, P(60+ | start)).

    Starter vektes med halveringstid 4 runder, pluss en liten prior (0,35 start av 0,7 kamp).
    """
    roles = {}
    L = u.siste
    for p, e in u.E.items():
        hh = u.history.get(p, {}).get('history', [])
        w = [.5 ** ((L - r['round']) / 4) for r in hh]
        ps = (sum(a * r['starts'] for a, r in zip(w, hh)) + .35) / (sum(w) + .7) if hh else (e['starts'] + .35) / (L + .7)
        starts = [r for r in hh if r['starts']]
        subs = [r for r in hh if not r['starts'] and r['minutes'] > 0]
        mg = sum(r['minutes'] for r in starts) / len(starts) if starts else min(90, e['minutes'] / max(1, e['starts']))
        subprob = len(subs) / max(1, len(hh) - len(starts))
        submin = sum(r['minutes'] for r in subs) / max(1, len(subs))
        p60cond = (sum(r['minutes'] >= 60 for r in starts) + 4.5) / (len(starts) + 5)
        roles[p] = (ps, mg, subprob, submin, p60cond)
    return roles


# ---------------------------------------------------------------- minutter

def grunnminutter(u, roles, blocked):
    """Motorens egen minuttabell før Claudes overstyringer: {(id, runde): [p_start, forventede_min, kilde]}.

    Verdiene er per kamp og er like i alle runder. Ikke avrundet ennå (se `avrund`).
    """
    md = {}
    for p, e in u.E.items():
        ps, mg, subprob, submin, _ = roles[p]
        av = 0 if p in blocked else ((e.get('chance_of_playing_next_round') or 50) / 100 if e['status'] == 'd' else 1)
        q = ps * av
        mi = (ps * mg + (1 - ps) * subprob * submin) * av
        kilde = 'Modell: vektede starter R1-R%d + prior; egne min/start' % u.siste
        if p in blocked:
            kilde += '; ute (API-status), null i hele horisonten'
        elif e['status'] == 'd':
            kilde += '; API d-prosent holdt konstant'
        for g in u.GWS:
            md[p, g] = [q, mi, kilde]
    return md


def bruk_overstyringer(u, md, rader, blocked):
    """Legg Claudes overstyringer oppå tabellen, i filrekkefølge. Endrer md på stedet.

    Hver rad: `id` ELLER `lag` (kortnavn), `gw_fra`, `gw_til`, `kilde` (påkrevd), og enten
      * `faktor`: p_start og forventede_min ganges med tallet, eller
      * `p_start` og/eller `forventede_min`: settes. Er bare den ene oppgitt, skaleres den andre i samme forhold.
    Lagrader rører ikke spillere som er ute. En rad som setter verdier for en spiller som er ute, gjør
    spilleren tilgjengelig i de rundene (kjent returdato). Returnerer mengden av slike (id, runde).
    """
    retur = set()
    lag = {v: k for k, v in u.T.items()}
    for n, r in enumerate(rader, 2):
        hvor = 'overstyring linje %d' % n
        if not (r.get('kilde') or '').strip():
            raise ValueError(hvor + ': kilde mangler')
        har_id, har_lag = bool((r.get('id') or '').strip()), bool((r.get('lag') or '').strip())
        if har_id == har_lag:
            raise ValueError(hvor + ': oppgi enten id eller lag')
        if har_id:
            spillere = [int(r['id'])]
            if spillere[0] not in u.E:
                raise ValueError(hvor + ': ukjent id ' + r['id'])
        else:
            if r['lag'] not in lag:
                raise ValueError(hvor + ': ukjent lag ' + r['lag'])
            spillere = [p for p, e in u.E.items() if e['team'] == lag[r['lag']] and p not in blocked]
        f = (r.get('faktor') or '').strip()
        nps = (r.get('p_start') or '').strip()
        nmi = (r.get('forventede_min') or '').strip()
        if bool(f) == bool(nps or nmi):
            raise ValueError(hvor + ': oppgi enten faktor eller p_start/forventede_min')
        # Hele raden kontrolleres før den brukes: en rad med omvendt intervall eller feil tall ble før hoppet over
        # uten melding (Codex' kontroll 21. nov, F3).
        fra, til = heltall(r.get('gw_fra')), heltall(r.get('gw_til'))
        if fra is None or til is None or fra > til:
            raise ValueError(hvor + ': gw_fra og gw_til må være hele runder med gw_fra <= gw_til (fikk %r-%r)'
                             % (r.get('gw_fra'), r.get('gw_til')))
        # Hele intervallet må ligge i horisonten; en rad som bare delvis gjorde det, ble før klippet uten melding
        # (Codex' kontroll 23. nov, F3).
        if fra < u.g0 or til > u.slutt:
            raise ValueError(hvor + ': runde %d-%d ligger ikke helt innenfor horisonten %d-%d'
                             % (fra, til, u.g0, u.slutt))
        for navn, tekst in (('faktor', f), ('p_start', nps), ('forventede_min', nmi)):
            if tekst:
                try:
                    v = float(tekst)
                except ValueError:
                    raise ValueError(hvor + ': %s er ikke et tall (%r)' % (navn, tekst))
                if not (math.isfinite(v) and v >= 0):
                    raise ValueError(hvor + ': %s må være et endelig tall >= 0 (%r)' % (navn, tekst))
        for p in spillere:
            for g in range(fra, til + 1):
                if (p, g) not in md:
                    continue
                q, mi, kilde = md[p, g]
                if f:
                    q *= float(f)
                    mi *= float(f)
                else:
                    if nps and nmi:
                        q, mi = float(nps), float(nmi)
                    elif nps:
                        if q == 0 and float(nps) > 0:
                            raise ValueError(hvor + ': p_start settes fra 0; oppgi også forventede_min')
                        mi = mi * float(nps) / q if q else 0.
                        q = float(nps)
                    else:
                        if mi == 0 and float(nmi) > 0:
                            raise ValueError(hvor + ': minutter settes fra 0; oppgi også p_start')
                        q = q * float(nmi) / mi if mi else 0.
                        mi = float(nmi)
                    if p in blocked and (q > 0 or mi > 0):
                        retur.add((p, g))
                if not (0 <= q <= 1 and 0 <= mi <= 90):
                    raise ValueError(hvor + ': gir p_start %.3f / minutter %.1f utenfor lovlig område' % (q, mi))
                md[p, g] = [q, mi, kilde + '; ' + r['kilde'].strip()]
    return retur


def avrund(md):
    """Samme avrunding som gw10-filen (4 og 2 desimaler). Prognosen regnes alltid på avrundede tall."""
    for k, (q, mi, kilde) in md.items():
        md[k] = [round(q, 4), round(mi, 2), kilde]
    return md


def skriv_minutter(u, md, sti, retur=frozenset()):
    """Minuttabellen som ble brukt. `retur` = 1 der en spiller som er ute, regnes likevel (kjent returdato),
    slik at tabellen kan leses inn igjen som `minuttabell` og gi de samme poengene."""
    skriv_csv(sti, [dict(id=p, navn=u.E[p]['web_name'], lag=u.T[u.E[p]['team']], gw=g, p_start=md[p, g][0],
                         forventede_min=md[p, g][1], retur=int((p, g) in retur), kilde=md[p, g][2])
                    for p in u.ids for g in u.GWS])


def les_minuttabell(u, sti):
    """Les en hel, frossen minuttabell. Støtter både `gw` og `gw_fra`/`gw_til` (gw10-formatet).

    Returnerer (md, retur). `retur` leses fra kolonnen med samme navn (skrevet av `skriv_minutter`); tabeller uten
    kolonnen (gw10) gir ingen returer, og spillere som er ute, regnes da som ute i hele horisonten.
    """
    md, retur = {}, set()
    for r in les_csv(sti):
        lo, hi = (int(r['gw']), int(r['gw'])) if r.get('gw') else (int(r['gw_fra']), int(r['gw_til']))
        for g in range(lo, hi + 1):
            assert (int(r['id']), g) not in md, 'Overlappende minuttrader'
            md[int(r['id']), g] = [float(r['p_start']), float(r['forventede_min']), r.get('kilde', '')]
            if (r.get('retur') or '0').strip() not in ('', '0'):
                retur.add((int(r['id']), g))
    assert set(md) >= {(p, g) for p in u.ids for g in u.GWS}, 'Minuttabellen dekker ikke alle spillere og runder'
    return md, retur


# ---------------------------------------------------------------- rater

def rater(u):
    """Per-90-rater per spiller, krympet mot egne tidligere sesonger (540 min) eller posisjonssnitt (270 min).

    Returnerer (rates, dc_rates): rates[id][stat] og andelen kamper på 60+ min der spilleren når
    grensen for defensive bidrag.
    """
    E, history = u.E, u.history
    pri = {}
    for k in COUNTS:
        ee = [e for e in E.values() if e['element_type'] == k and e['minutes'] > 0]
        m = sum(e['minutes'] for e in ee)
        pri[k] = {s: sum(float(e.get(s, 0)) for e in ee) * 90 / m for s in STATS}
    dcbase = {}
    for k in COUNTS:
        hh = [r for p, h in history.items() if E[p]['element_type'] == k for r in h.get('history', []) if r['minutes'] >= 60]
        threshold = 10 if k == 2 else 12
        dcbase[k] = sum(r.get('defensive_contribution', 0) >= threshold for r in hh) / max(1, len(hh)) if k != 1 else 0
    rates, dc_rates = {}, {}
    for p, e in E.items():
        k = e['element_type']
        past = [r for r in history.get(p, {}).get('history_past', [])
                if r.get('minutes', 0) >= 450 and r['season_name'] < u.sesong][-2:]
        ws = [.5 ** (len(past) - 1 - j) for j in range(len(past))]
        prior = {}
        for s in STATS:
            valid = [(w, r) for w, r in zip(ws, past) if r.get(s) is not None]
            prior[s] = sum(w * float(r[s]) for w, r in valid) * 90 / sum(w * r['minutes'] for w, r in valid) if valid else pri[k][s]
        weight = 540 if past else 270
        rates[p] = {s: (float(e.get(s, 0)) * 90 + weight * prior[s]) / (e['minutes'] + weight) for s in STATS}
        hh = [r for r in history.get(p, {}).get('history', []) if r['minutes'] >= 60]
        threshold = 10 if k == 2 else 12
        dc_rates[p] = (sum(r.get('defensive_contribution', 0) >= threshold for r in hh) + 3 * dcbase[k]) / (len(hh) + 3) if k != 1 else 0
    return rates, dc_rates


# ---------------------------------------------------------------- prognose

def prognose(u, md, retur=frozenset()):
    """Regn begge poengsett for alle spillere og runder i horisonten.

    md    : avrundet minuttabell {(id, runde): [p_start, forventede_min, kilde]}, verdier per kamp
    retur : (id, runde) der en spiller som er ute likevel skal regnes (kjent returdato fra overstyring)

    Dobbeltrunde: poengene er summen over kampene; P(spiller) = 1 - (1-p)^antall kamper.
    Blank runde: 0 poeng og P(spiller) = 0, slik at spilleren utløser autobytte.

    Returnerer et objekt med
      XP, REPO : (N, H) forventede poeng (codex og repo_hybrid)
      PP       : (N, H) sannsynlighet for minst ett minutt i runden
      UI       : indekser til spillere som kan kjøpes
      blocked, strength, mean, roles, rates, dc_rates, repo_mangler
    """
    E, sc, ix = u.E, u.sc, u.ix
    mean, strength, tm = lagstyrke(u)
    roles = roller(u)
    rates, dc_rates = rater(u)
    blocked = blokkerte(u)

    def forecast(p, g):
        e = E[p]
        k = e['element_type']
        po = KINDS[k]
        r = rates[p]
        ps, mi = md[p, g][0], md[p, g][1]
        assert 0 <= ps <= 1 and 0 <= mi <= 90
        _, _, subprob, _, p60c = roles[p]
        availability = max(ps, (e.get('chance_of_playing_next_round') or 50) / 100) if e['status'] == 'd' else 1
        pp = min(1, ps + max(0, availability - ps) * subprob)
        pp = 0 if mi == 0 else pp
        if mi > 0 and pp == 0 and (p not in blocked or (p, g) in retur):
            # Minutter uten sannsynlighet for å spille ga før poeng med P(spiller) = 0 (Codex' kontroll 21. nov, F9).
            raise ValueError('Minuttabellen gir %s (id %d) %.1f minutter i runde %d, men P(spiller) = 0: p_start er %.3f '
                             'og spilleren har ingen innhopp i historikken. Sett p_start > 0 eller minutter 0.'
                             % (e['web_name'], p, mi, g, ps))
        p60 = min(ps * p60c, mi / 60)
        val = bonus = 0.
        kamper = u.kamper.get((g, e['team']), [])
        for f in kamper:
            home = e['team'] == f['team_h']
            op = f['team_a'] if home else f['team_h']
            lam = mean * strength[op][0] * strength[e['team']][1] * (.9 if home else 1.1)
            scale = strength[op][1] * (1.1 if home else .9)
            attack = (r['expected_goals'] * sc['goals_scored'][po] + r['expected_assists'] * sc['assists']) * mi / 90 * scale
            gc = sum(z // 2 * math.exp(-lam) * lam ** z / math.factorial(z) for z in range(25))
            sv = r['saves'] * mi / max(ps, 1e-8) / 90 if ps else 0
            savepts = ps * sum(z // 3 * math.exp(-sv) * sv ** z / math.factorial(z) for z in range(40)) * sc['saves'] if k == 1 else 0
            other = sum(r[s] * sc[s] for s in STATS if s not in ['expected_goals', 'expected_assists', 'saves']) * mi / 90
            bonus += r['bonus'] * sc['bonus'] * mi / 90
            val += (sc['short_play'] * pp + (sc['long_play'] - sc['short_play']) * p60 + attack
                    + sc['clean_sheets'][po] * math.exp(-lam) * p60 + sc['goals_conceded'][po] * gc * mi / 90
                    + savepts + dc_rates[p] * sc['defensive_contribution'][po] * p60 + other)
        n = len(kamper)
        pp_runde = 0 if n == 0 else pp if n == 1 else 1 - (1 - pp) ** n
        return max(0, val), bonus, pp_runde

    N, H, g0 = u.N, u.H, u.g0
    XP = np.zeros((N, H))
    PP = np.zeros((N, H))
    BONUS = np.zeros((N, H))
    for p in u.ids:
        for g in u.GWS:
            XP[ix[p], g - g0], BONUS[ix[p], g - g0], PP[ix[p], g - g0] = forecast(p, g)
    REPO = XP.copy()
    repo_raw = defaultdict(list)
    for r in u.repo:
        repo_raw[int(r['element']), int(r['gw'])].append(r)
    mangler = 0
    for p in u.ids:
        for g in u.GWS:
            rr = repo_raw.get((p, g))
            if not rr:
                continue
            mi = md[p, g][1]
            if len(rr) != len(u.kamper.get((g, E[p]['team']), [])) or any(float(r['exp_minutes']) == 0 for r in rr):
                mangler += 1          # repo-filen har annet kampantall eller 0 minutter: behold codex
                continue
            REPO[ix[p], g - g0] = sum(float(r['xp']) * mi / float(r['exp_minutes']) for r in rr)
    for p in blocked:
        for g in u.GWS:
            if (p, g) not in retur:
                XP[ix[p], g - g0] = 0
                REPO[ix[p], g - g0] = 0
                PP[ix[p], g - g0] = 0
    g_kjop = u.GWS[1] if H > 1 else u.GWS[0]     # kjøpsfilteret ser på runden etter den første (som gw10)
    UI = np.array([ix[p] for p in u.ids if p not in blocked and E[p].get('can_select', True)
                   and md[p, g_kjop][0] >= (.35 if E[p]['status'] == 'd' else .5)], dtype=np.int64)
    return SimpleNamespace(XP=XP, REPO=REPO, PP=PP, BONUS=BONUS, UI=UI, blocked=blocked, strength=strength,
                           mean=mean, tm=tm, roles=roles, rates=rates, dc_rates=dc_rates, repo_mangler=mangler,
                           repo_runder=sorted({g for _, g in repo_raw}))


def lag_minutter(u, overstyringer=None, minuttabell=None):
    """Hele minuttkjeden: frossen tabell, eller grunntabell + overstyringer. Returnerer (md, retur)."""
    if minuttabell:
        md, retur = les_minuttabell(u, minuttabell)
        return md, frozenset(retur)
    blocked = blokkerte(u)
    md = grunnminutter(u, roller(u), blocked)
    retur = bruk_overstyringer(u, md, les_csv(overstyringer), blocked) if overstyringer else set()
    return avrund(md), frozenset(retur)
