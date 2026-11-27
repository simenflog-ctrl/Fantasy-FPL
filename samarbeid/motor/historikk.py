#!/usr/bin/env python3
"""Historisk måling av poengsettene (plan-v2.md del C). Kravene er låst i planen; denne filen bare regner.

    python samarbeid/motor/historikk.py --cache /sti/til/data/cache/vaastav

For hver sesong 2023/24-2025/26 og runde 8-38 lages en prognose én runde fram med data til og med runden før:
  codex       : motorens egen modell (poeng.prognose), med inndata bygget fra vaastav-filene
  repo        : repoets produksjonsmodell via src/eval_engine.py (egne minutter)
  repo_hybrid : repo skalert med motorens minutter, slik ukekjøringen gjør
Ingen modellkode ligger her, bare bygging av inndata og utregning av mål.

Ikke gjenskapt (se planen): API-flagg og Claudes overstyringer (alle regnes som tilgjengelige), defensive bidrag
før 2025/26 (settes til 0 poeng), og 2023/24 har bare én tidligere sesong som prior.
Skriver til samarbeid/modell/motor/: poengsett_prediksjoner.csv.gz (ikke i git) og maling_poengsett.json.
"""
import argparse
import copy
import json
import sys
import time
from pathlib import Path

HER = Path(__file__).resolve().parent
ROT = HER.parents[1]
sys.path.insert(0, str(HER))
sys.path.insert(0, str(ROT / 'src'))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import poeng  # noqa: E402
from uke import Uke, les_json  # noqa: E402

SESONGER = ['2023-24', '2024-25', '2025-26']
UTVIKLING, KONTROLL = ['2023-24', '2024-25'], '2025-26'
ALLE = ['2022-23'] + SESONGER
VEKTER = [0., .25, .5, .75, 1.]
STATS = poeng.STATS
POSNR = {'GK': 1, 'DEF': 2, 'MID': 3, 'FWD': 4}
FORSTE, SISTE = 8, 38


def poengregler(sesong):
    sc = copy.deepcopy(les_json(HER.parent / 'gw10' / 'data' / 'bootstrap.json')['game_config']['scoring'])
    sc['goals_scored']['GKP'] = 6
    if sesong < '2025-26':
        sc['defensive_contribution'] = {k: 0 for k in sc['defensive_contribution']}
    return sc


def tidligere(navn_sesonger, sesong):
    """history_past per spillernavn: totaler fra sesongene før `sesong`, eldste først."""
    past = {}
    for s in ALLE:
        if s >= sesong:
            break
        d = navn_sesonger[s]
        tot = d.groupby('name')[['minutes'] + STATS].sum()
        for navn, r in tot.iterrows():
            rad = dict(season_name=s.replace('-', '/'), minutes=int(r['minutes']))
            rad.update({k: float(r[k]) for k in STATS})
            past.setdefault(navn, []).append(rad)
    return past


def codex_sesong(d, past, sesong, logg):
    """Motorens prognose for hver runde. Returnerer DataFrame med én rad per spiller-runde."""
    sc = poengregler(sesong)
    lag = {n: i + 1 for i, n in enumerate(sorted(set(d.team)))}
    d = d.assign(lagid=d.team.map(lag), motid=d._opp_name.map(lag))
    hjemme = d[d.was_home].drop_duplicates('fixture')
    kamper = [dict(id=int(r.fixture), event=int(r.GW), team_h=int(r.lagid), team_a=int(r.motid),
                   kickoff_time=str(r.kickoff_time)) for r in hjemme.itertuples()]
    ut = []
    for t in range(FORSTE, SISTE + 1):
        hist, test = d[d.GW < t], d[d.GW == t]
        if test.empty:
            continue
        sist = test.drop_duplicates('element', keep='last').set_index('element')
        tot = hist.groupby('element')[['minutes', 'starts'] + STATS].sum()
        rader = {e: g for e, g in hist.groupby('element')}
        elements, history = [], {}
        for e in sorted(sist.index):
            r = sist.loc[e]
            s = tot.loc[e] if e in tot.index else None
            el = dict(id=int(e), web_name=r['name'], team=int(r['lagid']), element_type=POSNR[r['pos']],
                      now_cost=int(r['value']), status='a', chance_of_playing_next_round=None, can_select=True,
                      minutes=int(s['minutes']) if s is not None else 0, starts=int(s['starts']) if s is not None else 0,
                      total_points=0)
            el.update({k: float(s[k]) if s is not None else 0. for k in STATS})
            elements.append(el)
            h = rader.get(e)
            history[int(e)] = dict(
                history=[] if h is None else [dict(round=int(x.GW), starts=int(x.starts), minutes=int(x.minutes),
                                                   defensive_contribution=int(x.defensive_contribution))
                                              for x in h.itertuples()],
                history_past=past.get(r['name'], []))
        pm = [dict(element=int(x.element), fixture=int(x.fixture), team=int(x.lagid), gw=int(x.GW),
                   minutes=float(x.minutes), expected_goals=float(x.expected_goals))
              for x in hist[hist.element.isin(sist.index)].itertuples()]
        # Lagstyrken trenger ALLE spilleres xG i spilte kamper, også de som har forlatt ligaen.
        pm += [dict(element=-1, fixture=int(x.fixture), team=int(x.lagid), gw=int(x.GW), minutes=0.,
                    expected_goals=float(x.expected_goals)) for x in hist[~hist.element.isin(sist.index)].itertuples()]
        fx = [dict(f, finished=f['event'] < t) for f in kamper]
        bs = dict(elements=elements, teams=[dict(id=i, short_name=n) for n, i in lag.items()],
                  game_config=dict(scoring=sc))
        u = Uke(bs, fx, [], history, pm, [], t, t, 0, sesong.replace('-', '/'))
        md = poeng.avrund(poeng.grunnminutter(u, poeng.roller(u), set()))
        pr = poeng.prognose(u, md)
        fakta = test.groupby('element').agg(actual=('total_points', 'sum'), mins=('minutes', 'sum'), n_kamper=('fixture', 'count'))
        for e in u.ids:
            el = u.E[e]
            ut.append(dict(season=sesong, gw=t, element=e, name=el['web_name'], pos=el['element_type'],
                           pris=el['now_cost'] / 10, codex=pr.XP[u.ix[e], 0], codex_min=md[e, t][1],
                           actual=int(fakta.actual[e]), mins=int(fakta.mins[e]), n_kamper=int(fakta.n_kamper[e])))
        if t % 10 == 0:
            logg('  %s runde %d ferdig' % (sesong, t))
    return pd.DataFrame(ut)


