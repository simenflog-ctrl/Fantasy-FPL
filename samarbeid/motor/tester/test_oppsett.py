"""Oppsett og chiplogikk: motoren skal stoppe med en tydelig feil i stedet for å regne feil uten å si fra.

Tilfellene er de Codex fant i kontrollene 19. og 21. november 2026 (`samarbeid/modell/codex/motorkontroll.md`,
funn F1-F12).
"""
import json

import numpy as np
import pytest

import kjor
import poeng
import skadesim
import syntetisk
from conftest import MOTOR
from motor import Motor
from uke import les_csv, les_json, skriv_csv, skriv_json

GYLDIG = les_json(MOTOR / 'tester' / 'gw10_oppsett.json')


def med(**endring):
    o = json.loads(json.dumps(GYLDIG))
    o.update(endring)
    return o


def test_gyldig_oppsett_godtas():
    kjor.kontroller_oppsett(GYLDIG)


@pytest.mark.parametrize('o, tekst', [
    (med(chips={'BB': [12], 'FH': [13], 'WC': [14]}), 'støttes ikke'),
    (med(chips={'BB': [12], 'FH': [13], 'TC': [12]}), 'støttes ikke'),
    (med(horisont_til=20), 'horisont_til'),
    (med(horisont_til=9), 'horisont_til'),
    (med(felles_chip={'BB': 13, 'FH': 13}), 'samme runde'),
    (med(felles_chip={'BB': 9, 'FH': 13}), 'ikke blant chips BB'),
    (med(felles_chip={'BB': 12, 'FH': 10}), 'ikke blant chips FH'),
    (med(chips={'BB': [12], 'FH': [10, 13]}), 'inneværende runde'),
    (med(gratisbytter=6), 'gratisbytter'),
])
def test_ugyldig_oppsett_stoppes(o, tekst):
    with pytest.raises(ValueError, match=tekst):
        kjor.kontroller_oppsett(o)


def test_mangler_paakrevd_felt():
    o = dict(GYLDIG)
    del o['gratisbytter']
    with pytest.raises(ValueError, match='gratisbytter'):
        kjor.kontroller_oppsett(o)


def test_oppgitt_overstyringsfil_som_mangler(tmp_path):
    with pytest.raises(ValueError, match='finnes ikke'):
        kjor.kontroller_oppsett(med(overstyringer='claude/finnes_ikke.csv'), tmp_path)
    (tmp_path / 'claude').mkdir()
    (tmp_path / 'claude' / 'finnes.csv').write_text('id,lag,gw_fra,gw_til,faktor,p_start,forventede_min,kilde\n')
    kjor.kontroller_oppsett(med(overstyringer='claude/finnes.csv'), tmp_path)


@pytest.fixture(scope='module')
def liga():
    u = syntetisk.bygg()
    md, _ = poeng.lag_minutter(u)
    return u, poeng.prognose(u, md)


def test_bench_boost_i_free_hit_runden_avvises(liga):
    u, pr = liga
    m = Motor(u, pr, ft=2, bb_runder=[7, 8], fh_runder=[7, 8])
    with pytest.raises(AssertionError, match='Free Hit i runde 9'):
        m.faste_planer({'A': u.ORIG}, 8, 9)
    m.lag_maler()
    p = m.bane(u.ORIG, fh=7, full=True)
    m.alternativ('ok', p, 8)
    with pytest.raises(AssertionError, match='samme runde'):
        m.alternativ('feil', p, 7)
    with pytest.raises(AssertionError, match='ikke tilgjengelig'):
        m.alternativ('feil', p, 9)


def test_kapteinsrader_har_riktig_modellspredning(liga):
    u, pr = liga
    m = Motor(u, pr, ft=1)
    res = m.standardanalyse(maks_bytter=1, logg=lambda s: None)
    g = [r for r in res['alternativer'] if r['gruppe'] == 'G']
    assert g
    for r in g:
        assert r['modellspredning'] == pytest.approx(abs(r['codex_horisont'] - r['repo_hybrid_horisont']), abs=1e-12)


