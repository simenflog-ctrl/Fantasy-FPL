#!/usr/bin/env python3
"""GW11 round-two BB audit. Same frozen model, squads, policy and injury worlds.
Run with Anaconda; resumable ~3 minute batch, all writes under codex/.
"""
import argparse,hashlib,json,time
import numpy as np
import modell as m
O=m.O;C=O/'checkpoints';MODELS=['codex','repo_hybrid','blend']
def read(n):return json.loads((O/n).read_text())
def squad(ps):return m.ordered(m.ix[p] for p in ps)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=int,default=180);args=parser.parse_args()
    endtime=time.monotonic()+min(420,args.seconds)
    assert read('status.json')['status']=='fullført','Finish assignment 1 first'
    for fn,h in read('prognose_sha256.json').items():assert hashlib.sha256((O/fn).read_bytes()).hexdigest()==h
    m.TEMPLATES.extend(squad(read(f'checkpoints/template_{g}_{k}.json')) for g in range(12,20) for k in range(3))
    plans=read('planer.json')['hoved'];initial={k:squad(plans[k]['rows'][0]['tropp']) for k in ['A','B']}
    assert m.name(set(m.ORIG)-set(initial['B']))=='Muharemović'
    assert m.name(set(initial['B'])-set(m.ORIG))=='Van Hecke'
    raw=np.load(C/'injury_worlds.npz');U=raw['U'];duration=raw['duration']
    assert U.shape==(100,m.H,m.N)
    nominal={}
    for fh in [12,15]:
        for k,s in initial.items():nominal[fh,k]=np.array(m.trajectory(s,ft0=3,fh=fh,full=True)['alle_BB'])
    def resultfile(fh,prob,d,k):
        return f'checkpoints/sim_{int(prob*100)}_{d}_{k}.json' if fh==15 else f'checkpoints/bb_fh{fh}_{int(prob*100)}_{d}_{k}.json'
    def summarize():
        out=[]
        for fh in [12,15]:
            for prob in [.01,.02]:
                for k in initial:
                    files=[resultfile(fh,prob,d,k) for d in range(100)]
                    rr=[read(f) for f in files if (O/f).exists()]
                    if not rr:continue
                    a=np.array([r['alle_BB'] for r in rr])
                    for ga,gb in [(11,18),(11,19),(18,19)]:
                        delta=a[:,ga-m.FIRST,:]-a[:,gb-m.FIRST,:];d0=nominal[fh,k][ga-m.FIRST]-nominal[fh,k][gb-m.FIRST]
                        for j,model in enumerate(MODELS):
                            d=delta[:,j] if j<2 else delta.mean(axis=1)
                            out.append(dict(alternativ=k,FH=fh,p=prob,BB_a=ga,BB_b=gb,poengsett=model,delta_snitt=d.mean(),p10=np.quantile(d,.1),p90=np.quantile(d,.9),MC_SE=d.std(ddof=1)/np.sqrt(len(d)) if len(d)>1 else 0,andel_a_bedre=(d>1e-9).mean(),delta_uten_nye_skader=d0[j] if j<2 else d0.mean(),n=len(d)))
        if out:m.save('bb_skade.csv',out)
        return out
    summarize()
    for fh in [12,15]:
        for prob in [.01,.02]:
            for d in range(100):
                world=np.zeros((m.H,m.N),dtype=np.int16);end=np.zeros(m.N,dtype=np.int16)
                for t in range(1,m.H):
                    new=(end<=t)&(U[d,t]<prob);end[new]=t+duration[d,t,new];world[t]=end
                for k,s in initial.items():
                    fn=resultfile(fh,prob,d,k)
                    if not (O/fn).exists():
                        p=m.trajectory(s,ft0=3,fh=fh,world=world,record=False)
                        m.jsave(fn,dict(FH=fh,p=prob,verden=d,alternativ=k,alle_BB=p['alle_BB']))
                    if time.monotonic()>=endtime:
                        summarize();m.jsave('bb_status.json',dict(status='pågår',FH=fh,p=prob,verden=d));return
                if (d+1)%10==0:summarize();print('BB audit FH',fh,'rate',prob,'worlds',d+1,flush=True)
    out=summarize();assert len(out)==72 and all(r['n']==100 for r in out)
    m.jsave('bb_status.json',dict(status='fullført',FH=[12,15],planer=['A','B'],rater=[.01,.02],verdener=100,rader=len(out),modellendringer=False))
    print('BB audit complete: 72 paired comparisons; all n=100',flush=True)
if __name__=='__main__':main()