def repo_sesong(X, d, prev):
    """Repoets produksjonsmodell én runde fram, summert per spiller-runde. repo_hybrid_faktor brukes etterpå."""
    pred = X.walk_forward(d, prev, first_gw=FORSTE)
    pred = pred[['name', 'gw', 'fixture', 'xp', 'exp_minutes']].copy()
    return pred


def blokk_se(sum_per_blokk, n_per_blokk):
    """Klyngerobust standardfeil for et snitt, med blokker som klynger."""
    S, n = np.asarray(sum_per_blokk, float), np.asarray(n_per_blokk, float)
    B, N = len(S), n.sum()
    snitt = S.sum() / N
    return float(np.sqrt(B / (B - 1) * ((S - n * snitt) ** 2).sum()) / N)


def maal(df):
    """Alle mål i planen. df har kolonnene season, gw, blokk, actual, pos, pris, mins og én kolonne per kandidat."""
    kand = ['repo', 'repo_hybrid', 'codex'] + ['w%.2f' % w for w in VEKTER]
    res = dict(n=int(len(df)), kandidater={})
    for utvalg, dd in [('alle', df)] + [(s, df[df.season == s]) for s in SESONGER]:
        r = {}
        for k in kand:
            feil = (dd[k] - dd.actual) ** 2
            topp = {}
            for n in (10, 20):
                topp[n] = float(dd.sort_values(k, ascending=False).groupby(['season', 'gw']).head(n)
                                .groupby(['season', 'gw']).actual.mean().mean())
            spilt = dd[dd.mins > 0]
            r[k] = dict(mse=float(feil.mean()), mae=float((dd[k] - dd.actual).abs().mean()),
                        skjevhet=float((dd[k] - dd.actual).mean()), topp10=topp[10], topp20=topp[20],
                        spearman_spilte=float(spilt[k].corr(spilt.actual, method='spearman')))
        res['kandidater'][utvalg] = r
    return res


def paret(df, a, b):
    """a minus b: forskjell i MSE og topp 10 med blokk-SE (fire-runders blokker innen sesong)."""
    d = (df[a] - df.actual) ** 2 - (df[b] - df.actual) ** 2
    g = d.groupby([df.season, df.blokk])
    ut = dict(d_mse=float(d.mean()), se_mse=blokk_se(g.sum().values, g.count().values))
    mse_b = float(((df[b] - df.actual) ** 2).mean())
    ut['prosent'] = 100 * ut['d_mse'] / mse_b
    ut['per_sesong'] = {s: float(d[df.season == s].mean()) for s in SESONGER}

    def topp(k):
        return df.sort_values(k, ascending=False).groupby(['season', 'gw']).head(10).groupby(['season', 'gw']).actual.mean()
    dt = (topp(a) - topp(b)).reset_index()
    dt['blokk'] = (dt.gw - FORSTE) // 4
    gt = dt.groupby(['season', 'blokk']).actual
    ut['d_topp10'] = float(dt.actual.mean())
    ut['se_topp10'] = blokk_se(gt.sum().values, gt.count().values)
    return ut


def skjevhet_tabell(df):
    rader = []
    df = df.assign(prisklasse=pd.cut(df.pris, [0, 5, 7.5, 10, 99], right=False, labels=['<5,0', '5,0-7,4', '7,5-9,9', '>=10,0']))
    for (pos, pk), dd in df.groupby(['pos', 'prisklasse']):
        if len(dd) < 30:
            continue
        rad = dict(pos={1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}[pos], prisklasse=str(pk), n=int(len(dd)),
                   faktisk=float(dd.actual.mean()))
        for k in ['repo', 'repo_hybrid', 'codex', 'w0.50']:
            e = dd[k] - dd.actual
            g = e.groupby([dd.season, dd.blokk])
            rad[k] = float(e.mean())
            rad[k + '_se'] = blokk_se(g.sum().values, g.count().values) if g.ngroups > 1 else float('nan')
            rad[k + '_per_sesong'] = {s: float(e[dd.season == s].mean()) for s in SESONGER if (dd.season == s).any()}
        rader.append(rad)
    return rader


