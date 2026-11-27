"""Akseptansetester: motoren skal gjenskape tallene Codex leverte for runde 10 (plan-v2.md del B, punkt 1-5).

Fasit er filene i samarbeid/gw10/codex/. Grense: 0,05 poeng for lagtall, 0,000001 for spillerpoeng.
"""
import numpy as np
import pytest

from conftest import GW10, MOTOR
from uke import les_csv, les_json

C = GW10 / 'codex'
# (motorens kolonne, kolonnen i gw10-filene)
KOL = [('codex_runde', 'codex_R10'), ('codex_4r', 'codex_R10_R13'), ('codex_horisont', 'codex_R10_R19'),
       ('repo_hybrid_runde', 'repo_hybrid_R10'), ('repo_hybrid_4r', 'repo_hybrid_R10_R13'),
       ('repo_hybrid_horisont', 'repo_hybrid_R10_R19'), ('modellspredning', 'modellspredning_R10_R19'),
       ('poengtrekk_runde', 'poengtrekk_R10'), ('poengtrekk_totalt', 'poengtrekk_totalt'), ('bank_etter', 'bank_etter')]
GRENSE = .05


def sammenlign(rad, fasit):
    assert str(rad['BB']) == fasit['BB'] and str(rad['FH']) == fasit['FH'], rad['alternativ']
    assert set(rad['ut'].split(', ')) == set(fasit['ut'].split(', ')), rad['alternativ']
    assert set(rad['inn'].split(', ')) == set(fasit['inn'].split(', ')), rad['alternativ']
    return max(abs(float(rad[a]) - float(fasit[b])) for a, b in KOL)


def test_inndata_stemmer(gw10):
    u = gw10[0]
    u.kontroller_input()
    u.kontroller_tropp()
    assert (u.N, u.bank, u.budsjett, u.sesong) == (670, 4, 995, '2026/27')
    assert u.sc['goals_scored']['GKP'] == 10


def test_spillerpoeng(gw10):
    u, md, pr, m = gw10
    feil = n = 0
    for fn in ['spillerpoeng.csv', 'spillerpoeng_R18_R19.csv']:
        for r in les_csv(C / fn):
            i, t = u.ix[int(r['id'])], int(r['gw']) - 10
            feil = max(feil, abs(float(r['codex']) - pr.XP[i, t]), abs(float(r['repo_hybrid']) - pr.REPO[i, t]))
            n += 1
    assert n == 670 * 10 and feil < 1e-6


def test_p_spiller_og_lagstyrke(gw10):
    u, md, pr, m = gw10
    assert max(abs(float(r['p_play']) - pr.PP[u.ix[int(r['id'])], int(r['gw']) - 10]) for r in les_csv(C / 'p_play.csv')) < 1e-9
    lag = {v: k for k, v in u.T.items()}
    for r in les_csv(C / 'lagstyrke.csv'):
        a, f = pr.strength[lag[r['lag']]]
        assert abs(a - float(r['angrep'])) < 1e-9 and abs(f - float(r['forsvar'])) < 1e-9


def test_minuttabell_fra_overstyringer(gw10):
    """Grunntabell + overstyringsfil = Codex' minutter_antatt.csv, eksakt."""
    import poeng
    u, md, pr, m = gw10
    md2, retur = poeng.lag_minutter(u, overstyringer=MOTOR / 'tester' / 'gw10_overstyring.csv')
    assert not retur
    assert all(md[k][:2] == md2[k][:2] for k in md)


def test_alternativer_r2(gw10):
    """Fem planer med felles BB12/FH13 (Codex' runde 2)."""
    u, md, pr, m = gw10
    fasit = {r['alternativ']: r for r in les_csv(C / 'alternativer_r2.csv')}
    r1 = les_json(C / 'planer.json')
    tropper = {k: m.ordered(u.ix[p] for p in r1['hoved'][k]['rows'][0]['tropp']) for k in 'ABC'}
    tropper['Claude_Iwobi'] = m.tropp_etter(['Dasilva', 'Ødegaard'], ['Van Hecke', 'Iwobi'])
    tropper['Claude_Evanilson'] = m.tropp_etter(['Dasilva', 'Isak'], ['Evanilson', 'Van Hecke'])
    planer, rader = m.faste_planer(tropper, 12, 13)
    assert len(rader) == len(fasit) == 5
    for r in rader:
        assert sammenlign(r, fasit[r['alternativ']]) <= GRENSE, r['alternativ']
    assert max(m.kontroller_bane(p) for p in planer.values()) < 1e-9


def test_alternativer_r1(gw10, gw10_standard):
    """Hele standardanalysen: søk, rutenett, A-D, E (BB-runder), F (FH-runder), G (kapteiner)."""
    res = gw10_standard
    fasit = les_csv(C / 'alternativer.csv')
    egne = {r['alternativ']: r for r in res['alternativer']}
    assert set(egne) == {r['alternativ'] for r in fasit} and len(fasit) == 29
    for f in fasit:
        if f['alternativ'].startswith('G_'):
            # gw10 oppdaterte ikke modellspredningen etter kapteinsendringen (arvet feil, funnet av Codex 19. nov).
            f = dict(f, modellspredning_R10_R19=str(abs(float(f['codex_R10_R19']) - float(f['repo_hybrid_R10_R19']))))
        assert sammenlign(egne[f['alternativ']], f) <= GRENSE, f['alternativ']
    assert (res['valg'], res['bb'], res['fh']) == ('B', 12, 13)


