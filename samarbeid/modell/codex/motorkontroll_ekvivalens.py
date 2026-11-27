#!/usr/bin/env python3
"""Små eksempler for avvik utenfor GW10-fasiten. Ingen import av GW10-skript med skriving."""
import copy
import json
import time
import numpy as np
import motorkontroll_eksempler as a
import test_syntetisk as ts

start = time.monotonic()
resultat = []
def logg(test, dom='OK', **kw):
    row = dict(test=test, dom=dom, **kw)
    resultat.append(row)
    print(json.dumps(row, ensure_ascii=False), flush=True)
    (a.UT / 'ekvivalens.json').write_text(json.dumps(resultat, ensure_ascii=False, indent=2))

u, md, pr = a.liga()
for fn in (ts.test_dobbeltrunde_teller_to_ganger, ts.test_blank_runde_gir_null,
           ts.test_repo_hybrid_summerer_dobbeltrunde, ts.test_dobbeltrunde_mot_enkeltrunde_programmet):
    fn((u, md, pr))
    logg(fn.__name__)

# R2 har nøyaktig to blokker à 100 ved sitt draws=200.
N, H, seed = 3, 4, 7089878
U, D = a.skadesim.trekk_verdener(N, H, 200, seed)
rng = np.random.default_rng(seed)
UU, DD = [], []
for n in [100, 100]:
    UU.append(rng.random((n, H, N)))
    DD.append(np.array([1, 2, 3, 6], dtype=np.int16)[rng.integers(0, 4, size=(n, H, N))])
assert np.array_equal(U, np.concatenate(UU)) and np.array_equal(D, np.concatenate(DD))
U20, D20 = a.skadesim.trekk_verdener(N, H, 20, seed)
assert np.array_equal(U[:20], U20) and np.array_equal(D[:20], D20)
for d in range(200):
    world = np.zeros((H, N), dtype=np.int16)
    end = np.zeros(N, dtype=np.int16)
    for t in range(1, H):
        new = (end <= t) & (U[d, t] < .2)
        end[new] = t + D[d, t, new]
        world[t] = end
    assert np.array_equal(world, a.skadesim.verden(U[d], D[d], .2))
logg('R2: 200 tilfeldighetsblokker/verdener og stabilt 20-prefiks', verdener=200)

# Ny returdato er ikke dekket av GW10. Egen utmatet minuttabell skal kunne leses igjen.
b = copy.deepcopy(u)
p = a.syntetisk.pid(1, 2)
b.E[p]['status'] = 'i'
b.E[p]['chance_of_playing_next_round'] = 0
blocked = a.poeng.blokkerte(b)
mm = a.poeng.grunnminutter(b, a.poeng.roller(b), blocked)
retur = a.poeng.bruk_overstyringer(b, mm, [a.rad(p, fra=7, til=9, p_start=.8, forventede_min=70)], blocked)
mm = a.poeng.avrund(mm)
original = a.poeng.prognose(b, mm, retur)
path = a.UT / 'minutter-retur.csv'
a.poeng.skriv_minutter(b, mm, path, retur)
loaded, ret2 = a.poeng.lag_minutter(b, minuttabell=path)
replay = a.poeng.prognose(b, loaded, ret2)
assert loaded == mm and original.XP[b.ix[p], 1] > 0
lik = np.array_equal(original.XP, replay.XP) and np.array_equal(original.REPO, replay.REPO)
logg('F12: frossen minuttabell mister kjent returdato', 'RETTET' if lik else 'GJENSTÅR',
     id=p, gw=7, codex_fra_overstyring=float(original.XP[b.ix[p], 1]),
     codex_fra_frossen=float(replay.XP[b.ix[p], 1]),
     repo_fra_overstyring=float(original.REPO[b.ix[p], 1]),
     repo_fra_frossen=float(replay.REPO[b.ix[p], 1]), retur_for=len(retur), retur_etter=len(ret2))
logg('Ekvivalenseksempler ferdig', sekunder=round(time.monotonic() - start, 2))
