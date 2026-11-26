#!/usr/bin/env python3
"""Focused review of Claude's GW12 proposal; uses the frozen GW12 model."""
import csv, sys
from pathlib import Path
import numpy as np

O=Path(__file__).resolve().parent
sys.path.insert(0,str(O))
import modell as m
import modell_r2 as r2

FH=15
m.FH=FH
r2.m=m;r2.O=O;r2.C=O/'checkpoints';r2.load_templates()
CURRENT={'Trafford':385,'Tzolakis':572,'Gabriel':4,'Van Hecke':112,'De Cuyper':115,
         'Dasilva':176,'Silva':566,'Ødegaard':15,'Tavernier':68,'Groß':124,
         'Rudoni':183,'Mbeumo':427,'Barry':249,'Isak':379,'Haaland':411}
def idx(name): return m.ix[CURRENT[name]] if name in CURRENT else m.named(name)
def squad(changes):
    s=set(map(int,m.ORIG))
    for out,inn in changes:
        s.remove(idx(out));s.add(idx(inn))
    a=m.ordered(s);m.legal(a)
    return a
def trans(changes):
    a=squad(changes)
    return m.transact(m.ORIG,a,m.SALES.copy(),4)

PLANS={
 'A':[],
 'B':[('Silva','Muharemović')],
 'C':[('Ødegaard','Justin'),('Dasilva','E.Le Fée')],
 'P':[('Ødegaard','E.Le Fée'),('Dasilva','Konsa')],
 'G_keep':[('Dasilva','Bogle'),('Silva','Justin')],
}
rows=[];plans={}
def metricrow(kind,plan,values,bank='',ft=''):
    vals=np.array(values)
    total19=(dict(codex_R12_R19='',repo_hybrid_R12_R19='',blend_R12_R19='')
             if kind=='fixed_R12_R15' else
             dict(codex_R12_R19=vals[:,0].sum(),repo_hybrid_R12_R19=vals[:,1].sum(),blend_R12_R19=vals.mean(axis=1).sum()))
    rows.append(dict(type=kind,plan=plan,bank=bank,free_transfers=ft,
       codex_R12=vals[0,0],repo_hybrid_R12=vals[0,1],blend_R12=vals[0].mean(),
       codex_R12_R15=vals[:4,0].sum(),repo_hybrid_R12_R15=vals[:4,1].sum(),blend_R12_R15=vals[:4].mean(axis=1).sum(),
       **total19))

def fixed_values(s,sv,cash):
    vals=[]
    for t,g in enumerate(range(12,16)):
        active=s if g!=FH else m.renew(g,s,sv,cash,m.BLEND,m.PP,m.PURCHASE[:,t],fh=True,bb=99)
        z=m.select(active,m.BLEND[:,t],m.PP[:,t],m.POS,m.LUT,m.PERMS,True,False)
        vals.append((m.M[:,active,t]*z[1][None,:]).sum(axis=1))
    return np.array(vals)

def trajectory(s):
    p=m.trajectory(s,ft0=3,fh=FH,full=True,record=True)
    return np.array(p['normal']),p

print('Calculating base plans',flush=True)
for name,changes in PLANS.items():
    s,sv,cash=trans(changes)
    f=fixed_values(s,sv,cash);metricrow('fixed_R12_R15',name,f,cash/10,3)
    vals,p=trajectory(s);plans[name]=(s,sv,cash,vals,p)
    metricrow('adaptive_R12_R19',name,vals,cash/10,3)

def add_delta(label,left,right):
    a=plans[left][3];b=plans[right][3];d=a-b
    rows.append(dict(type='adaptive_delta',plan=label,
        codex_R12=d[0,0],repo_hybrid_R12=d[0,1],blend_R12=d[0].mean(),
        codex_R12_R15=d[:4,0].sum(),repo_hybrid_R12_R15=d[:4,1].sum(),blend_R12_R15=d[:4].mean(axis=1).sum(),
        codex_R12_R19=d[:,0].sum(),repo_hybrid_R12_R19=d[:,1].sum(),blend_R12_R19=d.mean(axis=1).sum()))
add_delta('P_minus_A','P','A')
add_delta('P_minus_G_keep','P','G_keep')
add_delta('G_keep_minus_A','G_keep','A')

print('Searching low-cost Dasilva defenders',flush=True)
cheap=[]
base=set(map(int,m.ORIG));dasilva=idx('Dasilva')
for j in m.UI:
    j=int(j)
    if m.POS[j]!=2 or m.COST[j]>44 or j in base: continue
    a=m.ordered(base-{dasilva}|{j})
    try: m.legal(a);s,sv,cash=m.transact(m.ORIG,a,m.SALES.copy(),4)
    except (AssertionError,ValueError): continue
    v,p=trajectory(s)
    cheap.append((float(v.mean(axis=1).sum()),m.E[m.ids[j]]['web_name'],cash/10,v,s,sv,cash))
