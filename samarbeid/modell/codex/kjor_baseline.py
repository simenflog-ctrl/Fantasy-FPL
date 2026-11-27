#!/usr/bin/env python3
"""Offline walk-forward: unchanged evaluate_pred reference + production functions.
Run from any cwd; all output and bytecode restricted to this directory.
No API/status archives: production reconstruction assumes availability=1.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
import contextlib, io, json, time, hashlib, socket
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import evaluate_pred as P
# Preserve this first review's legacy reference after evaluate_pred migrated.
from types import ModuleType
_original_sources = OUT / 'p0_original_sources.json'
if _original_sources.exists():
    P = ModuleType('legacy_evaluate_pred')
    P.__file__ = str(ROOT / 'src/evaluate_pred.py')
    exec(compile(json.loads(_original_sources.read_text())['src/evaluate_pred.py'],
                 P.__file__, 'exec'), P.__dict__)
import backtest as B
import minutes as M
import expected_points as E
import team_strength as T

# Fail closed: accidental network access must never silently fall back.
def no_network(*a, **k):
    raise RuntimeError('Network forbidden in this offline evaluation')
socket.socket.connect = no_network
socket.create_connection = no_network
P.BASE = str(ROOT / 'data/cache/vaastav')
SEASONS = ('2023-24', '2024-25', '2025-26')
_original_load = B.load
def deduplicated_load():
    d = _original_load()
    return d.drop_duplicates(['name','team','fixture']).copy()
B.load = deduplicated_load

def quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)

def tau_fast(pm):
    """Same grid/objective as E.fit_bonus_temperature, vectorized across fixtures."""
    q = pm[pm.minutes > 0]
    if q.empty:
        return 2.0
    codes, _ = pd.factorize(q.fixture, sort=True)
    bps, actual = q.bps.to_numpy(float), q.bonus.to_numpy(float)
    best, err = 8., float('inf')
    for tau in np.arange(2., 30., .5):
        w = np.exp(bps / tau)
        pred = 6 * w / np.bincount(codes, weights=w)[codes]
        score = np.abs(pred - actual).sum()
        if score < err:
            best, err = float(tau), score
    return best

def team_matches(d, teams):
    q = d.groupby(['fixture', 'team', 'GW', 'was_home'], as_index=False).agg(
        xg_for=('expected_goals', 'sum'), goals_for=('goals_scored', 'sum'),
        player_minutes=('minutes', 'sum'))
    other = q[['fixture','team','xg_for','goals_for']].rename(columns={
        'team':'opponent','xg_for':'xg_against','goals_for':'goals_against'})
    q = q.merge(other, on='fixture')
    q = q[q.team != q.opponent].copy()
    q['team'] = q.team.map(teams)
    q['opponent'] = q.opponent.map(teams)
    return q.rename(columns={'GW':'gw'})

def production(season, d, prev):
    raw = pd.read_csv(f'{P.BASE}/{season}/gws/merged_gw.csv').drop_duplicates()
    # Keep historical metadata out of B.load's deliberately narrow columns.
    meta = raw[['name','fixture','value']].drop_duplicates(['name','fixture'])
    d = d.merge(meta, on=['name','fixture'], validate='one_to_one')
    names = sorted(set(d.name) | set(prev.name))
    ids = {n:i+1 for i,n in enumerate(names)}
    teams = {n:i+1 for i,n in enumerate(sorted(set(d.team) | set(prev.team)))}
    prevpm = prev.assign(element=prev.name.map(ids)).rename(columns={'GW':'gw'})
    # Prior from prior-season goals, same estimator and penalty as production.
    old = B.PRIOR_WEIGHT_TEAM
    B.PRIOR_WEIGHT_TEAM = .5
    try:
        pa, pdf, ha, _ = B.team_ratings(prev.assign(expected_goals=prev.goals_scored))
    finally:
        B.PRIOR_WEIGHT_TEAM = old
    bottom = sorted(pa, key=lambda n: pa[n]-pdf[n])[:3]
    fa, fd = np.mean([pa[n] for n in bottom]), np.mean([pdf[n] for n in bottom])
    prev_tm = team_matches(prev, teams)
    gc = prev_tm.goals_against.to_numpy(float)
    mean, var = gc.mean(), gc.var()
    dispersion = 1e6 if var <= mean else float(np.clip(mean**2/(var-mean), .5, 50))
    agg = prev.groupby('name').agg(mins=('minutes','sum'), goals=('goals_scored','sum'),
        assists=('assists','sum'), bps=('bps','sum'), bonus=('bonus','sum'), yellow=('yellow_cards','sum'))
    personal = agg[agg.mins >= E.PRIOR_MIN_MINUTES].copy()
    personal['element'] = personal.index.map(ids)
    for src, dest in [('goals','p_goals'),('assists','p_assists'),('bps','p_bps'),('bonus','p_bonus'),('yellow','p_yellow')]:
        personal[dest] = personal[src]/personal.mins*90
    ep = personal[['element','p_goals','p_assists','p_bps','p_bonus','p_yellow']].reset_index(drop=True)
    # Same matching by full name; no 2025-26 cleaned file used for earlier years.
    E.last_season_priors = lambda bs: ep
    spr = B.start_prior(prev)
    mgs = prev[prev.starts == 1].groupby('name').minutes.mean()
    results, diagnostics = [], []
    for gw in sorted(g for g in d.GW.unique() if g >= 2):
        hist, test = d[d.GW < gw].copy(), d[d.GW == gw].copy()
        if hist.empty:
            continue
        latest = pd.concat([hist, test]).drop_duplicates('name', keep='last')
        # Test only contributes roster/position/team metadata, never match outcomes.
        bs = {'teams':[{'id':tid,'short_name':n,'name':n} for n,tid in teams.items()], 'elements':[]}
        psmap = {'GK':1,'DEF':2,'MID':3,'FWD':4}
        for r in latest.itertuples():
            bs['elements'].append(dict(id=ids[r.name], team=teams[r.team], first_name=r.name,
                second_name='', web_name=r.name, element_type=psmap[r.pos], now_cost=r.value, status='a'))
        prior = spr.copy()
        prior['element'] = prior.name.map(ids)
        prior['min_given_start'] = prior.name.map(mgs)
        now = latest.set_index('name').team
        prior['moved'] = prior.prior_team != prior.name.map(now)
        M.last_season_minutes = lambda bs: prior[['element','prior_p_start','min_given_start','moved']]
        pm = hist.assign(element=hist.name.map(ids)).rename(columns={'GW':'gw'})
        mins = quiet(M.build, pm, bs, M.league_rates(pm))
        rates = quiet(E.per90_rates, pm[pm.minutes > 0], mins, bs)
        rates['dc_rate'] = rates.element.map(E.dc_hit_rates(pm[pm.minutes > 0], rates)).fillna(0.)
        tm = team_matches(hist, teams)
        present = sorted(set(test.team) | set(hist.team))
        priors = pd.DataFrame([dict(team_id=teams[n], short_name=n,
            prior_att=pa.get(n,fa), prior_def=pdf.get(n,fd)) for n in present])
        ratings = quiet(T.fit_current, tm, priors, ha)
        rr = ratings.set_index('short_name')
        fixtures = test[['GW','fixture','team','_opp_name','was_home']].drop_duplicates()
        projs=[]
        # iterrows avoids pandas renaming underscore-prefixed tuple fields.
        for _, r in fixtures.iterrows():
            a, o = rr.loc[r.team], rr.loc[r._opp_name]
            projs.append(dict(gw=gw, fixture=r.fixture, team=r.team, opponent=r._opp_name,
                xg_for=round(float(np.exp(a.mu+a.att-o['def']+(ha if r.was_home else 0))),3),
                xg_against=round(float(np.exp(a.mu+o.att-a['def']+(0 if r.was_home else ha))),3)))
        proj = pd.DataFrame(projs)
        tau = tau_fast(pm)
        if gw == 2:
            assert tau == E.fit_bonus_temperature(pm), 'vectorized tau mismatch'
        scale = quiet(E.calibrate_xg_to_goals, tm, proj)
        pred = E.expected_points(rates, ratings, proj, tau, scale, dispersion, n_gw=1, season=season)
        pred['name'] = pred.element.map({v:k for k,v in ids.items()})
        obs = test[['name','fixture','total_points','bonus','minutes','value']].rename(columns={
            'total_points':'actual','bonus':'actual_bonus','minutes':'mins'})
        pred = pred.merge(obs, on=['name','fixture'], validate='one_to_one')
        pred['model']='produksjon_offline'; pred['season']=season
        results.append(pred[['model','season','name','pos','gw','fixture','xp','xp_bonus','actual','actual_bonus','mins','value']])
        diagnostics.append(dict(season=season,gw=gw,tau=tau,goal_scale=scale,n=len(pred)))
        if gw % 8 == 0:
            print(f'{season} produksjon GW{gw} tau={tau}', flush=True)
    return pd.concat(results, ignore_index=True), diagnostics

def summaries(p):
    p=p.copy()
    for col in ['xp','xp_bonus','actual','actual_bonus','mins','value']:
        p[col]=pd.to_numeric(p[col],errors='raise')
    rows=[]
    for (model, season), g in p.groupby(['model','season']):
        for lab, q in [('GW2-38',g), ('GW8-38',g[g.gw>=8])]:
            played=q[q.mins>0]
            z=dict(model=model,season=season,window=lab,n=len(q),played=len(played),rounds=q[['source_season','gw']].drop_duplicates().shape[0],
                mae=(q.xp-q.actual).abs().mean(),rmse=np.sqrt(((q.xp-q.actual)**2).mean()),
                spearman_played=spearmanr(played.xp,played.actual)[0],
                predicted=q.xp.mean(),actual=q.actual.mean())
            for k in (10,20,50):
                selected = [h.nlargest(k,'xp').actual.mean() for _,h in q.groupby(['source_season','gw'])]
                z[f'top{k}']=np.mean(selected)
                z[f'top{k}_se']=np.std(selected,ddof=1)/np.sqrt(len(selected))
            rows.append(z)
    pd.DataFrame(rows).to_csv(OUT/'baseline.csv',index=False)
    rows=[]
    p=p[p.model != 'form_3gw'].copy()
    # Price at the last observed earlier GW, never the realized test-match price.
    price_tables=[]
    for season in SEASONS:
        raw=pd.read_csv(f'{P.BASE}/{season}/gws/merged_gw.csv').drop_duplicates()
        prices=raw.sort_values(['GW','fixture']).groupby(['name','GW'],as_index=False).value.first()
        prices['pre_value']=prices.groupby('name').value.shift(1)
        prices=prices.rename(columns={'GW':'gw'})[['name','gw','pre_value']]
        prices['season']=season
        price_tables.append(prices)
    prices=pd.concat(price_tables,ignore_index=True)
    original=p[p.season != 'alle'].merge(prices,on=['season','name','gw'],validate='many_to_one')
    p=pd.concat([original,original.assign(season='alle')],ignore_index=True)
    p['value']=p.pre_value
    p['price_group']=pd.cut(p.value/10,[-np.inf,6,8,10,np.inf],right=False,labels=['<6','6-8','8-10','>=10'])
    for (model, season), base in p.groupby(['model','season']):
        for window, g in [('GW2-38',base),('GW8-38',base[base.gw>=8])]:
            for subset, q in [('all',g),('played',g[g.mins>0])]:
                for (price,pos), h in q.groupby(['price_group','pos'], observed=True):
                    for metric, pred, actual in [('total','xp','actual'),('bonus','xp_bonus','actual_bonus')]:
                        err=h[pred]-h[actual]
                        pergw=h.assign(err=err).groupby(['source_season','gw']).err.mean()
                        clusters=h.assign(centered=err-err.mean()).groupby(['source_season','gw']).centered.sum()
                        cluster_se=np.sqrt(len(clusters)/max(len(clusters)-1,1)*(clusters**2).sum())/len(h)
                        rows.append(dict(model=model,season=season,window=window,subset=subset,
                            price_group=price,pos=pos,metric=metric,n=len(h),rounds=len(pergw),
                            predicted=h[pred].mean(),actual=h[actual].mean(),bias=err.mean(),
                            bias_se_gw=cluster_se,
                            bias_gw_mean=pergw.mean()))
    pd.DataFrame(rows).to_csv(OUT/'kalibrering.csv',index=False)

if __name__=='__main__':
    start=time.time(); allp=[]; diagnostics=[]
    for season in SEASONS:
        d=P.load_season(season); prev=P.load_season(P.PRIOR_OF[season]).copy()
        # IDs restart each season: avoid cross-season fixture joins in early-GW pooling.
        prev['fixture'] = -prev.fixture
        p=P.walk_forward(d,P.start_prior_for(season),prev,first_gw=2)
        raw=pd.read_csv(f'{P.BASE}/{season}/gws/merged_gw.csv').drop_duplicates()
        obs=raw[['name','fixture','value','bonus']].rename(columns={'bonus':'actual_bonus'})
        p=p.merge(obs,on=['name','fixture'],validate='one_to_one')
        p=p.rename(columns={'bonus':'xp_bonus'});p['model']='evaluate_pred';p['season']=season
        allp.append(p)
        # Free baselines use exact same rows as evaluate_pred.
        for col in ['b_form']:
            f=p.copy(); f['xp']=f[col];f['xp_bonus']=np.nan;f['model']='form_3gw';allp.append(f)
        print(f'{season} rig complete: {len(p)} rows, elapsed {time.time()-start:.1f}s',flush=True)
        prod, diag=production(season,d,prev);allp.append(prod);diagnostics+=diag
        pd.concat(allp,ignore_index=True).to_csv(OUT/'prediksjoner.csv.gz',index=False,compression='gzip')
    p=pd.concat(allp,ignore_index=True)
    p['source_season']=p.season
    p=pd.concat([p,p.assign(season='alle')],ignore_index=True)
    summaries(p)
    pd.DataFrame(diagnostics).to_csv(OUT/'diagnostikk.csv',index=False)
    paths=[ROOT/'src'/n for n in ['backtest.py','evaluate_pred.py','minutes.py','expected_points.py','team_strength.py']]
    paths += [ROOT/f'data/cache/vaastav/{s}/gws/merged_gw.csv' for s in ['2022-23',*SEASONS]]
    (OUT/'manifest.json').write_text(json.dumps(dict(seconds=time.time()-start,python=sys.version,
        pandas=pd.__version__,numpy=np.__version__,sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2))
    print(f'Done: {time.time()-start:.1f}s',flush=True)
