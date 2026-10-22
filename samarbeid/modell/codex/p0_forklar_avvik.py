"""Attribute reconstruction differences to production minute-prior matching.

The legacy provider is a diagnostic ablation only, never the evaluation default.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
O=Path(__file__).resolve().parent;R=O.parents[2]
sys.path.insert(0,str(R/'src'))
import eval_engine as X
import minutes as M
import backtest as B


def run():
    old=pd.read_csv(O/'prediksjoner.csv.gz');old=old[old.model=='produksjon_offline']
    rows=[]
    for season in X.PRIOR_OF:
        d,prev=X.load_season(season),X.load_season(X.PRIOR_OF[season])
        sp=B.start_prior(prev).set_index('name')
        mgs=prev[prev.starts==1].groupby('name').minutes.mean()
        def legacy_provider(bs):
            names={t['id']:t['name'] for t in bs['teams']}
            rows=[]
            for e in bs['elements']:
                name=e['first_name']
                if name in sp.index:
                    row=sp.loc[name]
                    moved=str(row.prior_team).lower()!=str(names[e['team']]).lower()
                    rows.append(dict(element=e['id'],prior_p_start=row.prior_p_start,
                        min_given_start=mgs.get(name,np.nan),moved=moved))
            return pd.DataFrame(rows,columns=['element','prior_p_start','min_given_start','moved'])
        for gw in [2,8,20,38]:
            with patch.object(M,'last_season_minutes',legacy_provider):
                p=X.walk_forward(d,prev,first_gw=gw,rounds=[gw])
            ref=old[(old.season==season)&(old.gw==gw)].rename(columns={'fixture':'source_fixture'})
            z=p.merge(ref,on=['season','name','gw','source_fixture'],suffixes=('_new','_old'),validate='one_to_one')
            delta=z.xp_new-z.xp_old
            rows.append(dict(season=season,gw=gw,n=len(z),max_abs_xp=delta.abs().max(),mean_abs_xp=delta.abs().mean()))
    pd.DataFrame(rows).to_csv(O/'p0_avviksforklaring.csv',index=False)
    print(pd.DataFrame(rows).to_string(index=False))

if __name__=='__main__':run()