# ------------------------------------------------- Codex' kontroll 21. november: F1, F2, F3, F6, F7, F9, F11, F12

def rad(p='', lag='', fra=6, til=6, **kw):
    """Én rad i en overstyringsfil for den syntetiske ligaen (horisont 6-9)."""
    r = dict(id=str(p), lag=lag, gw_fra=str(fra), gw_til=str(til), faktor='', p_start='', forventede_min='', kilde='test')
    r.update({k: str(v) for k, v in kw.items()})
    return r


@pytest.mark.parametrize('o, tekst', [
    (med(gratisbytter=1.9), 'gratisbytter'),                                     # F2: ble før regnet som 1
    (med(gratisbytter=-1), 'gratisbytter'),
    (med(ft_folsomhet=[-1]), 'ft_folsomhet'),                                     # F2: ga fire minuspoeng ved rull
    (med(ft_folsomhet=[6]), 'ft_folsomhet'),
    (med(vekt_codex=2), 'vekt_codex'),                                            # F2: ga 2 x codex - repo
    (med(fh_start=10), 'fh_start'),                                               # F1: FH i inneværende runde
    (med(fh_start=13, chips={'BB': [12], 'FH': []}, felles_chip={'BB': 12}), 'fh_start'),   # F1: FH ikke tilgjengelig
    (med(chips={'BB': [12, 20], 'FH': [13, 16]}), 'chips BB'),                    # runde utenfor chipvinduet
    (med(horisont_til=17, chips={'BB': [12, 18], 'FH': [13, 16]}), 'chips BB'),   # F7 (23. nov): etter horisonten
    (med(maks_bytter=-1), 'maks_bytter'),
    (med(skadesim={'trekk': 1.5}), 'trekk'),
    (med(skadesim={'trekk': 2, 'rater': [0]}), 'rater'),
])
def test_ugyldige_tall_stoppes(o, tekst):
    with pytest.raises(ValueError, match=tekst):
        kjor.kontroller_oppsett(o)


def test_motor_avviser_ugyldige_tall_og_chips(liga):
    """F1 og F2 ved direkte bruk av Motor, ikke bare gjennom kjor.py."""
    u, pr = liga
    for ft in (6, -1, 1.9):
        with pytest.raises(AssertionError, match='Gratisbytter'):
            Motor(u, pr, ft=ft)
    with pytest.raises(AssertionError, match='Vekten'):
        Motor(u, pr, vekt=2)
    with pytest.raises(AssertionError, match='fh_start'):
        Motor(u, pr, bb_runder=[], fh_runder=[], fh_start=7)
    m = Motor(u, pr, ft=2, bb_runder=[], fh_runder=[])
    with pytest.raises(AssertionError, match='ikke tilgjengelig'):
        m.bane(u.ORIG, fh=7)
    with pytest.raises(AssertionError, match='ikke tilgjengelig'):
        m.ft_folsomhet({'A': u.ORIG}, None, 7, [2])
    with pytest.raises(AssertionError, match='Gratisbytter'):
        m.ft_folsomhet({'A': u.ORIG}, None, None, [-1])
    # F7 (23. nov): oppgitte chiprunder utenfor horisonten 6-9 ble filtrert bort uten melding.
    with pytest.raises(AssertionError, match='BB-runde \\[20\\] ligger utenfor horisonten'):
        Motor(u, pr, bb_runder=[20], fh_runder=[])
    with pytest.raises(AssertionError, match='FH-runde \\[10\\] ligger utenfor horisonten'):
        Motor(u, pr, bb_runder=[], fh_runder=[8, 10])


def test_motor_stopper_horisont_over_chipvinduet():
    """F7: Motor regnet BB20 fra runde 19 og BB39 fra runde 38. R20-R21 er lovlig."""
    def uke(fra, til):
        u = syntetisk.bygg(runde=fra, slutt=til, kommende={fra: [(1, 2), (3, 4), (5, 6)], til: [(2, 1), (4, 3), (6, 5)]})
        md, retur = poeng.lag_minutter(u)
        return u, poeng.prognose(u, md, retur)
    for fra, til in [(19, 20), (38, 39)]:
        u, pr = uke(fra, til)
        with pytest.raises(AssertionError, match='chipvinduet'):
            Motor(u, pr, bb_runder=[til], fh_runder=[])
    u, pr = uke(20, 21)
    Motor(u, pr, bb_runder=[20], fh_runder=[21])


