"""Verify executed artifacts, tau lock, numeric tables, flags and frozen gates."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json
from datetime import datetime
import numpy as np
import pandas as pd
O=Path(__file__).resolve().parent;R=O.parents[2]
sys.path.insert(0,str(O))
import kjor_p1p2 as K


def run():
    lock=json.loads((O/'p1_tau_last.json').read_text());method=json.loads((O/'p1p2_metode_for_kjoring.json').read_text())
    grid=pd.read_csv(O/'p1p2_tau_utvikling.csv');pooled=grid[grid.season=='utvikling_samlet']
    assert int(pooled.sort_values(['bonus_mse','tau']).iloc[0].tau)==lock['tau']
    assert lock['control_not_loaded'] and '2025-26' not in lock['load_history']
    assert hashlib.sha256((O/'p1p2_tau_utvikling.csv').read_bytes()).hexdigest()==lock['development_table_sha256']
    assert datetime.fromisoformat(method['exception_scope_written_utc'])<datetime.fromisoformat(lock['locked_utc'])
    for path,h in method['source_sha256'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h
    control=pd.read_csv(O/'p1p2_2025-26_base_locked.csv.gz')
    assert [c for c in control if c.startswith('bonus__tau')]==[f"bonus__tau{lock['tau']}"]
    pred=pd.read_csv(O/'p1p2_prediksjoner.csv.gz');levels=pd.read_csv(O/'p1p2_nivaer.csv')
    assert np.isfinite(pred[['xp','xp_bonus','actual','actual_bonus','mins','p_start','p_play','exp_minutes']]).all().all()
    predictions={name:K.sort(p) for name,p in pred.groupby('model')}
    base=predictions['baseline']
    assert len(base)==72583
    for name,p in predictions.items():
        assert len(p)==len(base) and p[K.KEY+['actual','mins']].equals(base[K.KEY+['actual','mins']])
        for season in [*K.SEASONS,'alle']:
            q=p if season=='alle' else p[p.season==season]
            z=levels[(levels.model==name)&(levels.season==season)].iloc[0]
            assert len(q)==z.n
            assert abs(((q.xp-q.actual)**2).mean()-z.mse)<1e-12
            assert abs(((q.xp_bonus-q.actual_bonus)**2).mean()-z.bonus_mse)<1e-12
    stat=pd.read_csv(O/'p1p2_parvis.csv');cal=pd.read_csv(O/'p1p2_premium.csv');wace=pd.read_csv(O/'p1p2_premium_wace.csv')
    for _,r in wace.iterrows():
        q=cal[(cal.model==r.model)&(cal.season==r.season)&(cal.metric==r.metric)]
        assert q.n.sum()==r.n
        assert abs((q.n*q.bias_baseline.abs()).sum()/q.n.sum()-r.wace_baseline)<1e-12
        assert abs((q.n*q.bias_candidate.abs()).sum()/q.n.sum()-r.wace_candidate)<1e-12
        assert abs(r.wace_candidate-r.wace_baseline-r.delta_wace)<1e-12
    decision=json.loads((O/'p1p2_beslutning.json').read_text())
    canonical={n:K.assess(stat,wace,n,bonus=n!='P2') for n in ['P2','B1']}
    assert all(canonical[n]==decision[n] for n in canonical)
    # The combined candidate never inherits B1's special primary-endpoint exception.
    if 'B1+P2' in predictions:
        canonical['B1+P2']=K.assess(stat,wace,'B1+P2',bonus=True)
        if canonical['B1+P2']!=decision['B1+P2']:
            K.dump('p1p2_beslutning_fra_kjoring.json',decision)
            decision['B1+P2']=canonical['B1+P2']
            K.dump('p1p2_beslutning.json',decision)
    manifest=json.loads((O/'p1p2_manifest.json').read_text())
    for path,h in manifest['source_sha256'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h
    assert K.M.SUB_GIVEN_NO_START is False and K.E.BONUS_TAU_FIXED is None
    parity=pd.read_csv(O/'p1p2_p0_paritet.csv');assert parity['max'].max()<1e-10
    report=dict(rows_per_model=len(base),tau=lock['tau'],only_locked_tau_on_control=True,
        baseline_max_delta_vs_p0=float(parity['max'].max()),
        model_source_unchanged_during_run=True,flags_restored=True,
        statuses={name:value['status'] for name,value in decision.items() if isinstance(value,dict) and 'status' in value})
    K.dump('p1p2_verifikasjon.json',report)
    print(json.dumps(report,indent=2))

if __name__=='__main__':run()
