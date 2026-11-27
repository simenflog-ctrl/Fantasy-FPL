#!/usr/bin/env python3
"""Flere minimale reproduksjoner; alle utdata i motorkontroll-data/kanttilfeller.json."""
import copy
import json
from pathlib import Path
import time

import motorkontroll_eksempler as a
import numpy as np

resultat = []


def logg(navn, **kw):
    rad = dict(test=navn, **kw)
    resultat.append(rad)
    print(json.dumps(rad, ensure_ascii=False), flush=True)
    (a.UT / 'kanttilfeller.json').write_text(json.dumps(resultat, ensure_ascii=False, indent=2))


start = time.monotonic()
u, md, pr = a.liga()
m = a.Motor(u, pr, bb_runder=[], fh_runder=[], tmp=a.UT / 'tmp')

# G-radene får nye poeng uten at modellspredning oppdateres (arvet fra GW10).
res = m.standardanalyse(maks_bytter=0, logg=lambda s: None)
avvik = []
for r in res['alternativer']:
    riktig = abs(r['codex_horisont'] - r['repo_hybrid_horisont'])
    if abs(riktig - r['modellspredning']) > 1e-9:
        avvik.append(dict(alternativ=r['alternativ'], oppgitt=r['modellspredning'], riktig=riktig))
logg('F8: feil modellspredning i kapteinsalternativer (arvet)', dom='GJENSTÅR' if avvik else 'RETTET', avvik=avvik)

# Begge feltene er innenfor tillatte intervaller, men sannsynlighet 0 og poeng >0.
p = a.syntetisk.pid(1, 12)
mm = copy.deepcopy(md)
def ghost_case():
    a.poeng.bruk_overstyringer(u, mm, [a.rad(p, p_start=0, forventede_min=30)], set())
    ghost = a.poeng.prognose(u, mm)
    i = u.ix[p]
    return dict(id=p, p_spiller=float(ghost.PP[i, 0]), codex=float(ghost.XP[i, 0]), repo=float(ghost.REPO[i, 0]))

# Bruk samme klassifiserer, med denne loggen som mottaker.
a.logg = lambda navn, dom, **kw: logg(navn, dom=dom, **kw)
try:
    ghost = ghost_case()
except (ValueError, AssertionError) as e:
    logg('F9: inkonsistente minutter', dom='RETTET', melding=str(e))
else:
    ugyldig = ghost['p_spiller'] == 0 and (ghost['codex'] > 0 or ghost['repo'] > 0)
    logg('F9: inkonsistente minutter gir poeng med P(spiller)=0',
         dom='GJENSTÅR' if ugyldig else 'RETTET', **ghost)
mm = copy.deepcopy(md)
a.avvisningsfunn('F3: omvendt overstyringsintervall',
                lambda: a.poeng.bruk_overstyringer(u, mm, [a.rad(p, fra=8, til=7, faktor='feil tall')], set()))
a.avvisningsfunn('F3: delvis overlapp før horisonten avvises',
                lambda: a.poeng.bruk_overstyringer(u, copy.deepcopy(md),
                                                  [a.rad(p, fra=5, til=7, faktor=0.5)], set()),
                horisont=[u.g0, u.slutt], intervall=[5, 7])
a.avvisningsfunn('F3: delvis overlapp etter horisonten avvises',
                lambda: a.poeng.bruk_overstyringer(u, copy.deepcopy(md),
                                                  [a.rad(p, fra=u.slutt - 1, til=u.slutt + 1, faktor=0.5)], set()),
                horisont=[u.g0, u.slutt], intervall=[u.slutt - 1, u.slutt + 1])
a.avvisningsfunn('F2: vekt=2 i Motor', lambda: a.Motor(u, pr, vekt=2))
a.avvisningsfunn('F2: FT-følsomhet -1', lambda: m.ft_folsomhet({'A': u.ORIG}, None, None, [-1]),
                sjekk=lambda rr: logg('F2: trekk ved rull', trekk=rr[0]['poengtrekk_runde']))

# Bare felles-chip støtter ingen ekstra chips, men ukjente WC/TC-felter avvises ikke.
w = a.skriv_uke(u, 'kant-uke')
o = dict(runde=6, horisont_til=9, gratisbytter=2, maks_bytter=0,
         chips={'BB': [], 'FH': []}, skadesim={'trekk': 0})
a.avvisningsfunn('F4: felles_chip WC/TC', lambda: a.kj(w, dict(o, felles_chip={'WC': 6, 'TC': 6})))
for start_round, slutt in [(19, 20), (38, 39)]:
    a.avvisningsfunn('F7: full kjøring over vindu/etter sesongslutt',
                    lambda: a.kj(w, dict(o, runde=start_round, horisont_til=slutt, chips={'BB': [slutt], 'FH': []})),
                    runde=start_round, horisont_til=slutt)