@pytest.mark.parametrize('r, tekst', [
    (rad(13, fra=8, til=7, faktor=0.5), 'gw_fra'),                 # F3: omvendt intervall ble hoppet over
    (rad(13, fra='7.5', til=8, faktor=0.5), 'gw_fra'),
    (rad(13, faktor='feil tall'), 'ikke et tall'),                 # F3
    (rad(13, faktor=-1), 'endelig tall'),
    (rad(13, fra=12, til=12, faktor=0.5), 'innenfor horisonten'),
    (rad(13, fra=5, til=7, faktor=0.5), 'innenfor horisonten'),    # F3 (23. nov): runde 5 ble klippet bort
    (rad(13, fra=8, til=10, faktor=0.5), 'innenfor horisonten'),
])
def test_overstyringsrad_med_feil_stoppes(r, tekst):
    u = syntetisk.bygg()
    blocked = poeng.blokkerte(u)
    md = poeng.grunnminutter(u, poeng.roller(u), blocked)
    with pytest.raises(ValueError, match=tekst):
        poeng.bruk_overstyringer(u, md, [r], blocked)


def test_overstyringsrad_over_hele_horisonten_godtas():
    u = syntetisk.bygg()
    blocked = poeng.blokkerte(u)
    md = poeng.grunnminutter(u, poeng.roller(u), blocked)
    foer = {k: list(v) for k, v in md.items()}
    poeng.bruk_overstyringer(u, md, [rad(13, fra=6, til=9, faktor=0.5)], blocked)
    runder = [g for g in u.GWS if (13, g) in md]
    assert runder
    for g in runder:
        assert md[13, g][:2] == pytest.approx([foer[13, g][0] * 0.5, foer[13, g][1] * 0.5])


def test_minutter_uten_sannsynlighet_for_aa_spille_stoppes():
    """F9: p_start 0 og 30 minutter for en spiller uten innhopp ga poeng med P(spiller) = 0."""
    u = syntetisk.bygg()
    blocked = poeng.blokkerte(u)
    md = poeng.grunnminutter(u, poeng.roller(u), blocked)
    retur = poeng.bruk_overstyringer(u, md, [rad(13, p_start=0, forventede_min=30)], blocked)
    with pytest.raises(ValueError, match=r'P\(spiller\) = 0'):
        poeng.prognose(u, poeng.avrund(md), retur)


def test_frossen_minuttabell_beholder_kjent_retur(tmp_path):
    """F12: en spiller som er ute med kjent returdato, får de samme poengene når minutter.csv leses inn igjen."""
    u = syntetisk.bygg()
    p = syntetisk.pid(1, 2)
    u.E[p]['status'] = 'i'
    u.E[p]['chance_of_playing_next_round'] = 0
    blocked = poeng.blokkerte(u)
    md = poeng.grunnminutter(u, poeng.roller(u), blocked)
    retur = poeng.bruk_overstyringer(u, md, [rad(p, fra=7, til=9, p_start=.8, forventede_min=70)], blocked)
    md = poeng.avrund(md)
    for_ = poeng.prognose(u, md, retur)
    poeng.skriv_minutter(u, md, tmp_path / 'minutter.csv', retur)
    md2, retur2 = poeng.lag_minutter(u, minuttabell=tmp_path / 'minutter.csv')
    etter = poeng.prognose(u, md2, retur2)
    assert md2 == md and retur2 == retur and for_.XP[u.ix[p], 1] > 0
    for a, b in [(for_.XP, etter.XP), (for_.REPO, etter.REPO), (for_.PP, etter.PP)]:
        assert np.array_equal(a, b)


