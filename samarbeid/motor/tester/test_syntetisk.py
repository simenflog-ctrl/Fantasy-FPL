"""Syntetiske tester (plan-v2.md del B, punkt 6): dobbeltrunder, blanke runder, autobytter, Bench Boost, kaptein.

gw10 hadde verken dobbeltrunde eller blank runde i horisonten, så denne logikken er ikke dekket av akseptansetestene.
"""
import numpy as np
import pytest

import poeng
import syntetisk
from fasit_autobytter import forventet
from lag import LUT, PERMS, evaluate_selection, select
from motor import Motor
from syntetisk import pid

R6, R7, R8, R9 = 0, 1, 2, 3     # kolonner i horisonten


@pytest.fixture(scope='module')
def liga():
    u = syntetisk.bygg()
    u.kontroller_input()
    u.kontroller_tropp()
    md, _ = poeng.lag_minutter(u)
    pr = poeng.prognose(u, md)
    return u, md, pr


def test_dobbeltrunde_teller_to_ganger(liga):
    u, md, pr = liga
    for j in range(15):
        i = u.ix[pid(1, j)]                       # lag 1: samme kamp én gang i R6 og to ganger i R7
        assert pr.XP[i, R6] > 0 or md[pid(1, j), 6][1] == 0
        assert pr.XP[i, R7] == pytest.approx(2 * pr.XP[i, R6], abs=1e-12)
        assert pr.BONUS[i, R7] == pytest.approx(2 * pr.BONUS[i, R6], abs=1e-12)
        assert pr.PP[i, R7] == pytest.approx(1 - (1 - pr.PP[i, R6]) ** 2, abs=1e-12)
    i = u.ix[pid(3, 2)]                           # lag 3 har én kamp i begge rundene (hjemme mot lag 4)
    assert pr.XP[i, R7] == pytest.approx(pr.XP[i, R6], abs=1e-12)


def test_blank_runde_gir_null(liga):
    u, md, pr = liga
    for lag in (5, 6):
        for j in range(15):
            i = u.ix[pid(lag, j)]
            assert pr.XP[i, R7] == 0 and pr.REPO[i, R7] == 0 and pr.PP[i, R7] == 0
            assert pr.XP[i, R6] > 0 or md[pid(lag, j), 6][1] == 0
    assert pr.repo_mangler == 0


def test_repo_hybrid_summerer_dobbeltrunde(liga):
    u, md, pr = liga
    p = pid(1, 2)                                 # startende forsvarer på lag 1
    raa, gamle_min = 2 + (p % 7) * .5, 80
    assert pr.REPO[u.ix[p], R6] == pytest.approx(raa * md[p, 6][1] / gamle_min, abs=1e-12)
    assert pr.REPO[u.ix[p], R7] == pytest.approx(2 * raa * md[p, 7][1] / gamle_min, abs=1e-12)


def test_dobbeltrunde_mot_enkeltrunde_programmet(liga):
    """Samme liga uten den andre kampen i R7: poengene for lag 1 halveres, resten er uendret."""
    u, md, pr = liga
    k = dict(syntetisk.KOMMENDE)
    k[7] = [(1, 2), (3, 4)]
    u2 = syntetisk.bygg(kommende=k)
    pr2 = poeng.prognose(u2, poeng.lag_minutter(u2)[0])
    i = u.ix[pid(1, 12)]
    assert pr.XP[i, R7] == pytest.approx(2 * pr2.XP[i, R7], abs=1e-12)
    assert np.allclose(np.delete(pr.XP, R7, axis=1), np.delete(pr2.XP, R7, axis=1), atol=1e-12)


def _mot_fasit(s, xp, pp, pos, bb=False):
    verdi, vekter, xi, benk, kap, vise = select(s, xp, pp, pos, LUT, PERMS, True, bb)
    fasit = forventet([pos[i] for i in s], [xp[i] for i in s], [pp[i] for i in s], [int(j) for j in xi],
                      [int(j) for j in benk], int(kap), int(vise), bb)
    return verdi, fasit, vekter, xi, benk, kap, vise


@pytest.mark.parametrize('runde', [R6, R7, R8])
def test_autobytter_mot_uttommende_fasit(liga, runde):
    """Motorens forventede lagpoeng = gjennomgang av alle utfall. R7 har både dobbeltrunde og blank runde i troppen."""
    u, md, pr = liga
    verdi, fasit, vekter, xi, benk, kap, vise = _mot_fasit(u.ORIG, pr.XP[:, runde], pr.PP[:, runde], u.POS)
    assert verdi == pytest.approx(fasit, abs=1e-9)


