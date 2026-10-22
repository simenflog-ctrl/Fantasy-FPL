"""Independent read-only solver checks for D0; never runs optimize.main()."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
import pandas as pd
O=Path(__file__).resolve().parent;R=O.parents[2]
sys.path.insert(0,str(R/'src'))
import optimize as A


def case(extras=1):
    positions=['GK']*2+['DEF']*5+['MID']*5+['FWD']*3
    pool=pd.DataFrame([dict(element=i+1,web_name=f'P{i+1}',pos=ps,team=f'T{i%5}',price=1.) for i,ps in enumerate(positions)])
    for j in range(extras):
        base=pool[pool.element==8+j].iloc[0]
        pool=pd.concat([pool,pd.DataFrame([dict(element=16+j,web_name=f'New{j}',pos='MID',team=base.team,price=1.)])],ignore_index=True)
    return pool


def run():
    results={}
    # One attractive replacement is affordable only if the old inflated sale value is used.
    pool=case();pool.loc[pool.element==8,'price']=6.;pool.loc[pool.element==16,'price']=6.1
    grid=pd.DataFrame(0.,index=pool.element,columns=[8]);grid.loc[16,8]=100.
    m,v,status=A.solve(pool,grid,[8],list(range(1,16)),.2,set(),{8:5.8},2)
    assert status=='Optimal' and v['buy'][16][8].value()==0
    m2,v2,status2=A.solve(pool,grid,[8],list(range(1,16)),.2,set(),{8:6.},2)
    assert status2=='Optimal' and v2['buy'][16][8].value()==1
    results['sale_price_binding']='PASS: 5.8 sale blocks unaffordable purchase; 6.0 permits it'
    # Two genuine FT enter the MILP (not just the price/FT helper tests).
    pool=case(extras=2);grid=pd.DataFrame(0.,index=pool.element,columns=[8]);grid.loc[[16,17],8]=100.
    m,v,status=A.solve(pool,grid,[8],list(range(1,16)),0.,set(),{},2)
    assert status=='Optimal' and sum(v['buy'][p][8].value() for p in [16,17])==2
    assert v['hits'][8].value()==0
    results['two_ft_in_solver']='PASS: two upgrades, zero hits'
    # Independently maximize FT after a forced WC with no transfers.
    grid=pd.DataFrame(0.,index=pool.element,columns=[8,9])
    m,v,status=A.solve(pool,grid,[8,9],list(range(1,16)),0.,{'wildcard'},{},3)
    m+=v['wc'][8]==1
    for p in pool.element:m+=v['buy'][p][8]==0
    next_ft=m.variablesDict()['ft_9'];m.setObjective(next_ft)
    m.solve(A.pulp.PULP_CBC_CMD(msg=0,timeLimit=10))
    assert A.pulp.LpStatus[m.status]=='Optimal' and next_ft.value()==3
    results['wc_preserves_three_ft']='PASS: upper bound and achievable next FT = 3, not 1 or 4'
    # Rule helper cases beyond gw08: hit, cap, free hit and legacy reset flag.
    history={'chips':[], 'current':[dict(event=1,event_transfers=0),dict(event=2,event_transfers=3)]}
    assert A.free_transfers(history,3)==1
    history={'chips':[], 'current':[dict(event=g,event_transfers=0) for g in range(1,12)]}
    assert A.free_transfers(history,12)==5
    history['chips']=[dict(name='freehit',event=10)];history['current'][9]['event_transfers']=12
    assert A.free_transfers(history,11)==5
    saved=A.CHIP_PRESERVES_FT
    try:
        A.CHIP_PRESERVES_FT=False
        assert A.free_transfers(history,11)==1
    finally:A.CHIP_PRESERVES_FT=saved
    results['ft_edge_cases']='PASS: hits, cap=5, FH preservation, legacy reset'
    (O/'d0_kontroll.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))

if __name__=='__main__':run()