def beslutning(df):
    """Den låste regelen i plan-v2.md del C."""
    utv = df[df.season.isin(UTVIKLING)]
    mse_utv = {w: float(((utv['w%.2f' % w] - utv.actual) ** 2).mean()) for w in VEKTER}
    w_valgt = min(VEKTER, key=lambda w: (mse_utv[w], abs(w - .5)))
    ut = dict(mse_utvikling=mse_utv, w_valgt=w_valgt)
    if w_valgt == .5:
        ut.update(konklusjon='BEHOLD 0,50', grunn='0,50 har lavest MSE på utviklingsårene')
        return ut
    p = paret(df, 'w%.2f' % w_valgt, 'w0.50')
    krav = {
        'minst 0,5 % lavere MSE samlet': -p['prosent'] >= .5,
        'minst 3 blokk-SE': p['d_mse'] < 0 and abs(p['d_mse']) >= 3 * p['se_mse'],
        'samme fortegn i alle tre sesonger': all(v < 0 for v in p['per_sesong'].values()),
        'topp 10 ikke dårligere enn 2 blokk-SE': p['d_topp10'] >= -2 * p['se_topp10'],
    }
    ut.update(paret_mot_050=p, krav={k: bool(v) for k, v in krav.items()},
              konklusjon=('ENDRE til %.2f' % w_valgt) if all(krav.values()) else 'UAVKLART: behold 0,50')
    return ut


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', default=str(ROT / 'data' / 'cache' / 'vaastav'))
    ap.add_argument('--ut', default=str(HER.parent / 'modell' / 'motor'))
    a = ap.parse_args()
    import eval_engine as X
    ut = Path(a.ut)
    ut.mkdir(parents=True, exist_ok=True)
    start = time.time()

    def logg(s):
        print('[%4.0f s] %s' % (time.time() - start, s), flush=True)
    data = {s: X.load_season(s, cache=a.cache) for s in ALLE}
    deler = []
    for s in SESONGER:
        d = data[s]
        logg(s + ': codex')
        c = codex_sesong(d, tidligere(data, s), s, logg)
        logg(s + ': repo')
        r = repo_sesong(X, d, data[X.PRIOR_OF[s]])
        r = r.merge(c[['name', 'gw', 'codex_min']], on=['name', 'gw'], how='inner')
        r['hyb'] = np.where(r.exp_minutes > 0, r.xp * r.codex_min / r.exp_minutes.where(r.exp_minutes > 0, 1), np.nan)
        rr = r.groupby(['name', 'gw']).agg(repo=('xp', 'sum'), repo_hybrid=('hyb', lambda v: v.sum(min_count=len(v))),
                                           n_repo=('xp', 'count')).reset_index()
        m = c.merge(rr, on=['name', 'gw'], how='left')
        # Som i ukekjøringen: uten brukbar repo-rad (0 minutter eller annet kampantall) brukes codex i hybriden.
        m['har_repo'] = m.repo.notna()
        m['repo_hybrid'] = m.repo_hybrid.where(m.repo_hybrid.notna() & (m.n_repo == m.n_kamper), m.codex)
        deler.append(m)
    alle = pd.concat(deler, ignore_index=True)
    alle['blokk'] = (alle.gw - FORSTE) // 4
    for w in VEKTER:
        alle['w%.2f' % w] = w * alle.codex + (1 - w) * alle.repo_hybrid
    alle.to_csv(ut / 'poengsett_prediksjoner.csv.gz', index=False)
    df = alle[alle.har_repo].copy()
    res = maal(df)
    res.update(rader_totalt=int(len(alle)), rader_uten_repo=int((~alle.har_repo).sum()),
               runder=[FORSTE, SISTE], sesonger=SESONGER, beslutning=beslutning(df),
               paret=dict(codex_mot_repo_hybrid=paret(df, 'codex', 'repo_hybrid'),
                          repo_hybrid_mot_repo=paret(df, 'repo_hybrid', 'repo'),
                          **{'w%.2f_mot_w0.50' % w: paret(df, 'w%.2f' % w, 'w0.50') for w in VEKTER if w != .5}),
               skjevhet=skjevhet_tabell(df), sekunder=round(time.time() - start))
    (ut / 'maling_poengsett.json').write_text(json.dumps(res, indent=1, ensure_ascii=False))
    logg('Ferdig. ' + json.dumps(res['beslutning'], ensure_ascii=False))
    for k, v in res['kandidater']['alle'].items():
        print('%-12s MSE %.4f  topp10 %.3f  topp20 %.3f  skjevhet %+.3f' % (k, v['mse'], v['topp10'], v['topp20'], v['skjevhet']))


if __name__ == '__main__':
    main()