cheap.sort(reverse=True,key=lambda z:z[0])
for rank,(score,nm,cash,v,s,sv,_) in enumerate(cheap,1):
    metricrow('one_Dasilva_DEF_le_4.4',nm,v,cash,3)
    rows[-1]['rank_blend']=rank
bestcheap=cheap[0]

for target in ['Muharemović','Konsa']:
    tag='Dasilva+Silva_to_Justin+'+target
    try:
        s,sv,cash=trans([('Dasilva','Justin'),('Silva',target)])
        v,p=trajectory(s);metricrow('two_transfer_budget_test',tag,v,cash/10,3);rows[-1]['status']='affordable'
    except (AssertionError,ValueError) as e:
        rows.append(dict(type='two_transfer_budget_test',plan=tag,status='not affordable',reason=str(e)))

oldpath=O/'kontroll_r12.csv'
if '--reuse-sim' in sys.argv and oldpath.exists():
    rows.extend(r for r in csv.DictReader(oldpath.open()) if r['type']=='paired_injury_2pct_P_vs_G_keep')
else:
    print('Running paired 2% worlds for P vs G_keep (100)',flush=True)
    raw=np.load(O/'checkpoints'/'injury_worlds.npz');U=raw['U'];dur=raw['duration']
    paired=[]
    for draw in range(100):
        world=np.zeros((m.H,m.N),dtype=np.int16);end=np.zeros(m.N,dtype=np.int16)
        for t in range(1,m.H):
            new=(end<=t)&(U[draw,t]<.02);end[new]=t+dur[draw,t,new];world[t]=end
        vP=np.array(m.trajectory(plans['P'][0],ft0=3,fh=FH,world=world,full=True,record=False)['normal']).sum(axis=0)
        vG=np.array(m.trajectory(plans['G_keep'][0],ft0=3,fh=FH,world=world,full=True,record=False)['normal']).sum(axis=0)
        d=vP-vG
        paired.append(dict(world=draw,codex_P=vP[0],repo_hybrid_P=vP[1],codex_G=vG[0],repo_hybrid_G=vG[1],delta_codex=d[0],delta_repo_hybrid=d[1],delta_blend=d.mean()))
        if (draw+1)%10==0: print(f'  {draw+1}/100',flush=True)
    for model,key in [('codex','delta_codex'),('repo_hybrid','delta_repo_hybrid'),('blend','delta_blend')]:
        a=np.array([r[key] for r in paired])
        rows.append(dict(type='paired_injury_2pct_P_vs_G_keep',plan=model,n=100,mean_delta=a.mean(),p10=np.quantile(a,.1),p90=np.quantile(a,.9),paired_SE=a.std(ddof=1)/np.sqrt(100),win_rate=(a>0).mean()))

s=plans['G_keep'][0];z=m.select(s,m.BLEND[:,0],m.PP[:,0],m.POS,m.LUT,m.PERMS,True,False);xi=z[2]
caps=[]
for c in xi:
    choices=[]
    for v in xi:
        if c==v:continue
        extra=m.M[:,s[c],0]+(1-m.PP[s[c],0])*m.M[:,s[v],0]
        choices.append((float(extra.mean()),int(c),int(v),extra))
    caps.append(max(choices,key=lambda q:q[0]))
caps.sort(reverse=True,key=lambda q:q[0])
for rank,(blend,c,v,extra) in enumerate(caps[:4],1):
    rows.append(dict(type='captain_G_keep_R12',rank=rank,captain=m.E[m.ids[s[c]]]['web_name'],vice=m.E[m.ids[s[v]]]['web_name'],
        codex_captain_extra=extra[0],repo_hybrid_captain_extra=extra[1],blend_captain_extra=blend,
        codex_player_xp=m.M[0,s[c],0],repo_hybrid_player_xp=m.M[1,s[c],0],blend_player_xp=m.BLEND[s[c],0]))

out=O/'kontroll_r12.csv'
fields=list(dict.fromkeys(k for r in rows for k in r))
with out.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('WROTE',out)
print('plan totals:')
for name in PLANS: print(name,'adaptive',plans[name][3].sum(axis=0))
print('best cheap defender',bestcheap[1],bestcheap[0], 'bank',bestcheap[2])
print('paired',[(r['plan'],r.get('mean_delta')) for r in rows if r['type']=='paired_injury_2pct_P_vs_G_keep'])
print('captains',[(r.get('captain'),r.get('vice'),r.get('blend_captain_extra')) for r in rows if r['type']=='captain_G_keep_R12'])