def test_autobytter_ulike_formasjoner_og_benkerekkefolger(liga):
    """Tving fram alle formasjoner og benkerekkefølger med usikre spillere, også lineups motoren ikke ville valgt."""
    u, md, pr = liga
    rng = np.random.RandomState(7)
    s, pos = u.ORIG, u.POS
    for forsok in range(6):
        xp = np.zeros(u.N)
        pp = np.ones(u.N)
        xp[s] = rng.uniform(1, 7, 15)
        pp[s] = rng.choice([0., .3, .6, .9, 1.], 15, p=[.1, .2, .3, .3, .1])
        xp[s[pp[s] == 0]] = 0
        ute = sorted(rng.choice(np.arange(2, 15), 3, replace=False))
        ant = [sum(1 for j in range(2, 15) if j not in ute and pos[s[j]] == k) for k in (2, 3, 4)]
        if ant[0] < 3 or ant[1] < 2 or ant[2] < 1:
            continue
        gk = int(rng.randint(2))
        xi = np.array([gk] + [j for j in range(2, 15) if j not in ute], dtype=np.int64)
        bn = np.array(rng.permutation(ute), dtype=np.int64)
        verdi, vekter, kap, vise = evaluate_selection(s, xi, bn, 1 - gk, xp, pp, pos, LUT, False)
        fasit = forventet([pos[i] for i in s], list(xp[s]), list(pp[s]), [int(j) for j in xi],
                          [1 - gk] + [int(j) for j in bn], int(kap), int(vise))
        assert verdi == pytest.approx(fasit, abs=1e-9), (forsok, xi, bn)


def test_startspiller_med_blank_runde_byttes_ut(liga):
    u, md, pr = liga
    s, pos = u.ORIG, u.POS
    xp = np.zeros(u.N)
    pp = np.zeros(u.N)
    xp[s] = 4.
    pp[s] = 1.
    xi = np.array([0, 2, 3, 4, 5, 7, 8, 9, 10, 12, 13], dtype=np.int64)      # 4-4-2
    bn = np.array([6, 11, 14], dtype=np.int64)                                # forsvar, midtbane, spiss
    xp[s[2]] = pp[s[2]] = 0                                                   # startende forsvarer uten kamp
    verdi, vekter, kap, vise = evaluate_selection(s, xi, bn, 1, xp, pp, pos, LUT, False)
    assert vekter[6] == 1 and vekter[11] == 0 and vekter[14] == 0             # første på benken går inn
    assert verdi == pytest.approx(11 * 4 + 4)                                 # 10 startende + innbytter + kaptein
    xp[s[0]] = pp[s[0]] = 0                                                   # startkeeper uten kamp
    verdi, vekter, kap, vise = evaluate_selection(s, xi, bn, 1, xp, pp, pos, LUT, False)
    assert vekter[1] == 1 and verdi == pytest.approx(11 * 4 + 4)


def test_tre_forsvarere_kan_ikke_erstattes_av_midtbane(liga):
    u, md, pr = liga
    s, pos = u.ORIG, u.POS
    xp = np.zeros(u.N)
    pp = np.zeros(u.N)
    xp[s] = 4.
    pp[s] = 1.
    xi = np.array([0, 2, 3, 4, 7, 8, 9, 10, 11, 12, 13], dtype=np.int64)     # 3-5-2
    bn = np.array([14, 5, 6], dtype=np.int64)                                 # spiss først, så to forsvarere
    xp[s[2]] = pp[s[2]] = 0                                                   # en av tre forsvarere uten kamp
    verdi, vekter, kap, vise = evaluate_selection(s, xi, bn, 1, xp, pp, pos, LUT, False)
    assert vekter[14] == 0 and vekter[5] == 1 and vekter[6] == 0              # spissen kan ikke gi 2 forsvarere


def test_bench_boost_teller_alle_femten(liga):
    u, md, pr = liga
    for runde in (R6, R7):
        xp, pp = pr.XP[:, runde], pr.PP[:, runde]
        verdi, fasit, vekter, xi, benk, kap, vise = _mot_fasit(u.ORIG, xp, pp, u.POS, bb=True)
        s = u.ORIG
        ekstra = max(xp[s[c]] + (1 - pp[s[c]]) * xp[s[v]] for c in range(15) for v in range(15) if c != v)
        assert verdi == pytest.approx(xp[s].sum() + ekstra, abs=1e-9)
        assert verdi == pytest.approx(fasit, abs=1e-9)


