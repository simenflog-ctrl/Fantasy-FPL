#!/usr/bin/env python3
"""Uavhengige kontrolltilfeller. Skriver bare under denne filens motorkontroll-data/.

Kjør med Anaconda og PYTHONDONTWRITEBYTECODE=1. RETTET betyr at et tidligere ugyldig tilfelle avvises; GJENSTÅR bekrefter avviket. Ingen produksjonskode endres.
"""
import ast
import copy
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import time

HER = Path(__file__).resolve().parent
ROT = HER.parents[2]
MOTOR = ROT / 'samarbeid/motor'
UT = HER / 'motorkontroll-data'
UT.mkdir(exist_ok=True)
(UT / 'tmp').mkdir(exist_ok=True)
os.environ['TMPDIR'] = str(UT / 'tmp')
sys.path[:0] = [str(MOTOR), str(MOTOR / 'tester')]

import numpy as np
import poeng
import kjor
import syntetisk
import skadesim
from lag import LUT, PERMS, select
from motor import Motor
from uke import Uke, les_json, les_csv, skriv_csv, skriv_json

FUNN = []


def logg(navn, dom, **data):
    rad = dict(test=navn, dom=dom, **data)
    FUNN.append(rad)
    print(json.dumps(rad, ensure_ascii=False), flush=True)
    (UT / 'eksempler.json').write_text(json.dumps(FUNN, ensure_ascii=False, indent=2))


def feil(fn, typer=(ValueError, AssertionError, KeyError)):
    try:
        fn()
    except typer as e:
        return type(e).__name__ + ': ' + str(e)
    raise AssertionError('Forventet avvisning')


def avvisningsfunn(navn, fn, sjekk=None, **data):
    """Behold reproduksjonen når den lykkes; logg rettelse hvis motoren avviser."""
    try:
        res = fn()
    except (ValueError, AssertionError) as e:
        logg(navn, 'RETTET', melding=type(e).__name__ + ': ' + str(e), **data)
        return None
    if sjekk:
        sjekk(res)
    logg(navn, 'GJENSTÅR', **data)
    return res


def ny_mappe(navn):
    p = UT / navn
    assert p.parent == UT and p.name not in ('tmp', '')
    if p.exists():
        shutil.rmtree(p)
    p.mkdir()
    return p


def frys_fixture():
    """Lite lokalt repo med faste filnavn; tester repoet til ukemappen."""
    repo = ny_mappe('frys-repo')
    (repo / 'data/derived').mkdir(parents=True)
    for fn in kjor.FRYSES:
        (repo / 'data/derived' / fn).write_text('kontrollkilde ' + fn + '\n')
    w = repo / 'samarbeid/gw-kontroll'
    w.mkdir(parents=True)
    return repo, w


def liga(**kw):
    u = syntetisk.bygg(**kw)
    md, retur = poeng.lag_minutter(u)
    pr = poeng.prognose(u, md, retur)
    return u, md, pr


def rad(p='', lag='', fra=6, til=6, **kw):
    r = dict(id=str(p), lag=lag, gw_fra=str(fra), gw_til=str(til), faktor='', p_start='', forventede_min='', kilde='kontroll')
    r.update({k: str(v) for k, v in kw.items()})
    return r


def skriv_uke(u, navn):
    w = ny_mappe(navn)
    (w / 'data/element_summary').mkdir(parents=True, exist_ok=True)
    (w / 'motor/input').mkdir(parents=True, exist_ok=True)
    (w / 'claude').mkdir(exist_ok=True)
    for fn, obj in [('bootstrap', u.b), ('fixtures', u.fx), ('entry', {'last_deadline_bank': u.bank}),
                    ('salgspriser', [dict(id=p, salgspris=int(u.SALES[u.ix[p]]) / 10) for p in u.orig])]:
        skriv_json(w / ('data/' + fn + '.json'), obj)
    for p, h in u.history.items():
        skriv_json(w / ('data/element_summary/%d.json' % p), h)
    skriv_csv(w / 'motor/input/player_matches.csv', u.pm)
    skriv_csv(w / 'motor/input/expected_points.csv', u.repo)
    return w