# --frys: eksisterende andre fil skal stoppe før første fil kopieres.
repo, partial = a.frys_fixture()
(partial / 'motor/input').mkdir(parents=True)
(partial / 'motor/input/expected_points.csv').write_text('gammel fil\n')
try:
    a.kjor.frys(partial)
except SystemExit as e:
    melding = str(e)
else:
    raise AssertionError('Skulle nekte overskriving')
assert (partial / 'motor/input/expected_points.csv').read_text() == 'gammel fil\n'
logg('F10: --frys etterlater delvis frosset par ved feil',
     dom='GJENSTÅR' if (partial / 'motor/input/player_matches.csv').exists() else 'RETTET', melding=melding)

# Negativ test for kjøpsuniverset: alle statuser og can_select er filtrert.
bad = copy.deepcopy(u)
ids = list(bad.ids[:6])
for p, status in zip(ids[:4], ['u', 'n', 'i', 's']):
    bad.E[p]['status'] = status
bad.E[ids[4]]['chance_of_playing_next_round'] = 0
bad.E[ids[5]]['can_select'] = False
bm, ret = a.poeng.lag_minutter(bad)
bp = a.poeng.prognose(bad, bm, ret)
assert not {bad.ix[p] for p in ids}.intersection(bp.UI)
logg('Kjøpsunivers: u/n/i/s/0 prosent og can_select', dom='OK')

# Frossen minuttabell er alternativet til overstyringer; utvidet horisont utenfor Uke er tillatt.
tabell = a.UT / 'minuttabell-kontroll.csv'
a.poeng.skriv_minutter(u, md, tabell)
loaded, ret = a.poeng.lag_minutter(u, minuttabell=tabell, overstyringer='finnes-ikke')
assert loaded == md and not ret
logg('Frossen minuttabell har prioritet over overstyringer', dom='OK')

# Ufullstendig dobbeltrad/0 repo-minutter gir hele codex-runden, ikke delsummen.
p = a.syntetisk.pid(1, 2)
for variant in ['mangler_en', 'null_minutter']:
    bad = copy.deepcopy(u)
    rr = [r for r in bad.repo if r['element'] == p and r['gw'] == 7]
    if variant == 'mangler_en':
        bad.repo.remove(rr[0])
    else:
        rr[0]['exp_minutes'] = 0
    bp = a.poeng.prognose(bad, md)
    assert bp.REPO[u.ix[p], 1] == bp.XP[u.ix[p], 1] and bp.repo_mangler == 1
    logg('Repo dobbeltrunde fallback', dom='OK', variant=variant)

# R2 beregnet eget fritt chiprutenett for Claudes forslag. CLI gjør bare felles datoer.
w2 = a.skriv_uke(u, 'egne-alternativer-uke')
out_id = a.syntetisk.pid(1, 2)
in_id = a.syntetisk.pid(1, 3)
custom = dict(o, chips={'BB': [6, 8], 'FH': [7, 9]},
              alternativer=[dict(navn='Claude_test', ut=[out_id], inn=[in_id])])
rr = a.kj(w2, custom)
assert 'Claude_test' in rr['planer']
eget_grid = a.les_csv(w2 / 'motor/chiprutenett_egne.csv')
logg('F11: eget alternativ får chiprutenett', dom='RETTET' if len(eget_grid) == 4 else 'GJENSTÅR',
     felles=list(rr['planer']), eget_rutenett_celler=len(eget_grid),
     chippar=[(r['BB'], r['FH']) for r in eget_grid])

# Ny generator bruker alltid blokker på 100; den er ikke identisk med gamle vilkårlige trekkantall.
N, H, trekk, seed = 3, 4, 150, 7089878
U, D = a.skadesim.trekk_verdener(N, H, trekk, seed)
rng = np.random.default_rng(seed)
U0 = rng.random((100, H, N))
D0 = np.array([1, 2, 3, 6])[rng.integers(0, 4, size=(100, H, N))]
U1 = rng.random((trekk - 100, H, N))
D1 = np.array([1, 2, 3, 6])[rng.integers(0, 4, size=(trekk - 100, H, N))]
assert np.array_equal(U[:100], U0) and np.array_equal(D[:100], D0)
assert np.array_equal(U[100:], U1) and not np.array_equal(D[100:], D1)
logg('Skadesim: avvik fra R2 ved 150 trekk, korrekt stabil blokkregel', dom='OK',
     første_100_identiske=True, varigheter_101_150_identiske=False)

logg('Kanttilfeller ferdig', dom='OK', sekunder=round(time.monotonic() - start, 2))
