#!/usr/bin/env python3
"""Independent P1/P2 measurements. No control outcomes read before tau lock.

Run in existing Anaconda Python. No downloads, package installs or production
outputs. All artifacts go next to this file. Claudes actual flags are restored
in finally blocks. The only model code called is the production eval engine.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime,timezone
import hashlib,json,socket,time
import numpy as np
import pandas as pd

O=Path(__file__).resolve().parent;R=O.parents[2]
sys.path.insert(0,str(R/'src'))
import eval_engine as X
import evaluate_pred as P
import expected_points as E
import minutes as M

GRID=(4,5,6,7,8,10,12)
DEV=('2023-24','2024-25');CONTROL='2025-26';SEASONS=(*DEV,CONTROL)
KEY=['season','element','gw','fixture']

def now():return datetime.now(timezone.utc).isoformat()
def dump(name,value):
    (O/name).write_text(json.dumps(value,indent=2,allow_nan=False))

@contextmanager
def flags(sub=False,tau=None):
    old=M.SUB_GIVEN_NO_START,E.BONUS_TAU_FIXED
    try:
        M.SUB_GIVEN_NO_START=sub;E.BONUS_TAU_FIXED=tau
        yield
    finally:
        M.SUB_GIVEN_NO_START,E.BONUS_TAU_FIXED=old

def fixed(tau):
    def apply():
        old=E.BONUS_TAU_FIXED;E.BONUS_TAU_FIXED=tau
        return lambda:setattr(E,'BONUS_TAU_FIXED',old)
    return apply

def sort(p):return p.sort_values(KEY).reset_index(drop=True)

def run_season(season,*,sub=False,tau=None,cases=None):
    print('START',season,'P2',sub,'tau',tau,'score_cases',list(cases or {}),now(),flush=True)
    d,prev=X.load_season(season),X.load_season(X.PRIOR_OF[season])
    with flags(sub,tau):
        p=X.walk_forward(d,prev,first_gw=8,score_cases=cases)
    assert p.gw.nunique()==31
    assert not p.duplicated(KEY).any()
    print('DONE',season,len(p),now(),flush=True)
    return sort(p)

def pair(predictions):
    base=sort(predictions['baseline'])
    q=base[KEY+['name','pos','pre_value','actual','actual_bonus','mins','actual_start','p_start']].copy()
    for name,p in predictions.items():
        p=sort(p)
        assert p[KEY+['actual','actual_bonus','mins','actual_start']].equals(base[KEY+['actual','actual_bonus','mins','actual_start']]),name
        q[f'xp__{name}']=p.xp.to_numpy(float)
        q[f'bonus__{name}']=p.xp_bonus.to_numpy(float)
    return q

def stats(predictions):
    q=pair(predictions)
    return P.paired_statistics(q,list(predictions),origin=8)

def means(predictions):
    q=pair(predictions);rows=[]
    for season in [*SEASONS,'alle']:
        g=q if season=='alle' else q[q.season==season]
        for row in P.summary(g,list(predictions)).to_dict('records'):
            name=row['model'];row.update(season=season,
                bonus_mse=((g[f'bonus__{name}']-g.actual_bonus)**2).mean())
            rows.append(row)
    return pd.DataFrame(rows)

def eff(values,q):return P.block_effect(values,q.season,q.gw,origin=8)

def mechanism(base,sub):
    base,sub=sort(base),sort(sub)
    assert base[KEY].equals(sub[KEY])
    np.testing.assert_array_equal(base.p_start,sub.p_start)
    rows=[]
    for season in [*SEASONS,'alle']:
        mask=np.ones(len(base),bool) if season=='alle' else (base.season==season).to_numpy()
        for label,lo,hi in [('all_<0.6',0,.6),('[0,0.2)',0,.2),('[0.2,0.4)',.2,.4),('[0.4,0.6)',.4,.6)]:
            idx=mask & base.p_start.ge(lo).to_numpy() & base.p_start.lt(hi).to_numpy()
            a,b=base[idx].copy(),sub[idx].copy()
            for metric,pa,pb,actual in [
                ('p_play',a.p_play,b.p_play,(a.mins>0).astype(float)),
                ('minutes',a.exp_minutes,b.exp_minutes,a.mins),
                ('p_sub',a.p_play-a.p_start,b.p_play-b.p_start,((a.actual_start==0)&(a.mins>0)).astype(float))]:
                ea,eb=pa-actual,pb-actual
                _,sea,nblocks=eff(ea,a);_,seb,_=eff(eb,a)
                delta,se,_=eff(eb**2-ea**2,a)
                rows.append(dict(season=season,p_start_group=label,metric=metric,n=len(a),blocks=nblocks,
                    predicted_baseline=pa.mean(),predicted_P2=pb.mean(),actual=actual.mean(),
                    bias_baseline=ea.mean(),se_bias_baseline=sea,bias_P2=eb.mean(),se_bias_P2=seb,
                    mse_baseline=(ea**2).mean(),mse_P2=(eb**2).mean(),delta_mse=delta,se_delta_mse=se))
    return pd.DataFrame(rows)

def premium(base,candidate,name):
    base,candidate=sort(base),sort(candidate)
    assert base[KEY].equals(candidate[KEY])
    rows=[];aggregates=[]
    for season in [*SEASONS,'alle']:
        scope=(base.season==season) if season!='alle' else pd.Series(True,index=base.index)
        for metric,col,truth in [('bonus','xp_bonus','actual_bonus'),('total','xp','actual')]:
            influences=[];n_total=0;sum_base=0.;sum_new=0.
            for label,lo,hi in [('8-10',80,100),('>=10',100,np.inf)]:
                for pos in ['FWD','MID']:
                    mask=scope & base.pre_value.ge(lo) & base.pre_value.lt(hi) & base.pos.eq(pos)
                    a,b=base[mask].copy(),candidate[mask].copy()
                    if a.empty:continue
                    ea=a[col]-a[truth];eb=b[col]-a[truth]
                    ma,sa,nb=eff(ea,a);mb,sb,_=eff(eb,a)
                    delta,se,_=eff(eb-ea,a)
                    d_mse,se_mse,_=eff(eb**2-ea**2,a)
                    # Delta-method influence for change in |cell mean error|.
                    influence=np.sign(mb)*eb-np.sign(ma)*ea
                    abschange,se_abs,_=eff(influence,a)
                    rows.append(dict(model=name,season=season,price_group=label,pos=pos,metric=metric,
                        n=len(a),blocks=nb,predicted_baseline=a[col].mean(),predicted_candidate=b[col].mean(),
                        actual=a[truth].mean(),bias_baseline=ma,se_bias_baseline=sa,bias_candidate=mb,
                        se_bias_candidate=sb,delta_bias=delta,se_delta_bias=se,
                        abs_bias_change=abschange,se_abs_bias_change=se_abs,
                        mse_baseline=(ea**2).mean(),mse_candidate=(eb**2).mean(),delta_mse=d_mse,se_delta_mse=se_mse))
                    h=a[['season','gw']].copy();h['influence']=influence.to_numpy();influences.append(h)
                    n_total+=len(a);sum_base+=len(a)*abs(ma);sum_new+=len(a)*abs(mb)
            h=pd.concat(influences,ignore_index=True)
            delta,se,nb=eff(h.influence,h)
            aggregates.append(dict(model=name,season=season,metric=metric,n=n_total,blocks=nb,
                wace_baseline=sum_base/n_total,wace_candidate=sum_new/n_total,delta_wace=delta,se_delta_wace=se))
    return pd.DataFrame(rows),pd.DataFrame(aggregates)

def assess(stat,cal,name,bonus=False):
    q=stat[stat.model==name]
    def row(metric,season):return q[(q.metric==metric)&(q.season==season)].iloc[0]
    a=row('mse','alle')
    criteria=dict(mse_reduction_ge_0p5pct=bool(a.relative_mse_reduction>=.005),
        total_mse_ge_3_block_se=bool(a.difference<0 and -a.difference>=3*a.se),
        total_mse_same_better_sign_all_seasons=all(row('mse',s).difference<0 for s in SEASONS),
        top10_top20_guard_pooled=all(row(k,'alle').difference>=-2*row(k,'alle').se for k in ['top10','top20']))
    if bonus:
        criteria['control_total_mse_better']=bool(row('mse',CONTROL).difference<0)
        criteria['control_top10_top20_guard']=all(row(k,CONTROL).difference>=-2*row(k,CONTROL).se for k in ['top10','top20'])
        criteria['bonus_mse_better_control_and_pooled']=all(row('bonus_mse',s).difference<0 for s in [CONTROL,'alle'])
        criteria['premium_bonus_wace_better_control_and_pooled']=all(float(cal[(cal.model==name)&(cal.season==s)&(cal.metric=='bonus')].delta_wace.iloc[0])<0 for s in [CONTROL,'alle'])
    normal=bool(all(criteria.values()))
    exception=False
    if bonus and name=='B1' and not normal:
        exception=bool(criteria['bonus_mse_better_control_and_pooled'] and
            criteria['premium_bonus_wace_better_control_and_pooled'] and
            criteria['top10_top20_guard_pooled'] and criteria['control_top10_top20_guard'] and
            not criteria['total_mse_ge_3_block_se'])
    # An unmet gate is not proof of harm; distinguish that from a rejected
    # candidate with guard failure or consistent adverse primary direction.
    harm=(not criteria['top10_top20_guard_pooled'] or
          (a.difference>0 and a.difference>=3*a.se))
    if bonus:
        harm=harm or not criteria['control_top10_top20_guard'] or not criteria['bonus_mse_better_control_and_pooled']
    status='GODKJENT' if normal or exception else ('AVVIST' if harm else 'UAVKLART')
    return dict(status=status,normal_requirements_met=normal,exception_used=exception,criteria=criteria)

def run():
    start=time.time()
    def deny(*a,**k):raise RuntimeError('Network prohibited')
    socket.socket.connect=deny;socket.create_connection=deny
    assert M.SUB_GIVEN_NO_START is False and E.BONUS_TAU_FIXED is None
    source_paths=[R/'src'/n for n in ['eval_engine.py','evaluate_pred.py','minutes.py','expected_points.py','team_strength.py']]
    source_hash={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    prereg=json.loads((O/'p1p2_metode_for_kjoring.json').read_text())
    for path,h in prereg['source_sha256'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h
    bases=[];subs=[];gridparts=[];loaded=[]
    # Development phase: CONTROL is not loaded, predicted, inspected or scored.
    for season in DEV:
        loaded += [season,X.PRIOR_OF[season]]
        cases={f'tau{tau}':fixed(float(tau)) for tau in GRID}
        b=run_season(season,cases=cases);bases.append(b)
        b.to_csv(O/f'p1p2_{season}_base_grid.csv.gz',index=False,compression='gzip')
        for tau in GRID:
            gridparts.append(dict(season=season,tau=tau,n=len(b),
                bonus_sse=float(((b[f'bonus__tau{tau}']-b.actual_bonus)**2).sum()),
                bonus_mse=float(((b[f'bonus__tau{tau}']-b.actual_bonus)**2).mean())))
        s=run_season(season,sub=True);subs.append(s)
        s.to_csv(O/f'p1p2_{season}_P2.csv.gz',index=False,compression='gzip')
    grid=pd.DataFrame(gridparts)
    pooled=grid.groupby('tau',as_index=False).agg(n=('n','sum'),bonus_sse=('bonus_sse','sum'))
    pooled['bonus_mse']=pooled.bonus_sse/pooled.n;pooled['season']='utvikling_samlet'
    grid=pd.concat([grid,pooled],ignore_index=True)
    grid.to_csv(O/'p1p2_tau_utvikling.csv',index=False)
    selected=int(pooled.sort_values(['bonus_mse','tau']).iloc[0].tau)
    assert CONTROL not in loaded
    dump('p1_tau_last.json',dict(locked_utc=now(),tau=selected,grid=list(GRID),
        development=list(DEV),objective='pooled player-fixture bonus-MSE, GW8-38',
        control_not_loaded=True,load_history=loaded,source_sha256=source_hash,
        development_table_sha256=hashlib.sha256((O/'p1p2_tau_utvikling.csv').read_bytes()).hexdigest()))
    print('TAU LOCKED BEFORE CONTROL:',selected,now(),flush=True)
    # Only the locked tau is evaluated on the control year.
    b=run_season(CONTROL,cases={f'tau{selected}':fixed(float(selected))});bases.append(b)
    b.to_csv(O/f'p1p2_{CONTROL}_base_locked.csv.gz',index=False,compression='gzip')
    s=run_season(CONTROL,sub=True);subs.append(s)
    s.to_csv(O/f'p1p2_{CONTROL}_P2.csv.gz',index=False,compression='gzip')
    base=pd.concat(bases,ignore_index=True);sub=pd.concat(subs,ignore_index=True)
    b1=base.copy();b1['xp']=b1[f'xp__tau{selected}'];b1['xp_bonus']=b1[f'bonus__tau{selected}']
    predictions={'baseline':base,'P2':sub,'B1':b1}
    perf=stats(predictions)
    cal,aggregates=premium(base,b1,'B1')
    decisions=dict(P2=assess(perf,aggregates,'P2'),B1=assess(perf,aggregates,'B1',bonus=True))
    dump('p1p2_beslutning_forelopig.json',dict(tau=selected,**decisions))
    if all(decisions[n]['status']=='GODKJENT' for n in ['P2','B1']):
        combo=pd.concat([run_season(season,sub=True,tau=float(selected)) for season in SEASONS],ignore_index=True)
        predictions['B1+P2']=combo
        perf=stats(predictions)
        cc,ac=premium(base,combo,'B1+P2');cal=pd.concat([cal,cc],ignore_index=True)
        aggregates=pd.concat([aggregates,ac],ignore_index=True)
        decisions['B1+P2']=assess(perf,aggregates,'B1+P2',bonus=True)
        # Report incremental effects as well as effects relative to baseline.
        incremental=[]
        for ref in ['B1','P2']:
            st=P.paired_statistics(pair({ref:predictions[ref],'B1+P2':combo}),[ref,'B1+P2'],origin=8)
            incremental.append(st)
        pd.concat(incremental,ignore_index=True).to_csv(O/'p1p2_kombinasjon_inkrement.csv',index=False)
    else:
        decisions['B1+P2']=dict(status='IKKE KJØRT',reason='Both individual candidates must pass first')
    perf.to_csv(O/'p1p2_parvis.csv',index=False)
    means(predictions).to_csv(O/'p1p2_nivaer.csv',index=False)
    cal.to_csv(O/'p1p2_premium.csv',index=False)
    aggregates.to_csv(O/'p1p2_premium_wace.csv',index=False)
    mechanism(base,sub).to_csv(O/'p1p2_minuttkalibrering.csv',index=False)
    # Check the frame-prior refactor against the pre-existing P0 baseline only
    # after the selection lock and control phase have both completed.
    reference=pd.read_csv(O/'p0_prediksjoner.csv.gz');reference=reference[reference.gw>=8]
    q=sort(base).merge(reference,on=KEY,suffixes=('_new','_old'),validate='one_to_one')
    assert len(q)==len(base)==len(reference)
    parity=q.assign(abs_delta=(q.xp_new-q.xp_old).abs()).groupby('season').abs_delta.agg(['size','max','mean']).reset_index()
    parity.to_csv(O/'p1p2_p0_paritet.csv',index=False)
    assert parity['max'].max()<1e-10
    allrows=[]
    for name,p in predictions.items():
        r=p[KEY+['name','pos','pre_value','xp','xp_bonus','actual','actual_bonus','mins','actual_start','p_start','p_play','exp_minutes']].copy()
        r['model']=name;allrows.append(r)
    pd.concat(allrows,ignore_index=True).to_csv(O/'p1p2_prediksjoner.csv.gz',index=False,compression='gzip')
    assert all(hashlib.sha256((R/path).read_bytes()).hexdigest()==h for path,h in source_hash.items()),'Model source changed during measurement'
    assert E.BONUS_TAU_FIXED is None and M.SUB_GIVEN_NO_START is False
    dump('p1p2_beslutning.json',dict(tau=selected,**decisions,B2=dict(status='IKKE KJØRT',reason='Only B1 is implemented/requested; B2 is conditional, not an automatic second tuning step')))
    dump('p1p2_manifest.json',dict(seconds=time.time()-start,finished_utc=now(),rows_per_model=len(base),
        seasons=list(SEASONS),gws='8-38',source_sha256=source_hash,python=sys.version,
        flags_restored=dict(SUB_GIVEN_NO_START=M.SUB_GIVEN_NO_START,BONUS_TAU_FIXED=E.BONUS_TAU_FIXED)))
    print(json.dumps(decisions,indent=2));print('DONE SECONDS',time.time()-start,flush=True)

if __name__=='__main__':run()