def kj(w, o, **kw):
    return kjor.kjor(w, oppsett=o, logg=lambda s: None, **kw)


def main():
    start = time.monotonic()
    u, md, pr = liga()
    # Eksakt AST-likhet av de fire flyttede numba-funksjonene.
    old = ast.parse((ROT / 'samarbeid/gw10/codex/modell.py').read_text())
    new = ast.parse((MOTOR / 'lag.py').read_text())
    def funksjon(tree, navn):
        f = copy.deepcopy(next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == navn))
        if isinstance(f.body[0], ast.Expr) and isinstance(f.body[0].value, (ast.Str, ast.Constant)):
            f.body.pop(0)
        return ast.dump(f, include_attributes=False)
    navn = ['benchweights', 'evaluate_selection', 'select', 'obj_batch']
    assert all(funksjon(old, n) == funksjon(new, n) for n in navn)
    logg('Ekvivalens lag.py', 'OK', ast_identiske=navn)

    # Begge poengsett gjennom autobytter og BB, også dobbelt/blankt.
    from fasit_autobytter import forventet
    maks = 0.
    for pred in [pr.XP, pr.REPO]:
        for t in [0, 1]:
            for bb in [False, True]:
                v, weights, xi, bn, c, vc = select(u.ORIG, pred[:, t], pr.PP[:, t], u.POS, LUT, PERMS, True, bb)
                fasit = forventet(list(u.POS[u.ORIG]), list(pred[u.ORIG, t]), list(pr.PP[u.ORIG, t]),
                                  list(xi), list(bn), int(c), int(vc), bb)
                maks = max(maks, abs(v - fasit))
                assert abs(v - fasit) < 1e-9
    logg('Dobbel/blank, begge poengsett, autobytter og BB', 'OK', maks_avvik=maks)

    # Overstyringer i filrekkefølge; alle blokkeringsflagg; returdato.
    p = syntetisk.pid(1, 2)
    base = copy.deepcopy(md)
    poeng.bruk_overstyringer(u, base, [rad(p, p_start=.8, forventede_min=80), rad(lag='L1', faktor=.5)], set())
    assert base[p, 6][:2] == [.4, 40.]
    base2 = copy.deepcopy(md)
    poeng.bruk_overstyringer(u, base2, [rad(lag='L1', faktor=.5), rad(p, p_start=.8, forventede_min=80)], set())
    assert base2[p, 6][:2] == [.8, 80.]
    for status, sjanse in [('u', None), ('n', None), ('i', None), ('s', None), ('a', 0)]:
        b = copy.deepcopy(u)
        b.E[p]['status'], b.E[p]['chance_of_playing_next_round'] = status, sjanse
        blocked = poeng.blokkerte(b)
        mm = poeng.grunnminutter(b, poeng.roller(b), blocked)
        assert all(mm[p, g][:2] == [0, 0] for g in b.GWS)
        ret = poeng.bruk_overstyringer(b, mm, [rad(lag='L1', p_start=.8, forventede_min=80),
                                              rad(p, fra=7, til=8, p_start=.8, forventede_min=80)], blocked)
        assert mm[p, 6][:2] == [0, 0] and ret == {(p, 7), (p, 8)}
        pp = poeng.prognose(b, mm, ret)
        assert pp.XP[b.ix[p], 0] == 0 and pp.XP[b.ix[p], 1] > 0
        assert b.ix[p] not in pp.UI
    negative = [rad(p, faktor=.5, kilde=''), rad(999999, faktor=.5), rad(p, faktor=.5, p_start=.8),
                rad(lag='ukjent', faktor=.5), rad(p, lag='L1', faktor=.5), rad(p, faktor=-1)]
    for r in negative:
        feil(lambda: poeng.bruk_overstyringer(u, copy.deepcopy(md), [r], set()))
    logg('Overstyringer: rekkefølge, flagg, retur, kilde, id og eksklusivitet', 'OK')

    # Tomt chipsett fungerer, men felles datoer omgår det.
    m = Motor(u, pr, ft=2, bb_runder=[], fh_runder=[], tmp=UT / 'tmp')
    plain = m.bane(u.ORIG, full=True)
    assert m.velg_bb(plain) is None
    avvist = feil(lambda: Motor(u, pr, fh_runder=[6]))
    feil(lambda: m.bane(u.ORIG, fh=6))
    logg('FH nå via ordinær liste/bane avvises', 'OK', melding=avvist)
    m_fh = Motor(u, pr, ft=2, bb_runder=[7, 8], fh_runder=[7, 8], tmp=UT / 'tmp')
    p_fh = m_fh.bane(u.ORIG, fh=7, full=True)
    avvisningsfunn('F1: BB/FH samtidig', lambda: m_fh.alternativ('A', p_fh, 7))
    avvisningsfunn('F1: BB utenfor horisonten', lambda: m.alternativ('A', plain, 5))

    # Ingen bytter, FT opp til fem; FH bevarer lageret uten +1 (avtalt lokal antakelse).
    mzero = Motor(u, copy.deepcopy(pr), ft=4, bb_runder=[], fh_runder=[])
    mzero.M[:] = 0
    mzero.fh_runder = [7, 8]
    pzero = mzero.bane(u.ORIG, fh=7)
    assert [(r['FT_for'], r['FT_etter']) for r in pzero['rows']] == [(4, 5), (5, 5), (5, 5), (5, 5)]
    mzero.ft = 1
    pzero = mzero.bane(u.ORIG, fh=7)
    assert [(r['FT_for'], r['FT_etter']) for r in pzero['rows']] == [(1, 2), (2, 2), (2, 3), (3, 4)]
    logg('FT: +1, tak fem og lokal FH-antakelse', 'OK', FT=[(r['FT_for'], r['FT_etter']) for r in pzero['rows']])
    for ft in [6, -1, 1.9]:
        avvisningsfunn('F2: ugyldig FT i Motor',
                       lambda: Motor(u, pr, ft=ft, bb_runder=[], fh_runder=[]).bane(u.ORIG), input=ft)
    for ft in [6, -1, 1.9]:
        avvisningsfunn('F2: ugyldig gratisbytter i CLI-validator',
                       lambda: kjor.kontroller_oppsett(dict(runde=6, gratisbytter=ft)), input=ft)

    # Salgsrabatt brukes, re-kjøp koster markedspris, ulovlig klubb/posisjon/budsjett stopper.
    ps = m.pools(m.BLEND, [0], np.ones(u.N, dtype=bool))
    nn = m.neighbors(u.ORIG, ps, u.SALES, u.budsjett)
    dest = nn[0]
    out, inc = (set(u.ORIG) - set(dest)).pop(), (set(dest) - set(u.ORIG)).pop()
    sv = u.SALES.copy()
    sv[out] -= 3
    _, sv2, cash = m.transact(u.ORIG, dest, sv, u.bank)
    assert cash == u.bank + sv[out] - u.COST[inc] and sv2[out] == u.COST[out]
    _, _, cash2 = m.transact(dest, u.ORIG, sv2, cash)
    assert cash2 == u.bank - 3
    feil(lambda: m.transact(u.ORIG, dest, sv, -1000))
    feil(lambda: m.legal(u.ORIG[:-1]))
    feil(lambda: m.legal(m.ordered(set(u.ORIG) - {int(u.ORIG[0])} | {u.ix[syntetisk.pid(1, 3)]})))
    clubs = copy.deepcopy(m)
    clubs.TEAM[dest] = 1
    feil(lambda: clubs.legal(dest))
    # To nye spillere fra samme klubb og posisjon som selges: enkel lovlig plan med to bytter.
    changes = []
    for i in u.ORIG:
        for j in pr.UI:
            if j not in u.ORIG and u.TEAM[j] == u.TEAM[i] and u.POS[j] == u.POS[i]:
                changes.append((int(i), int(j)))
                break
    pair = changes[:2]
    new = m.ordered((set(u.ORIG) - {a for a, b in pair}) | {b for a, b in pair})
    bp = m.bane(new, ft0=1)
    assert bp['rows'][0]['trekk'] == 4 and bp['rows'][0]['FT_etter'] == 1
    sens = m.ft_folsomhet({'A': u.ORIG, 'C': new}, None, None, [1, 2, 3])
    assert [r['poengtrekk_runde'] for r in sens if r['alternativ'] == 'C'] == [4, 0, 0]
    assert [r['FT'] for r in sens] == [1, 1, 2, 2, 3, 3]
    logg('Salgspris, gjenkjøp, budsjett, 2/5/5/3, klubbgrense, trekk og FT-følsomhet', 'OK')

    # CLI-testdata er ekte filer i kontrollmappen, ikke endringer i noen gwNN.
    w = skriv_uke(u, 'syntetisk-uke')
    o = dict(runde=6, horisont_til=9, gratisbytter=2, chips={'BB': [], 'FH': []}, maks_bytter=0, skadesim={'trekk': 0})
    avvisningsfunn('F3: eksplisitt manglende overstyringsfil',
                   lambda: kj(w, dict(o, overstyringer='claude/finnes-ikke.csv'), bare_poeng=True))
    avvisningsfunn('F4: WC og TC i chips',
                   lambda: kj(w, dict(o, chips={'BB': [], 'FH': [], 'WC': [6], 'TC': [6]})))
    avvisningsfunn('F1: full kjøring med BB/FH-kollisjon',
                   lambda: kj(w, dict(o, felles_chip={'BB': 7, 'FH': 7})))
    kj(w, o, bare_poeng=True)

    # Dokumentert frysing av prognosen skjer ikke, og ny kjøring erstatter filen.
    before = hashlib.sha256((w / 'motor/spillerpoeng.csv').read_bytes()).hexdigest()
    skriv_csv(w / 'claude/minutter_overstyring.csv', [rad(p, faktor=0)])
    kj(w, o, bare_poeng=True)
    after = hashlib.sha256((w / 'motor/spillerpoeng.csv').read_bytes()).hexdigest()
    assert before != after and not list(w.rglob('SHA256SUMS'))
    logg('F5: frysing delegert til prognoseskriptet i README', 'AKSEPTERT', hash_for=before, hash_etter=after)
    (w / 'claude/minutter_overstyring.csv').unlink()  # senere rundeeksempler bruker en ren uke

    # --frys via CLI: kildefilene leses bare; målet ligger i kontrollmappen.
    frys_repo, freeze = frys_fixture()
    cmd = [sys.executable, str(MOTOR / 'kjor.py'), str(freeze), '--frys']
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    hashes = {fn: hashlib.sha256((freeze / 'motor/input' / fn).read_bytes()).hexdigest() for fn in kjor.FRYSES}
    assert hashes == {fn: hashlib.sha256((frys_repo / 'data/derived' / fn).read_bytes()).hexdigest() for fn in kjor.FRYSES}
    proc2 = subprocess.run(cmd, capture_output=True, text=True)
    assert proc2.returncode != 0 and 'overskriver ikke' in proc2.stderr
    logg('CLI --frys: riktige bytes og nekter overskriving', 'OK')
    # --bare-poeng med standard utmappe og bank. File-listen utenfor motor endres ikke.
    skriv_json(w / 'motor/oppsett.json', o)
    protected = {str(f.relative_to(w)): hashlib.sha256(f.read_bytes()).hexdigest()
                 for f in w.rglob('*') if f.is_file() and 'motor' not in f.relative_to(w).parts}
    proc = subprocess.run([sys.executable, str(MOTOR / 'kjor.py'), str(w), '--bare-poeng'], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    after_files = {str(f.relative_to(w)): hashlib.sha256(f.read_bytes()).hexdigest()
                   for f in w.rglob('*') if f.is_file() and 'motor' not in f.relative_to(w).parts}
    assert protected == after_files
    assert les_json(w / 'motor/kontroll.json')['bank'] == u.bank / 10
    logg('CLI --bare-poeng, standard bank og bare skriving i motor/', 'OK')

    # Full CLI, eget alternativ og FT-følsomhet.
    outids, inids = [u.ids[a] for a, b in pair], [u.ids[b] for a, b in pair]
    full_o = dict(o, alternativer=[{'navn': 'Claude_test', 'ut': outids, 'inn': inids}], ft_folsomhet=[1, 2, 3])
    skriv_json(w / 'motor/oppsett.json', full_o)
    proc = subprocess.run([sys.executable, str(MOTOR / 'kjor.py'), str(w)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert len(les_csv(w / 'motor/ft_folsomhet.csv')) == 6
    assert {r['alternativ'] for r in les_csv(w / 'motor/alternativer_felles.csv')} == {'A', 'Claude_test'}
    assert les_json(w / 'motor/kontroll.json')['status'] == 'OK'
    logg('CLI full, Claudes eget alternativ og ft_folsomhet', 'OK')

    # Simulering er bestilt, men hoppes over når BB er brukt opp.
    try:
        sim = kj(w, dict(o, skadesim={'trekk': 2, 'rater': [.02]}))
    except (ValueError, AssertionError) as e:
        logg('F6: bestilt skadesim uten BB avvises uttrykkelig', 'RETTET', melding=str(e))
    else:
        gjort = 'skadesim' in sim['kontroll'] and (w / 'motor/skadesim.csv').exists()
        logg('F6: bestilt skadesim uten BB', 'RETTET' if gjort else 'GJENSTÅR',
             status=sim['kontroll']['status'], simulert=gjort)

    # Standard horisonter og eksplisitt krysning av chipvinduet.
    for g, slutt in [(12, 19), (19, 19), (20, 29), (35, 38)]:
        defaults = dict(runde=g, gratisbytter=2)
        res = kj(w, defaults, bare_poeng=True)
        assert res['uke'].slutt == slutt
    avvisningsfunn('F7: CLI horisont over R19/R20',
                   lambda: kj(w, dict(runde=19, horisont_til=20, gratisbytter=2), bare_poeng=True))
    assert Motor(u, pr).fh_start == 7 and Motor(u, pr, fh_runder=[]).fh_start is None
    avvisningsfunn('F1: fh_start uten tilgjengelig FH',
                   lambda: Motor(u, pr, fh_runder=[], fh_start=7).standardanalyse(maks_bytter=0, logg=lambda s: None))
    logg('Standard horisont R12/R19/R20/R35 og fh_start', 'OK', horisonter=[19, 19, 29, 38])

    # Manglende repo-rader gir fallback uten å telles som manglende.
    b = copy.deepcopy(u)
    b.repo = []
    rp = poeng.prognose(b, md)
    assert np.array_equal(rp.REPO, rp.XP) and rp.repo_mangler == 0
    logg('Repo-fallback ved manglende rader (arvet og tillatt)', 'OK', repo_mangler=rp.repo_mangler, antall_rader=0)

    # Forhåndsregistreringen sa første 20 skadeverdener, eksisterende test tar bare 10.
    gu = Uke.fra_mappe(ROT / 'samarbeid/gw10', 10, 19, input_mappe=ROT / 'samarbeid/gw10/codex/input')
    gmd, _ = poeng.lag_minutter(gu, minuttabell=ROT / 'samarbeid/gw10/codex/minutter_antatt.csv')
    gm = Motor(gu, poeng.prognose(gu, gmd), ft=2, fh_start=16, tmp=UT / 'tmp')
    r1 = les_json(ROT / 'samarbeid/gw10/codex/planer.json')
    squads = {k: gm.ordered(gu.ix[p] for p in r1['hoved'][k]['rows'][0]['tropp']) for k in 'AB'}
    trials, _, _ = skadesim.simuler(gm, squads, 12, 13, rater=(.02,), trekk=20)
    gold = {(int(r['verden']), r['alternativ']): r for r in les_csv(ROT / 'samarbeid/gw10/codex/skadetrekk_r2.csv') if float(r['p']) == .02}
    err = max(abs(r[s] - float(gold[r['verden'], r['alternativ']][s])) for r in trials for s in ['codex', 'repo_hybrid'])
    assert err <= .05
    logg('Første 20 skadeverdener mot GW10 r2', 'OK', maks_avvik=err)
    logg('Kontrollskript ferdig', 'OK', sekunder=round(time.monotonic() - start, 2))


if __name__ == '__main__':
    main()