def test_visekaptein_arver_naar_kapteinen_ikke_spiller(liga):
    u, md, pr = liga
    s, pos = u.ORIG, u.POS
    xp = np.zeros(u.N)
    pp = np.zeros(u.N)
    xp[s] = 3.
    pp[s] = 1.
    xp[s[12]], pp[s[12]] = 9., .6          # klart beste kaptein, men spiller bare 60 %
    xp[s[7]] = 5.                           # beste vise
    verdi, vekter, xi, benk, kap, vise = select(s, xp, pp, pos, LUT, PERMS, True, False)
    assert (kap, vise) == (12, 7)
    assert vekter[12] == 2 and vekter[7] == pytest.approx(1 + .4)
    # En kaptein uten kamp gir null: da velges han aldri, og fasiten gir visen hele doblingen.
    assert forventet([pos[i] for i in s], [0. if j == 12 else xp[i] for j, i in enumerate(s)],
                     [0. if j == 12 else 1. for j in range(15)], [0, 2, 3, 4, 7, 8, 9, 10, 12, 13, 14],
                     [1, 5, 6, 11], 12, 7) == pytest.approx(9 * 3 + 5 + 3 + 5)   # ni startende, visen, innbytter, visens dobling


def test_eierbane_gjennom_dobbel_og_blank_runde(liga):
    u, md, pr = liga
    m = Motor(u, pr, ft=1)
    res = m.standardanalyse(maks_bytter=1, logg=lambda s: None)
    assert set(res['planer']) == {'A', 'B'} and res['fh'] in m.fh_runder
    for p in list(res['planer'].values()) + list(res['fh_planer'].values()):
        assert m.kontroller_bane(p) < 1e-9
        ft = 1
        for r in p['rows']:
            assert r['bank'] >= 0 and r['FT_for'] == ft and 1 <= r['FT_etter'] <= 5
            assert len(r['tropp']) == 15 and len(r['elleve']) == 11 and len(r['benk']) == 4
            assert min(r['bb_gevinst']) >= -1e-9
            byttet = 0 if r['chip'] == 'FH' else len(r['inn'])
            assert r['trekk'] == 4 * max(0, byttet - ft)
            ft = r['FT_etter']
            if r['chip'] == 'FH':
                assert r['permanent'] != r['tropp'] or not r['inn']
    a = res['planer']['A']
    assert a['rows'][0]['inn'] == [] and a['rows'][0]['trekk'] == 0
    # Uten Free Hit: i R7 har troppen fem spillere uten kamp. Ingen av dem kan gi poeng.
    uten = m.bane(u.ORIG, fh=None, full=True)
    r7 = uten['rows'][1]
    blanke = {pid(lag, j) for lag in (5, 6) for j in range(15)}
    assert all(v == 0 or i not in blanke for i, v in zip(r7['tropp'], r7['vekter']))
    assert m.kontroller_bane(uten) < 1e-9 and uten['FH'] is None
    # Free Hit i den blanke/doble runden skal lønne seg mot ingen Free Hit.
    med = m.bane(u.ORIG, fh=7, full=True)
    assert m.bland(m.total(med, None)) > m.bland(m.total(uten, None))
    assert not (set(med['rows'][1]['elleve']) & blanke)      # benken kan fylles med billige spillere uten kamp


def test_chip_ikke_tilgjengelig(liga):
    u, md, pr = liga
    m = Motor(u, pr, ft=2, bb_runder=[], fh_runder=[])
    res = m.standardanalyse(maks_bytter=1, logg=lambda s: None)
    assert res['fh'] is None and res['bb'] is None and res['kollisjon'] is None
    assert all(r['BB'] == '' and r['FH'] == '' for r in res['alternativer'])
    assert {r['gruppe'] for r in res['alternativer']} == {'A', 'B', 'G'}


def test_overstyringer(liga):
    u, md, pr = liga
    blocked = set()
    grunn = poeng.grunnminutter(u, pr.roles, blocked)
    p, q = pid(1, 2), pid(3, 2)
    f0, m0 = grunn[p, 6][0], grunn[p, 6][1]
    rader = [dict(id=str(p), lag='', gw_fra='6', gw_til='6', faktor='0.5', p_start='', forventede_min='', kilde='test'),
             dict(id='', lag='L3', gw_fra='7', gw_til='8', faktor='0', p_start='', forventede_min='', kilde='test'),
             dict(id=str(p), lag='', gw_fra='9', gw_til='9', faktor='', p_start='0.5', forventede_min='', kilde='test')]
    poeng.bruk_overstyringer(u, grunn, rader, blocked)
    assert grunn[p, 6][:2] == [f0 * .5, m0 * .5] and grunn[p, 7][:2] == [f0, m0]
    assert grunn[q, 7][:2] == [0, 0] and grunn[q, 8][:2] == [0, 0] and grunn[q, 6][0] > 0
    assert grunn[p, 9][0] == .5 and grunn[p, 9][1] == pytest.approx(m0 * .5 / f0)
    for darlig in [dict(rader[0], kilde=''), dict(rader[0], lag='L1'), dict(rader[0], p_start='0.4'),
                   dict(rader[0], faktor='3')]:
        with pytest.raises(ValueError):
            poeng.bruk_overstyringer(u, poeng.grunnminutter(u, pr.roles, blocked), [darlig], blocked)
