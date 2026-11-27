"""Re-run production P0 baseline, compare frozen original reconstruction row-wise."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,time
import numpy as np
import pandas as pd
O=Path(__file__).resolve().parent;ROOT=O.parents[2]
sys.path.insert(0,str(ROOT/'src'))
import eval_engine as X
import evaluate_pred as P
import minutes as M


def run():
    start=time.time();predictions=[];diagnostics=[]
    assert not getattr(M,'SUB_GIVEN_NO_START',False),'Baseline must retain old minute behavior'
    for season in P.SEASONS:
        p=X.walk_forward(X.load_season(season),X.load_season(X.PRIOR_OF[season]),first_gw=2)
        predictions.append(p);diagnostics+=p.attrs['diagnostics']
        print(season,len(p),'elapsed',round(time.time()-start,1),flush=True)
    p=pd.concat(predictions,ignore_index=True)
    p.to_csv(O/'p0_prediksjoner.csv.gz',index=False,compression='gzip')
    pd.DataFrame(diagnostics).to_csv(O/'p0_diagnostikk.csv',index=False)
    rows=[]
    for season in list(P.SEASONS)+['alle']:
        q=p if season=='alle' else p[p.season==season]
        for window,qw in [('GW2-38',q),('GW8-38',q[q.gw>=8])]:
            t=qw.copy();t['xp__produksjon_p0']=t.xp
            s=P.summary(t,['produksjon_p0']).iloc[0].to_dict()
            s.update(season=season,window=window,played=int((qw.mins>0).sum()),
                     rounds=qw[['season','gw']].drop_duplicates().shape[0],
                     predicted=qw.xp.mean(),actual=qw.actual.mean())
            rows.append(s)
    pd.DataFrame(rows).to_csv(O/'p0_baseline.csv',index=False)
    old=pd.read_csv(O/'prediksjoner.csv.gz');old=old[old.model=='produksjon_offline']
    old=old.rename(columns={'fixture':'source_fixture'})
    key=['season','name','gw','source_fixture']
    z=p.merge(old,on=key,suffixes=('_new','_old'),validate='one_to_one',how='outer',indicator=True)
    assert (z['_merge']=='both').all(),z['_merge'].value_counts()
    assert np.array_equal(z.actual_new,z.actual_old)
    z['delta_xp']=z.xp_new-z.xp_old
    z['delta_bonus']=z.xp_bonus_new-z.xp_bonus_old
    deltas=[]
    for season,q in list(z.groupby('season'))+[('alle',z)]:
        deltas.append(dict(season=season,n=len(q),max_abs_xp=q.delta_xp.abs().max(),
            mean_abs_xp=q.delta_xp.abs().mean(),max_abs_bonus=q.delta_bonus.abs().max(),
            mean_delta_xp=q.delta_xp.mean(),rows_over_1e_6=int((q.delta_xp.abs()>1e-6).sum()),
            rows_over_001=int((q.delta_xp.abs()>.01).sum())))
    pd.DataFrame(deltas).to_csv(O/'p0_rekonstruksjon_avvik.csv',index=False)
    z.reindex(z.delta_xp.abs().sort_values(ascending=False).index).head(100)[
        key+['xp_new','xp_old','delta_xp','delta_bonus']].to_csv(O/'p0_storste_avvik.csv',index=False)
    paths=[ROOT/'src'/n for n in ['eval_engine.py','evaluate_pred.py','expected_points.py','team_strength.py','minutes.py']]
    (O/'p0_manifest.json').write_text(json.dumps(dict(seconds=time.time()-start,python=sys.version,
        minute_flag=getattr(M,'SUB_GIVEN_NO_START',False),sha256={str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in paths}),indent=2))
    print(pd.DataFrame(rows).to_string(index=False));print(pd.DataFrame(deltas).to_string(index=False))

if __name__=='__main__':run()