def test_chiprutenett_og_kapteiner(gw10_standard):
    res = gw10_standard
    fasit = {(r['bytter'], r['FH'], r['BB']): r for r in les_csv(C / 'chiprutenett.csv')}
    assert len(fasit) == len(res['rutenett'])
    for r in res['rutenett']:
        f = fasit[str(r['bytter']), str(r['FH']), str(r['BB'])]
        assert abs(r['codex'] - float(f['codex'])) <= GRENSE and abs(r['repo_hybrid'] - float(f['repo_hybrid'])) <= GRENSE
    kap = les_csv(C / 'kapteiner.csv')
    assert [k['navn'] for k in res['kapteiner']] == [k['navn'] for k in kap]
    for a, f in zip(res['kapteiner'], kap):
        assert a['vise'] == f['vice']
        assert abs(a['ekstrakopi_codex'] - float(f['ekstrakopi_codex'])) < 1e-6
        assert abs(a['ekstrakopi_repo'] - float(f['ekstrakopi_repo'])) < 1e-6


def test_skadesim_forste_verdener(gw10):
    """De 10 første skadeverdenene ved 2 % for A og B mot Codex' skadetrekk_r2.csv."""
    import skadesim
    u, md, pr, m = gw10
    r1 = les_json(C / 'planer.json')
    tropper = {k: m.ordered(u.ix[p] for p in r1['hoved'][k]['rows'][0]['tropp']) for k in 'AB'}
    trekk, sim, par = skadesim.simuler(m, tropper, 12, 13, rater=(.02,), trekk=10)
    fasit = {(r['verden'], r['alternativ']): r for r in les_csv(C / 'skadetrekk_r2.csv') if float(r['p']) == .02}
    for r in trekk:
        f = fasit[str(r['verden']), r['alternativ']]
        assert abs(r['codex'] - float(f['codex'])) <= GRENSE and abs(r['repo_hybrid'] - float(f['repo_hybrid'])) <= GRENSE


@pytest.mark.langsom
def test_skadeintervall_r1(gw10, gw10_standard):
    """skade_p10_blend / skade_p90_blend i alternativer.csv: 100 verdener ved 2 % for A-D4 (ca. 3 minutter)."""
    import skadesim
    u, md, pr, m = gw10
    res = gw10_standard
    tropper = {m.etikett(n): s for n, s in res['valgt'].items()}
    raa = skadesim.simuler_raa(m, tropper, res['fh'], .02, 100, 7089878)
    fasit = {r['alternativ']: r for r in les_csv(C / 'alternativer.csv')}
    for k, a in raa.items():
        bb = m.velg_bb(res['planer'][k])
        blend = a[:, bb - 10, :].mean(axis=1)
        assert abs(np.quantile(blend, .1) - float(fasit[k]['skade_p10_blend'])) <= GRENSE, k
        assert abs(np.quantile(blend, .9) - float(fasit[k]['skade_p90_blend'])) <= GRENSE, k


@pytest.mark.langsom
def test_kommandolinjen_ende_til_ende(tmp_path):
    """kjor.py med gw10-oppsettet: filene skrives, og alternativer_felles.csv = Codex' alternativer_r2.csv."""
    import kjor
    if not (GW10 / 'data' / 'element_summary').exists():
        pytest.skip('element_summary mangler')
    res = kjor.kjor(GW10, ut=tmp_path, oppsett=les_json(MOTOR / 'tester' / 'gw10_oppsett.json'), logg=lambda s: None)
    for fn in ['spillerpoeng.csv', 'minutter.csv', 'alternativer.csv', 'alternativer_felles.csv', 'chiprutenett.csv',
               'kapteiner.csv', 'planer.json', 'skadesim.csv', 'parvise.csv', 'skadetrekk.csv', 'kontroll.json']:
        assert (tmp_path / fn).stat().st_size > 0, fn
    fasit = {r['alternativ']: r for r in les_csv(C / 'alternativer_r2.csv')}
    egne = {r['alternativ']: r for r in les_csv(tmp_path / 'alternativer_felles.csv')}
    for k in ['A', 'B', 'C', 'Claude_Iwobi', 'Claude_Evanilson']:
        assert sammenlign(egne[k], fasit[k]) <= GRENSE, k
    k = les_json(tmp_path / 'kontroll.json')
    assert k['status'] == 'OK' and (k['valg'], k['BB'], k['FH']) == ('B', 12, 13)
    assert k['dobbeltrunder'] == [] and k['blanke_runder'] == []
    assert len(les_csv(tmp_path / 'spillerpoeng.csv')) == 6700
    assert not list(GW10.glob('motor/*'))        # ingenting skrevet i ukemappen
