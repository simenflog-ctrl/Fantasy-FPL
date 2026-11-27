"""Supplementary paired diagnostics; reads only artifacts/local historical data."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
import pandas as pd
O=Path(__file__).resolve().parent
R=O.parents[2]

def run():
    p=pd.read_csv(O/'prediksjoner.csv.gz')
    rows=[]
    for season,g in p.groupby('season'):
        a=g[g.model=='evaluate_pred']
        for model in ['produksjon_offline','form_3gw']:
            b=g[g.model==model]
            z=a.merge(b,on=['name','gw','fixture'],suffixes=('_a','_b'),validate='one_to_one')
            assert np.array_equal(z.actual_a,z.actual_b)
            for metric in ['mae','mse']:
                da=(z.xp_b-z.actual_b).abs()-(z.xp_a-z.actual_a).abs() if metric=='mae' else (z.xp_b-z.actual_b)**2-(z.xp_a-z.actual_a)**2
                c=z.assign(da=da).groupby('gw').da.agg(['sum','size'])
                cluster=c['sum']-da.mean()*c['size']
                se=np.sqrt(len(c)/(len(c)-1)*(cluster**2).sum())/len(z)
                rows.append(dict(season=season,model=model,reference='evaluate_pred',metric=metric,n=len(z),difference=da.mean(),se_gw=se))
    pd.DataFrame(rows).to_csv(O/'parvis_diagnostikk.csv',index=False)
    rows=[]
    for (model,season,name),g in p[p.model!='form_3gw'].groupby(['model','season','name']):
        if not ('Haaland' in name or 'Bruno' in name and 'Fernandes' in name):continue
        for metric,pc,ac in [('total','xp','actual'),('bonus','xp_bonus','actual_bonus')]:
            d=g[pc]-g[ac]
            rows.append(dict(model=model,season=season,name=name,metric=metric,n=len(g),predicted=g[pc].mean(),actual=g[ac].mean(),bias=d.mean(),se_gw=d.std(ddof=1)/np.sqrt(len(g))))
    pd.DataFrame(rows).to_csv(O/'spillerkalibrering.csv',index=False)
    rows=[]
    for s in ['2022-23','2023-24','2024-25','2025-26']:
        raw=pd.read_csv(R/f'data/cache/vaastav/{s}/gws/merged_gw.csv')
        clean=raw.drop_duplicates()
        bonus=clean.groupby('fixture').bonus.sum()
        rows.append(dict(season=s,raw_rows=len(raw),duplicate_rows=raw.duplicated().sum(),fixtures=bonus.size,bonus_per_fixture=bonus.mean(),fixtures_bonus_above6=(bonus>6).sum(),players=clean.element.nunique()))
    pd.DataFrame(rows).to_csv(O/'datakontroll.csv',index=False)

if __name__=='__main__':run()