def test_skadesim_uten_bench_boost(liga):
    """F6: uten tilgjengelig BB sammenlignes totalene uten BB (før ble simuleringen hoppet over uten melding)."""
    u, pr = liga
    m = Motor(u, pr, ft=1, bb_runder=[], fh_runder=[8])
    trekk, sim, par = skadesim.simuler(m, {'A': u.ORIG}, None, 8, rater=(.02,), trekk=3)
    assert len(trekk) == 3 and {r['BB'] for r in trekk} == {''}
    U, D = skadesim.trekk_verdener(m.N, m.H, 3, 7089878)
    for d, r in enumerate(trekk):
        v = m.bane(u.ORIG, fh=8, world=skadesim.verden(U[d], D[d], .02), record=False)['total_uten_BB']
        assert r['codex'] == pytest.approx(v[0]) and r['repo_hybrid'] == pytest.approx(v[1])


def test_rutenett_for_egne_er_samme_regning_som_standardrutenettet(liga):
    """F11: egne alternativer får sitt eget chiprutenett, regnet som standardrutenettet."""
    u, pr = liga
    m = Motor(u, pr, ft=1, bb_runder=[6, 8], fh_runder=[7, 9])
    res = m.standardanalyse(maks_bytter=0, logg=lambda s: None)
    egne = m.rutenett_for({'A': u.ORIG})
    std = [r for r in res['rutenett'] if r['bytter'] == 0]
    assert len(egne) == len(std) == 4
    for a, b in zip(egne, std):
        assert (a['alternativ'], a['FH'], a['BB']) == ('A', b['FH'], b['BB'])
        assert a['codex'] == pytest.approx(b['codex']) and a['repo_hybrid'] == pytest.approx(b['repo_hybrid'])


def skriv_uke(u, w):
    """Ukemappe på disk for den syntetiske ligaen, som kjor.kjor kan lese."""
    (w / 'data' / 'element_summary').mkdir(parents=True)
    (w / 'motor' / 'input').mkdir(parents=True)
    for fn, obj in [('bootstrap', u.b), ('fixtures', u.fx), ('entry', {'last_deadline_bank': u.bank}),
                    ('salgspriser', [dict(id=p, salgspris=int(u.SALES[u.ix[p]]) / 10) for p in u.orig])]:
        skriv_json(w / 'data' / (fn + '.json'), obj)
    for p, h in u.history.items():
        skriv_json(w / 'data' / 'element_summary' / ('%d.json' % p), h)
    skriv_csv(w / 'motor' / 'input' / 'player_matches.csv', u.pm)
    skriv_csv(w / 'motor' / 'input' / 'expected_points.csv', u.repo)
    return w


def test_kjoring_uten_bench_boost_med_eget_alternativ(tmp_path):
    """F6, F11 og F12 gjennom hele kjor.kjor: BB brukt, FH igjen, ett eget alternativ (slik R12 ser ut)."""
    w = skriv_uke(syntetisk.bygg(), tmp_path / 'uke')
    o = dict(runde=6, horisont_til=9, gratisbytter=1, chips={'BB': [], 'FH': [8, 9]}, maks_bytter=1,
             alternativer=[dict(navn='Claude_test', ut=[3], inn=[4])], ft_folsomhet=[2],
             skadesim=dict(trekk=2, rater=[.02]))
    k = kjor.kjor(w, oppsett=o, logg=lambda s: None)['kontroll']
    assert k['status'] == 'OK' and k['felles_BB'] is None and k['felles_FH'] in (8, 9)
    assert k['skadesim'] == dict(trekk=2, rater=[.02], BB=None, FH=k['felles_FH'])
    assert len(les_csv(w / 'motor' / 'skadetrekk.csv')) == 2 * len(k['alternativer'])
    egne = les_csv(w / 'motor' / 'chiprutenett_egne.csv')
    assert {r['alternativ'] for r in egne} == {'Claude_test'} and {r['FH'] for r in egne} == {'8', '9'}
    assert 'retur' in les_csv(w / 'motor' / 'minutter.csv')[0]
