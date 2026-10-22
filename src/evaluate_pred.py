"""Paired walk-forward evaluation of the actual production forecast functions.

Primary endpoint: player-fixture MSE, GW8-38 in three seasons. Uncertainty
uses non-overlapping four-GW blocks within each season, rather than treating
correlated player rows as independent. See samarbeid/modell/plan.md.

Configurations mutate production flags and return a restoration callback:

    import minutes as M
    def candidate():
        old = M.SUB_GIVEN_NO_START
        M.SUB_GIVEN_NO_START = True
        return lambda: setattr(M, 'SUB_GIVEN_NO_START', old)
    compare({'baseline': lambda: None, 'candidate': candidate})

All historical input is local. Prediction formulas are in minutes,
team_strength and expected_points; eval_engine only reconstructs inputs.
season_sim still uses the legacy backtest implementation and is not yet a
production-parity decision evaluation (that is a separate planned step).
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import eval_engine as engine

BASE = engine.CACHE
SEASONS = ('2023-24', '2024-25', '2025-26')
PRIOR_OF = engine.PRIOR_OF


def load_season(season):
    return engine.load_season(season, cache=BASE)


def walk_forward(d, sprior=None, prev=None, first_gw=None, rounds=None):
    """sprior is obsolete: production computes its own minute prior."""
    if prev is None:
        season = str(d.season.iloc[0])
        prev = load_season(PRIOR_OF[season])
    return engine.walk_forward(d, prev, first_gw=8 if first_gw is None else first_gw,
                               rounds=rounds)


def block_effect(values, season, gw, block_size=4, origin=8):
    """Mean and cluster-robust SE of a paired delta (unequal block sizes).

    Blocks never cross season boundaries. Center each block's sum by its
    row count times the global mean; do not give a three-round tail block
    the same weight as a full four-round block. One block cannot give an SE.
    """
    q = pd.DataFrame({'delta': np.asarray(values, float),
                      'season': np.asarray(season), 'gw': np.asarray(gw)})
    if q.empty:
        raise ValueError('No paired observations')
    q['block'] = (q.gw-origin)//block_size
    mu = float(q.delta.mean())
    clusters = q.groupby(['season','block']).delta.agg(['sum','size'])
    n = len(clusters)
    se = (float(np.sqrt(n/(n-1)*((clusters['sum']-mu*clusters['size'])**2).sum())/len(q))
          if n > 1 else float('nan'))
    return mu, se, n


def summary(p, names):
    rows=[]
    played=p[p.mins > 0]
    for nm in names:
        col=f'xp__{nm}'
        err=p[col]-p.actual
        row=dict(model=nm,n=len(p),mae=err.abs().mean(),mse=(err**2).mean(),
                 rmse=np.sqrt((err**2).mean()),
                 spearman_played=spearmanr(played[col],played.actual)[0])
        for k in (10,20,50):
            row[f'top{k}']=np.mean([g.nlargest(k,col).actual.mean()
                                    for _,g in p.groupby(['season','gw'])])
        rows.append(row)
    return pd.DataFrame(rows)


def paired_statistics(p, names, block_size=4, origin=8):
    """All effects are candidate minus baseline; MSE/MAE lower, top-k higher."""
    rows=[]
    a=names[0]
    for nm in names[1:]:
        for season in list(p.season.unique())+(['alle'] if p.season.nunique()>1 else []):
            q=p if season=='alle' else p[p.season==season]
            aa,bb=q[f'xp__{a}']-q.actual,q[f'xp__{nm}']-q.actual
            effects={'mse':bb**2-aa**2,'mae':bb.abs()-aa.abs()}
            if 'actual_bonus' in q:
                effects['bonus_mse']=(q[f'bonus__{nm}']-q.actual_bonus)**2-(q[f'bonus__{a}']-q.actual_bonus)**2
            for metric,delta in effects.items():
                mean,se,blocks=block_effect(delta,q.season,q.gw,block_size,origin)
                rows.append(dict(model=nm,reference=a,season=season,metric=metric,
                    difference=mean,se=se,blocks=blocks,n=len(q),
                    relative_mse_reduction=(-mean/(aa**2).mean() if metric=='mse' else np.nan)))
            for k in (10,20,50):
                v=[]
                for (s,g),h in q.groupby(['season','gw']):
                    v.append(dict(season=s,gw=g,delta=h.nlargest(k,f'xp__{nm}').actual.mean()
                                  -h.nlargest(k,f'xp__{a}').actual.mean()))
                v=pd.DataFrame(v)
                mean,se,blocks=block_effect(v.delta,v.season,v.gw,block_size,origin)
                rows.append(dict(model=nm,reference=a,season=season,metric=f'top{k}',
                    difference=mean,se=se,blocks=blocks,n=len(v),relative_mse_reduction=np.nan))
    return pd.DataFrame(rows)


def compare(configs, seasons=SEASONS, use_prior=True, first_gw=8, rounds=None):
    """Run serial configurations, verify pairing AND outcomes, report block SE.

    The personal/team priors belong to the production model. To ablate a prior,
    inject an explicit empty prior frame in that production function; silently
    reverting to the legacy backtest model is intentionally unsupported.
    """
    if not use_prior:
        raise ValueError('Production evaluation requires prior-season inputs')
    first_gw = 8 if first_gw is None else first_gw
    names=list(configs)
    if not names:
        raise ValueError('At least one configuration is required')
    allp=[]
    for season in seasons:
        d,prev=load_season(season),load_season(PRIOR_OF[season])
        runs={}
        for nm,configure in configs.items():
            undo=configure()
            try:
                runs[nm]=walk_forward(d,prev=prev,first_gw=first_gw,rounds=rounds)
            finally:
                if callable(undo):
                    undo()
            print(f'  kjørt {season}/{nm}: {len(runs[nm])} prediksjoner',flush=True)
        base=runs[names[0]]
        keys=['element','gw','fixture']
        stable=keys+['actual','actual_bonus','mins']
        p=base[keys+['name','pos','value','actual','actual_bonus','mins','b_form']].copy()
        for nm in names:
            other=runs[nm]
            if not other[stable].equals(base[stable]):
                raise RuntimeError(f'{season}/{nm}: forskjellige rader eller utfall; ikke parvis')
            p[f'xp__{nm}']=other.xp.to_numpy(float)
            p[f'bonus__{nm}']=other.xp_bonus.to_numpy(float)
        p['season']=season
        allp.append(p)
    p=pd.concat(allp,ignore_index=True)
    print(summary(p,names).round(5).to_string(index=False))
    stats=paired_statistics(p,names,origin=first_gw)
    if not stats.empty:
        print('\nParvis effekt, kandidat minus baseline, fire-runders blokk-SE:')
        print(stats.round(6).to_string(index=False))
    p.attrs['comparison']=stats.to_dict('records')
    return p


if __name__=='__main__':
    compare({'baseline':lambda:None})
