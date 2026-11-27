"""Read-only before/after check on frozen 2026/27 production input files."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,types,socket
import numpy as np
import pandas as pd
O=Path(__file__).resolve().parent;R=O.parents[2]
sys.path.insert(0,str(R/'src'))
import expected_points as E

def run():
    def deny(*a,**k):raise RuntimeError('offline only')
    socket.socket.connect=deny;socket.create_connection=deny
    source=json.loads((O/'p0_original_sources.json').read_text())['src/expected_points.py']
    old=types.ModuleType('original_expected_points');old.__file__=str(R/'src/expected_points.py')
    exec(compile(source,old.__file__,'exec'),old.__dict__)
    old.LAST_SEASON=str(R/'data/cache/vaastav/2025-26/cleaned_players.csv')
    pm,mins,teams,proj,bs=old.load()
    tm=pd.read_csv(R/'data/derived/team_matches.csv')
    rates=old.per90_rates(pm,mins,bs)
    rates['dc_rate']=rates.element.map(old.dc_hit_rates(pm,rates)).fillna(0.)
    tau=old.fit_bonus_temperature(pm);scale=old.calibrate_xg_to_goals(tm,proj);disp=old.fit_dispersion(tm)
    a=old.expected_points(rates,teams,proj,tau,scale,disp)
    b,diag=E.forecast(pm,mins,teams,proj,bs,tm)
    key=['element','gw','fixture']
    z=a.merge(b,on=key,suffixes=('_old','_new'),validate='one_to_one')
    assert len(z)==len(a)==len(b)
    avg=teams.set_index('short_name').xg_vs_avg
    rr=rates.set_index('element')
    pp=proj.set_index(['team','gw','fixture'])
    expected=[]
    for r in z.itertuples():
        p=rr.loc[r.element];f=pp.loc[(r.team_old,r.gw,r.fixture)]
        expected.append(4*p.expected_goals90*p.exp_minutes/90*f.xg_for/max(avg[p.team],1e-6) if p.pos=='GK' else 0.)
    z['expected_delta']=expected
    z['actual_delta']=z.xp_new-z.xp_old
    z['unexpected_delta']=z.actual_delta-z.expected_delta
    assert z.unexpected_delta.abs().max()<1e-12
    for c in ['xp_bonus','xp_dc','xp_defence','exp_minutes']:
        np.testing.assert_array_equal(z[c+'_old'],z[c+'_new'])
    z[key+['pos_new','actual_delta','expected_delta','unexpected_delta']].to_csv(O/'p0_produksjon_regresjon.csv',index=False)
    print('PRODUCTION REGRESSION OK',len(z),'rows; max unexpected delta',z.unexpected_delta.abs().max(),
        '; max GK delta',z.actual_delta.abs().max(),'; diagnostics',diag)

if __name__=='__main__':run()
