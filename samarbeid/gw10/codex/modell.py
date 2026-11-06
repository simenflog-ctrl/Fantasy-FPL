#!/usr/bin/env python3
"""GW10 standalone successor to GW09 modell_r2.py.
Exact independent-appearance autosubs and paired adaptive injury worlds.
R10-R19; frozen local data; no network/install or writes outside this directory.
minutter_antatt.csv is input and is created only if absent.
"""
import csv, json, math, hashlib, time
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
import itertools
from numba import njit
import pulp
O=Path(__file__).resolve().parent; D=O.parent/'data'; IN=O/'input'
def read(p): return json.loads(p.read_text())
def rows(p): return list(csv.DictReader(p.open()))
def save(n,rs):
    assert rs
    with (O/n).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def jwrite(n,obj): (O/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
b=read(D/'bootstrap.json'); E={e['id']:e for e in b['elements']}; ids=sorted(E); ix={p:i for i,p in enumerate(ids)}; N=len(ids)
T={t['id']:t['short_name'] for t in b['teams']}; sc=b['game_config']['scoring']; fx=read(D/'fixtures.json'); sales=read(D/'salgspriser.json')
cost={p:e['now_cost'] for p,e in E.items()}; orig=frozenset(r['id'] for r in sales); osell={r['id']:round(10*r['salgspris']) for r in sales}
assert sum(osell.values())+4==995 and sc['goals_scored']['GKP']==10
history={int(p.stem):read(p) for p in (D/'element_summary').glob('*.json')}
kinds={1:'GKP',2:'DEF',3:'MID',4:'FWD'}; COUNTS={1:2,2:5,3:5,4:3}; GWS=list(range(10,20)); H=len(GWS)
forms=[(d,m,10-d-m) for d in range(3,6) for m in range(2,6) if 1<=10-d-m<=3]
name=lambda ps:', '.join(E[int(p)]['web_name'] for p in ps)
def named(n): return next((p for p,e in E.items() if e['web_name']==n),None)
# Frozen bot inputs; no mutable data/derived reads after initial snapshot.
pm=[r for r in rows(IN/'player_matches.csv') if int(r['gw'])<=9]; agg=defaultdict(lambda:[0.,0.]); tx=defaultdict(float)
for r in pm:
    p=int(r['element']);agg[p][0]+=float(r['minutes']);agg[p][1]+=float(r['expected_goals']);tx[int(r['fixture']),int(r['team'])]+=float(r['expected_goals'])
assert all(agg[p][0]==e['minutes'] and abs(agg[p][1]-float(e['expected_goals']))<.05 for p,e in E.items())
tm=defaultdict(lambda:[0.,0.,0])
for f in fx:
    if not f['finished'] or not f['event'] or f['event']>9:continue
    for t,op in [(f['team_h'],f['team_a']),(f['team_a'],f['team_h'])]:
        tm[t][0]+=tx[f['id'],t];tm[t][1]+=tx[f['id'],op];tm[t][2]+=1
mean=sum(v[0] for v in tm.values())/sum(v[2] for v in tm.values())
strength={t:((v[0]+7*mean)/(v[2]+7)/mean,(v[1]+7*mean)/(v[2]+7)/mean) for t,v in tm.items()}
save('lagstyrke.csv',[dict(lag=T[t],xG=v[0],xGA=v[1],kamper=v[2],angrep=strength[t][0],forsvar=strength[t][1]) for t,v in sorted(tm.items())])
# News supplied by user; quantitative effects below are model assumptions, not news facts.
blocked_names={'João Pedro','Saka','Semenyo','Lacroix','Cash','Shaw','James','Šeško','Frimpong'}
blocked={p for p,e in E.items() if e['status'] in ['u','n','i','s'] or e.get('chance_of_playing_next_round')==0}
roles={}
for p,e in E.items():
    hh=history.get(p,{}).get('history',[]);w=[.5**((9-r['round'])/4) for r in hh]
    ps=(sum(a*r['starts'] for a,r in zip(w,hh))+.35)/(sum(w)+.7) if hh else (e['starts']+.35)/9.7
    starts=[r for r in hh if r['starts']];subs=[r for r in hh if not r['starts'] and r['minutes']>0]
    mg=sum(r['minutes'] for r in starts)/len(starts) if starts else min(90,e['minutes']/max(1,e['starts']))
    subprob=len(subs)/max(1,len(hh)-len(starts)); submin=sum(r['minutes'] for r in subs)/max(1,len(subs))
    p60cond=(sum(r['minutes']>=60 for r in starts)+4.5)/(len(starts)+5)
    roles[p]=(ps,mg,subprob,submin,p60cond)
mp=O/'minutter_antatt.csv'
if not mp.exists():
    rr=[]
    for p,e in E.items():
        ps,mg,subprob,submin,p60c=roles[p]
        for lo,hi in [(10,10),(11,19)]:
            av=0 if p in blocked else ((e.get('chance_of_playing_next_round') or 50)/100 if e['status']=='d' else 1)
            q=ps*av;mi=(ps*mg+(1-ps)*subprob*submin)*av
            source='Modell: vektede starter R1–9 + prior; egne min/start; API 6. nov'
            if p in blocked:source+='; ute/kjøpsforbud, ukjent retur: null til R19'
            elif e['status']=='d':source+='; API d-prosent holdt konstant, ukjent friskdato'
            n=e['web_name']
            if lo==10 and T[e['team']] in ['BHA','BOU','SUN','CRY'] and p not in blocked:
                q*=.95;mi*=.95
                source+='; torsdag Europa/søndag liga: 5% relativ reduksjon (antakelse, ikke bekreftet rotasjon)'
            if lo==10 and n=='Groß':
                q*=.85;mi*=.85;source+='; fot-smell: ytterligere 15% relativ reduksjon, diagnose ukjent'
            if lo==10 and n in ['Grealish','Crooks']:
                q=mi=0;source+='; kjent fravær R10 fra bruker'
            if n in ['Morita','Toth']:
                q=mi=0;source+='; kjent fravær, ukjent retur: forsiktig null til R19'
            rr.append(dict(id=p,navn=n,lag=T[e['team']],gw_fra=lo,gw_til=hi,p_start=round(q,4),forventede_min=round(mi,2),kilde=source))
    save(mp.name,rr)
md={}
for r in rows(mp):
    for g in range(int(r['gw_fra']),int(r['gw_til'])+1):
        assert (int(r['id']),g) not in md,'Overlapping minute rows'
        md[int(r['id']),g]=r
assert set(md)=={(p,g) for p in ids for g in GWS}
# Same shrunk historical rate model as R2/R3; no fit to one realized GW8 result.
stats=['expected_goals','expected_assists','bonus','yellow_cards','red_cards','own_goals','penalties_saved','penalties_missed','saves'];pri={};rates={};prior_sources={};dc_rates={}
for k in COUNTS:
    ee=[e for e in E.values() if e['element_type']==k and e['minutes']>0];m=sum(e['minutes'] for e in ee)
    pri[k]={s:sum(float(e.get(s,0)) for e in ee)*90/m for s in stats}
dcbase={}
for k in COUNTS:
    hh=[r for p,h in history.items() if E[p]['element_type']==k for r in h.get('history',[]) if r['minutes']>=60];threshold=10 if k==2 else 12
    dcbase[k]=sum(r.get('defensive_contribution',0)>=threshold for r in hh)/max(1,len(hh)) if k!=1 else 0
for p,e in E.items():
    k=e['element_type'];past=[r for r in history.get(p,{}).get('history_past',[]) if r.get('minutes',0)>=450 and r['season_name']<'2026/27'][-2:];ws=[.5**(len(past)-1-j) for j in range(len(past))];prior={}
    for s in stats:
        valid=[(w,r) for w,r in zip(ws,past) if r.get(s) is not None]
        prior[s]=sum(w*float(r[s]) for w,r in valid)*90/sum(w*r['minutes'] for w,r in valid) if valid else pri[k][s]
    weight=540 if past else 270;rates[p]={s:(float(e.get(s,0))*90+weight*prior[s])/(e['minutes']+weight) for s in stats};prior_sources[p]=[r['season_name'] for r in past]
    hh=[r for r in history.get(p,{}).get('history',[]) if r['minutes']>=60];threshold=10 if k==2 else 12
    dc_rates[p]=(sum(r.get('defensive_contribution',0)>=threshold for r in hh)+3*dcbase[k])/(len(hh)+3) if k!=1 else 0

def forecast(p,g):
    e=E[p];k=e['element_type'];po=kinds[k];r=rates[p];mm=md[p,g];ps=float(mm['p_start']);mi=float(mm['forventede_min'])
    assert 0<=ps<=1 and 0<=mi<=90
    _,_,subprob,_,p60c=roles[p]
    availability=max(ps,(e.get('chance_of_playing_next_round') or 50)/100) if e['status']=='d' else 1
    pp=min(1,ps+max(0,availability-ps)*subprob);pp=0 if mi==0 else pp;p60=min(ps*p60c,mi/60)
    val=bonus=0.
    for f in fx:
        if f['event']!=g or e['team'] not in [f['team_h'],f['team_a']]:continue
        home=e['team']==f['team_h'];op=f['team_a'] if home else f['team_h'];lam=mean*strength[op][0]*strength[e['team']][1]*(.9 if home else 1.1);scale=strength[op][1]*(1.1 if home else .9)
        attack=(r['expected_goals']*sc['goals_scored'][po]+r['expected_assists']*sc['assists'])*mi/90*scale
        gc=sum(z//2*math.exp(-lam)*lam**z/math.factorial(z) for z in range(25))
        sv=r['saves']*mi/max(ps,1e-8)/90 if ps else 0;savepts=ps*sum(z//3*math.exp(-sv)*sv**z/math.factorial(z) for z in range(40))*sc['saves'] if k==1 else 0
        other=sum(r[s]*sc[s] for s in stats if s not in ['expected_goals','expected_assists','saves'])*mi/90
        bonus+=r['bonus']*sc['bonus']*mi/90
        val+=sc['short_play']*pp+(sc['long_play']-sc['short_play'])*p60+attack+sc['clean_sheets'][po]*math.exp(-lam)*p60+sc['goals_conceded'][po]*gc*mi/90+savepts+dc_rates[p]*sc['defensive_contribution'][po]*p60+other
    return max(0,val),bonus

POS=np.array([E[p]['element_type'] for p in ids]);TEAM=np.array([E[p]['team'] for p in ids]);COST=np.array([cost[p] for p in ids]);SALES=COST.copy()
for p,v in osell.items():SALES[ix[p]]=v
ORIG=np.array(sorted([ix[p] for p in orig],key=lambda i:(POS[i],i)),dtype=np.int64)
name=lambda aa:', '.join(E[ids[int(i)]]['web_name'] for i in aa)
named=lambda n:next(ix[p] for p in ids if E[p]['web_name']==n)
BB=99;FH=16
jsave=jwrite

def ordered(ss):return np.array(sorted(set(int(i) for i in ss),key=lambda i:(POS[i],i)),dtype=np.int64)
def legal(s):
    assert len(s)==len(set(s))==15
    assert [int(sum(POS[s]==k)) for k in range(1,5)]==[2,5,5,3]
    assert max(Counter(TEAM[s]).values())<=3

XP=np.array([[forecast(p,g)[0] for g in GWS] for p in ids]);REPO=XP.copy();PP=np.zeros_like(XP)
repo_raw={(int(r['element']),int(r['gw'])):r for r in rows(IN/'expected_points.csv')}
for p in ids:
    e=E[p];_,_,subprob,_,_=roles[p]
    for g in GWS:
        r=md[p,g];ps=float(r['p_start']);mi=float(r['forventede_min']);av=max(ps,(e.get('chance_of_playing_next_round') or 50)/100) if e['status']=='d' else 1
        PP[ix[p],g-10]=min(1,ps+max(0,av-ps)*subprob) if mi else 0
        if (p,g) in repo_raw:
            raw=repo_raw[p,g];oldmin=float(raw['exp_minutes']);REPO[ix[p],g-10]=float(raw['xp'])*mi/oldmin if oldmin else XP[ix[p],g-10]
for p in blocked:XP[ix[p]]=0;REPO[ix[p]]=0;PP[ix[p]]=0
M=np.array([XP,REPO]);BLEND=M.mean(axis=0)
UI=np.array([ix[p] for p in ids if p not in blocked and E[p].get('can_select',True) and float(md[p,11]['p_start'])>=(.35 if E[p]['status']=='d' else .5)],dtype=np.int64)
for label,rg in [('spillerpoeng.csv',range(10,18)),('spillerpoeng_R18_R19.csv',range(18,20))]:
    save(label,[dict(id=p,navn=E[p]['web_name'],gw=g,codex=round(XP[ix[p],g-10],6),repo_hybrid=round(REPO[ix[p],g-10],6)) for p in ids for g in rg])
save('p_play.csv',[dict(id=p,navn=E[p]['web_name'],gw=g,p_start=md[p,g]['p_start'],p_play=PP[ix[p],g-10]) for p in ids for g in GWS])
save('kalibrering.csv',[dict(id=p,navn=E[p]['web_name'],observert_snitt_R1_R9=E[p]['total_points']/9,codex_R10=XP[ix[p],0],repo_raw_R10=float(repo_raw.get((p,10),{}).get('xp',0)),repo_hybrid_R10=REPO[ix[p],0],codex_R10_R15_snitt=XP[ix[p],:6].mean(),repo_R10_R15_snitt=REPO[ix[p],:6].mean(),bonus_observert=E[p]['bonus']/9,bonus_codex_R10=forecast(p,10)[1]) for p in ids if E[p]['now_cost']>=60 and E[p]['web_name'] in ['Haaland','Salah','Palmer','B.Fernandes','Mbeumo','Gabriel','Isak','Watkins','Tavernier','Rogers']])
# LUT: legitimate substitutions by nominal formation and ordered bench positions.
# Missing slots remain slots, not a requirement that actual playing survivors satisfy 3/2/1.
# Prefer first available bench player whenever a valid matching exists; then next.
# Subset feasibility: substitute into distinct absent starter slots and retain legal XI formation.
LUT=np.zeros((144,27,144,8),dtype=np.int8)
# forms from setup
for d,m,f in forms:
    fi=d*24+m*4+f
    benchpos=[0]*(5-d)+[1]*(5-m)+[2]*(3-f)
    for bp in set(itertools.permutations(benchpos)):
        bi=bp[0]*9+bp[1]*3+bp[2]
        for miss in itertools.product(range(d+1),range(m+1),range(f+1)):
            mi=miss[0]*24+miss[1]*4+miss[2]
            feasible=[]
            for sm in range(8):
                add=[sum(bool(sm&(1<<j)) and bp[j]==k for j in range(3)) for k in range(3)];n=sum(add)
                ok=False
                for rem in itertools.product(*(range(z+1) for z in miss)):
                    if sum(rem)!=n:continue
                    final=np.array([d,m,f])-rem+add
                    if all(final>=np.array([3,2,1])) and all(final<=np.array([5,5,3])):ok=True;break
                if ok:feasible.append(sm)
            for av in range(8):
                choices=[sm for sm in feasible if sm&av==sm]
                # bench1 highest priority, then bench2, then bench3.
                best=max(choices,key=lambda sm:((sm&1)>0,(sm&2)>0,(sm&4)>0))
                LUT[fi,bi,mi,av]=best
PERMS=np.array(list(itertools.permutations(range(3))),dtype=np.int64)

@njit
def benchweights(s,xi,bn,pp,pos,lut):
    counts=np.zeros(3,np.int64);prob=np.zeros((3,6));prob[:,0]=1.
    for j in xi:
        if pos[s[j]]==1:continue
        k=pos[s[j]]-2;q=1-pp[s[j]];n=counts[k]
        for z in range(n+1,-1,-1):prob[k,z]=(prob[k,z]*(1-q) if z<=n else 0)+(prob[k,z-1]*q if z>0 else 0)
        counts[k]+=1
    fi=counts[0]*24+counts[1]*4+counts[2];bi=(pos[s[bn[0]]]-2)*9+(pos[s[bn[1]]]-2)*3+pos[s[bn[2]]]-2
    out=np.zeros(3)
    for a in range(counts[0]+1):
        for b_ in range(counts[1]+1):
            for c in range(counts[2]+1):
                pr=prob[0,a]*prob[1,b_]*prob[2,c]
                if pr<1e-15:continue
                mi=a*24+b_*4+c
                for av in range(8):
                    joint=pr
                    for j in range(3):joint*=pp[s[bn[j]]] if av&(1<<j) else 1-pp[s[bn[j]]]
                    chosen=lut[fi,bi,mi,av]
                    for j in range(3):
                        if chosen&(1<<j) and pp[s[bn[j]]]>0:out[j]+=joint/pp[s[bn[j]]]
    return out

@njit
def evaluate_selection(s,xi,bn,gkb,xp,pp,pos,lut,bb=False):
    weights=np.zeros(15)
    for j in xi:weights[j]=1.
    if bb:
        weights[:]=1.
    else:
        bw=benchweights(s,xi,bn,pp,pos,lut)
        for k in range(3):weights[bn[k]]=bw[k]
        gk=1-gkb;weights[gkb]=1-pp[s[gk]]
    # captain + vice: appearance, not start probability, determines inheritance.
    cap=-1;vice=-1;extra=-1.
    for c in xi:
        for v in xi:
            if c==v:continue
            ev=xp[s[c]]+(1-pp[s[c]])*xp[s[v]]
            if ev>extra+1e-12 or (abs(ev-extra)<1e-12 and cap>=0 and xp[s[c]]>xp[s[cap]]):extra=ev;cap=c;vice=v
    weights[cap]+=1.;weights[vice]+=1-pp[s[cap]]
    value=0.
    for j in range(15):value+=weights[j]*xp[s[j]]
    return value,weights,cap,vice

@njit
def select(s,xp,pp,pos,lut,perms,exhaustive=False,bb=False):
    # Exact search in main report. MC uses a deterministic shortlist of XI masks,
    # with exact probability integration for EACH shortlisted XI and bench order.
    masks=np.zeros((400,3),np.int64);nm=0
    if exhaustive:
        for a in range(2,13):
            for b_ in range(a+1,14):
                for c in range(b_+1,15):masks[nm]=np.array([a,b_,c]);nm+=1
    else:
        # Four ranking schemes: unconditional, conditional, and two coverage credits.
        for mode in range(4):
            ranks=np.zeros((3,5),np.int64);nn=np.zeros(3,np.int64)
            for k in range(3):
                scores=np.full(15,-1e8)
                for j in range(2,15):
                    if pos[s[j]]!=k+2:continue
                    if mode==0:v=xp[s[j]]
                    elif mode==1:v=xp[s[j]]/max(pp[s[j]],.05)
                    else:v=xp[s[j]]+(1-pp[s[j]])*(2 if mode==2 else 4)
                    scores[j]=v
                order=np.argsort(-scores)
                for j in order:
                    if scores[j]>-1e7:ranks[k,nn[k]]=j;nn[k]+=1
            for d in range(3,6):
                for m in range(2,6):
                    f=10-d-m
                    if f<1 or f>3:continue
                    bslots=np.zeros(3,np.int64);cnt=0
                    for k,n in enumerate((d,m,f)):
                        for jj in range(n,nn[k]):bslots[cnt]=ranks[k,jj];cnt+=1
                    bslots.sort();duplicate=False
                    for old in range(nm):
                        if np.all(masks[old]==bslots):duplicate=True;break
                    if not duplicate:masks[nm]=bslots;nm+=1
    best=-1.;besttie=-1.;bestw=np.zeros(15);bestxi=np.zeros(11,np.int64);bestbn=np.zeros(4,np.int64);bestc=bestv=0
    for z in range(nm):
        raw=masks[z];counts=np.array([5,5,3])
        for j in raw:counts[pos[s[j]]-2]-=1
        if counts[0]<3 or counts[1]<2 or counts[2]<1:continue
        for gk in range(2):
            xi=np.zeros(11,np.int64);xi[0]=gk;nn=1
            for j in range(2,15):
                if j!=raw[0] and j!=raw[1] and j!=raw[2]:xi[nn]=j;nn+=1
            for perm in perms:
                bn=raw[perm];val,w,cap,vice=evaluate_selection(s,xi,bn,1-gk,xp,pp,pos,lut,bb)
                tie=1e-6*(3*xp[s[bn[0]]]+2*xp[s[bn[1]]]+xp[s[bn[2]]])
                for j in xi:tie+=xp[s[j]]+.001*pp[s[j]]
                if val>best+1e-12 or (abs(val-best)<1e-12 and tie>besttie):
                    best=val;besttie=tie;bestw=w;bestxi=xi.copy();bestbn=np.array([1-gk,bn[0],bn[1],bn[2]]);bestc=cap;bestv=vice
                if bb:break
    return best,bestw,bestxi,bestbn,bestc,bestv

# Tiny rule tests: 3-defender XI cannot replace absent defender with midfielder;
# a midfielder may replace an absent midfielder; zero-minute captain triggers vice.
def rule_tests():
    d,m,f=3,5,2;fi=d*24+m*4+f
    # bench DEF, DEF, FWD; absent DEF must skip FWD if both bench DEF absent.
    bi=0*9+0*3+2;mi=1*24
    assert LUT[fi,bi,mi,4]==0 and LUT[fi,bi,mi,5]&1
    # GK fallback weights independent of outfield formation.
    s=ORIG;xp=np.ones(N);pp=np.ones(N);xi=np.array([0,2,3,4,7,8,9,10,11,12,13]);bn=np.array([5,6,14]);pp[s[0]]=0;pp[s[12]]=0;xp[s[0]]=0;xp[s[12]]=0
    val,w,c,v=evaluate_selection(s,xi,bn,1,xp,pp,POS,LUT,False);assert w[1]==1
    pp=np.ones(N);_,w,c,v=evaluate_selection(s,xi,bn,1,xp,pp,POS,LUT,False);assert w[1]==0
rule_tests()

# Exact appearance integration for candidate lineups; finite shortlist for fast policy.
@njit
def obj_batch(squads,pred,pp,cols,bb,pos,lut,perms):
    vv=np.zeros(len(squads))
    for j in range(len(squads)):
        for t in cols:
            z=select(squads[j],pred[:,t],pp[:,t],pos,lut,perms,False,t==bb)
            vv[j]+=z[0]
    return vv

def approx(ss,pred,pp,cols,bb=10):
    ss=np.atleast_2d(ss);v=pred[ss][:,:,cols];ap=pp[ss][:,:,cols];cs=[];bench=[];chosenpp=[]
    for sl in [slice(0,2),slice(2,7),slice(7,12),slice(12,15)]:
        order=np.argsort(-v[:,sl,:],axis=1);a=np.take_along_axis(v[:,sl,:],order,axis=1);p=np.take_along_axis(ap[:,sl,:],order,axis=1)
        cs.append(np.concatenate([np.zeros((len(ss),1,len(cols))),np.cumsum(a,axis=1)],axis=1));chosenpp.append(np.concatenate([np.zeros((len(ss),1,len(cols))),np.cumsum(1-p,axis=1)],axis=1))
    best=np.zeros((len(ss),len(cols)));tot=v.sum(axis=1);cap=v.max(axis=1)
    for d,m,f in forms:
        xi=cs[0][:,1]+cs[1][:,d]+cs[2][:,m]+cs[3][:,f]
        absent=chosenpp[1][:,d]+chosenpp[2][:,m]+chosenpp[3][:,f]
        benchpts=tot-xi-(cs[0][:,2]-cs[0][:,1]);gain=benchpts*np.minimum(absent,3)/3+(cs[0][:,2]-cs[0][:,1])*chosenpp[0][:,1]
        z=xi+cap+gain
        if bb in cols:z[:,cols.index(bb)]=tot[:,cols.index(bb)]+cap[:,cols.index(bb)]
        best=np.maximum(best,z)
    return best.sum(axis=1)

def pools(pred,cols,avail):
    result=[]
    for k in range(1,5):
        q=UI[(POS[UI]==k)&avail[UI]];v=pred[q][:,cols].sum(axis=1)
        top=q[np.argsort(-v,kind='stable')[:12]];cheap=q[np.lexsort((q,COST[q]))[:4]]
        result.append(np.array(sorted(set(top)|set(cheap)),dtype=np.int64))
    return result

def neighbors(s,ps,sv,liquid):
    ss=[];clubs=np.bincount(TEAM[s],minlength=21);spent=sv[s].sum()
    for slot,out in enumerate(s):
        inc=ps[POS[out]-1];inc=inc[~np.isin(inc,s)]
        inc=inc[(spent-sv[out]+sv[inc]<=liquid)&(clubs[TEAM[inc]]-(TEAM[inc]==TEAM[out])<3)]
        for p in inc:
            new=s.copy();new[slot]=p;ss.append(ordered(new))
    return np.array(ss,dtype=np.int64) if ss else np.empty((0,15),dtype=np.int64)

def transact(s,new,sv,cash):
    legal(new);out=set(s)-set(new);inn=set(new)-set(s);cash=int(cash+sum(sv[i] for i in out)-sum(COST[i] for i in inn));assert cash>=0
    sv=sv.copy()
    for i in out|inn:sv[i]=COST[i]
    return new,sv,cash

def rolling(g,s,sv,cash,ft,pred,pp,avail,wc,bb=19):
    end=min(19,g+3,wc-1 if wc>g else 19);cols=[h-10 for h in range(g,end+1) if h!=FH];n=hits=0
    if not cols:return s,sv,cash,n,hits
    for _ in range(min(5,ft+1)):
        ps=pools(pred,cols,avail);liquid=int(cash+sv[s].sum());nn=neighbors(s,ps,sv,liquid)
        if not len(nn):break
        ap=approx(nn,pred,pp,cols,bb-10);first=np.argsort(-ap)[:3]
        # Two-swap financing candidates, same proposal rule in every WC timing.
        if n<ft:
            extra=[]
            for j in first:
                for q in neighbors(nn[j],ps,sv,liquid):
                    if len(set(q)-set(s))==2:extra.append(q)
            if extra:nn=np.concatenate([nn,np.array(extra)])
        nn=np.unique(nn,axis=0);ap=approx(nn,pred,pp,cols,bb-10);counts=np.array([len(set(q)-set(s)) for q in nn]);valid=counts<=ft-n+1;nn=nn[valid];ap=ap[valid];counts=counts[valid]
        costhit=4*np.maximum(0,counts-(ft-n));rank=np.argsort(-(ap-costhit));short=nn[rank[:3]];counts=counts[rank[:3]]
        base=obj_batch(s[None,:],pred,pp,np.array(cols),bb-10,POS,LUT,PERMS)[0]
        vv=obj_batch(short,pred,pp,np.array(cols),bb-10,POS,LUT,PERMS);scores=vv-4*np.maximum(0,counts-(ft-n));j=scores.argmax();cnt=int(counts[j]);gain=vv[j]-base
        paid=max(0,cnt-(ft-n));free=cnt-paid;threshold=(0 if ft-n==5 or g==19 else free)+5*paid
        if gain<=threshold+1e-7:break
        s,sv,cash=transact(s,short[j],sv,cash);n+=cnt;hits+=4*paid
        if paid:break
    return s,sv,cash,n,hits


TEMPLATES=[]
def renew(g,s,sv,cash,pred,pp,avail,fh=False,ban=None,bb=19,keep=None):
    cols=list(range(g-10,10)) if not fh else [g-10];cols=[t for t in cols if fh or t!=FH-10];ps=pools(pred,cols,avail);liquid=int(cash+sv[s].sum());seeds=[]
    def repair(template):
        cur=list(template);used=set(cur);clubs=Counter(TEAM[cur])
        for slot,i in enumerate(cur):
            if (avail[i] or i in s) and i!=ban:continue
            used.remove(i);clubs[TEAM[i]]-=1
            cand=[int(z) for z in UI if avail[z] and POS[z]==POS[i] and z not in used and z!=ban and clubs[TEAM[z]]<3]
            if not cand:return None
            z=min(cand,key=lambda j:(sv[j],j));cur[slot]=z;used.add(z);clubs[TEAM[z]]+=1
        a=ordered(cur)
        if sv[a].sum()>liquid:return None
        return a
    for q in [s]+TEMPLATES:
        a=repair(q)
        if a is not None:seeds.append(a)
    cheap=[];clubs=Counter()
    for k,n in [(1,2),(2,5),(3,5),(4,3)]:
        for i in sorted([int(z) for z in UI if POS[z]==k and avail[z] and z!=ban],key=lambda z:(sv[z],z)):
            if clubs[TEAM[i]]<3:
                cheap.append(i);clubs[TEAM[i]]+=1
                if sum(POS[z]==k for z in cheap)==n:break
    if len(cheap)==15 and sv[cheap].sum()<=liquid:seeds.append(ordered(cheap))
    if keep is not None:seeds=[a for a in seeds if keep in a]
    assert seeds
    ss=np.unique(np.array(seeds),axis=0);ap=approx(ss,pred,pp,cols,bb-10);ss=ss[np.argsort(-ap)[:4]]
    vv=obj_batch(ss,pred,pp,np.array(cols),bb-10,POS,LUT,PERMS);best=ss[vv.argmax()].copy();value=vv.max()
    for _ in range(3):
        nn=neighbors(best,ps,sv,liquid)
        if ban is not None:nn=nn[~np.any(nn==ban,axis=1)]
        if keep is not None:nn=nn[np.any(nn==keep,axis=1)]
        if not len(nn):break
        ap=approx(nn,pred,pp,cols,bb-10);nn=nn[np.argsort(-ap)[:3]]
        vv=obj_batch(nn,pred,pp,np.array(cols),bb-10,POS,LUT,PERMS);j=vv.argmax()
        if vv[j]<=value+1e-7:break
        best=nn[j].copy();value=vv[j]
    legal(best);assert all(avail[i] or i in s for i in best)
    if ban is not None:assert ban not in best
    return ordered(best)


# MILP proposes candidates; all final comparisons use R2's exact autosub integrator.
def seed(cols,nmoves=None,model=2,bb=None):
    candidates=sorted(set(UI)|set(ORIG)) if nmoves is not None else list(UI)
    pred=BLEND if model==2 else M[model]
    prob=pulp.LpProblem('GW10',pulp.LpMaximize)
    x=pulp.LpVariable.dicts('s',candidates,cat='Binary');price=SALES.copy()
    for k,n in [(1,2),(2,5),(3,5),(4,3)]:prob+=pulp.lpSum(x[i] for i in candidates if POS[i]==k)==n
    for t in T:prob+=pulp.lpSum(x[i] for i in candidates if TEAM[i]==t)<=3
    prob+=pulp.lpSum(int(price[i])*x[i] for i in candidates)<=995
    if nmoves is not None:prob+=pulp.lpSum(x[i] for i in candidates if i not in ORIG)==nmoves
    obj=[]
    for g in cols:
        y=pulp.LpVariable.dicts('xi'+str(g),candidates,cat='Binary');c=pulp.LpVariable.dicts('c'+str(g),candidates,cat='Binary')
        prob+=pulp.lpSum(y.values())==11;prob+=pulp.lpSum(c.values())==1
        for i in candidates:prob+=y[i]<=x[i];prob+=c[i]<=y[i]
        for k,lo,hi in [(1,1,1),(2,3,5),(3,2,5),(4,1,3)]:
            prob+=pulp.lpSum(y[i] for i in candidates if POS[i]==k)>=lo
            prob+=pulp.lpSum(y[i] for i in candidates if POS[i]==k)<=hi
        obj.extend(float(pred[i,g-10])*((x[i] if bb==g else y[i])+c[i]) for i in candidates)
    prob+=pulp.lpSum(obj)
    solver=pulp.PULP_CBC_CMD(msg=False,timeLimit=8,gapRel=.0001,threads=1);solver.tmpDir=str(O)
    prob.solve(solver);s=ordered(i for i in candidates if x[i].value() is not None and x[i].value()>.5)
    legal(s);assert SALES[s].sum()<=995
    if nmoves is not None:assert len(set(s)-set(ORIG))==nmoves
    return s


def trajectory(initial,ft0=2,fh=16,world=None,full=False,arrays=None,record=True):
    """Identical four-round normal-XI transfer policy for every BB date.
    BB does not alter ownership, FT use or FH date. This permits paired comparison
    of all 10 BB dates on one adaptive ownership trajectory, without hindsight.
    """
    global FH
    FH=fh;mats=M if arrays is None else arrays;blend=mats.mean(axis=0)
    s=ORIG.copy();sv=SALES.copy();cash=4;ft=ft0;rr=[];normal=[];boost=[]
    if world is None:world=np.zeros((H,N),dtype=np.int16)
    for t,g in enumerate(GWS):
        release=world[t];av=release<=t;known=(np.arange(H)[None,:]>=release[:,None])|av[:,None]
        pred=blend*known;pp=PP*known;before=s.copy();ftbefore=ft;hit=n=0
        if t==0:
            n=len(set(initial)-set(s));s,sv,cash=transact(s,initial,sv,cash);active=s;hit=4*max(0,n-ft)
        elif g==fh:active=renew(g,s,sv,cash,pred,pp,av,fh=True,bb=99)
        else:
            s,sv,cash,n,hit=rolling(g,s,sv,cash,ft,pred,pp,av,99,bb=99);active=s
        z=select(active,pred[:,t],pp[:,t],POS,LUT,PERMS,full,False)
        zb=select(active,pred[:,t],pp[:,t],POS,LUT,PERMS,False,True)
        points=(mats[:,active,t]*known[active,t][None,:]*z[1][None,:]).sum(axis=1)-hit
        boosted=(mats[:,active,t]*known[active,t][None,:]*zb[1][None,:]).sum(axis=1)-hit
        rawbench=(mats[:,active[z[3]],t]*known[active[z[3]],t][None,:]).sum(axis=1)
        normal.append(points);boost.append(boosted-points)
        if g!=fh:ft=min(5,max(0,ft-n)+1)
        if record:
            rr.append(dict(gw=g,chip='FH' if g==fh else '',tropp=[ids[i] for i in active],permanent=[ids[i] for i in s],elleve=[ids[active[j]] for j in z[2]],benk=[ids[active[j]] for j in z[3]],kaptein=ids[active[z[4]]],visekaptein=ids[active[z[5]]],vekter=z[1].tolist(),bb_vekter=zb[1].tolist(),poeng=points.tolist(),bb_gevinst=(boosted-points).tolist(),benk_brutto=rawbench.tolist(),inn=[ids[i] for i in sorted(set(active)-set(before))],ut=[ids[i] for i in sorted(set(before)-set(active))],bank=cash/10,FT_for=ftbefore,FT_etter=ft,trekk=hit))
        legal(s);assert cash>=0 and 1<=ft<=5
    normal=np.array(normal);boost=np.array(boost)
    totals=normal.sum(axis=0)[None,:]+boost;totals[fh-10]=np.nan
    return dict(FH=fh,FT=ft0,total_uten_BB=normal.sum(axis=0).tolist(),alle_BB=totals.tolist(),normal=normal.tolist(),boost=boost.tolist(),rows=rr)


def choose_bb(p):return int(np.nanargmax(np.mean(p['alle_BB'],axis=1)))+10

def alternative(label,p,bb,group=None):
    r=p['rows'][0];points=np.array(p['normal']).copy();points[bb-10]+=p['boost'][bb-10]
    z=dict(alternativ=label,gruppe=group or label[0],FT=p['FT'],BB=bb,FH=p['FH'],ut=name(ix[i] for i in r['ut']),inn=name(ix[i] for i in r['inn']),poengtrekk_R10=r['trekk'],poengtrekk_totalt=sum(r['trekk'] for r in p['rows']),bank_etter=r['bank'])
    for m,model in enumerate(['codex','repo_hybrid']):
        for suffix,n in [('R10',1),('R10_R13',4),('R10_R19',10)]:z[model+'_'+suffix]=float(points[:n,m].sum())
    z['modellspredning_R10_R19']=abs(z['codex_R10_R19']-z['repo_hybrid_R10_R19'])
    z['skade_p10_blend']='';z['skade_p90_blend']=''
    return z


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--draws',type=int,default=100);parser.add_argument('--deterministic-only',action='store_true');args=parser.parse_args()
    start=time.time();print('Forecast ready:',N,'players; repo',sorted({g for p,g in repo_raw}),flush=True)
    candidates={0:[ORIG]}
    for n in [1,2,3,4]:
        seeds=[]
        for cols in [[10],list(range(10,14)),list(range(10,20))]:
            for model in [0,1,2]:seeds.append(seed(cols,n,model))
        candidates[n]=list(np.unique(np.array(seeds),axis=0))
        print('Transfer seeds',n,len(candidates[n]),flush=True)
    # Broad single-transfer enumeration plus financing pairs: static proposals only.
    allpools=[UI[POS[UI]==k] for k in range(1,5)]
    singles=neighbors(ORIG,allpools,SALES,995)
    for pred in [M[0],M[1],BLEND]:
        for cols in [[0],list(range(4)),[t for t in range(H) if t!=6]]:
            ap=approx(singles,pred,PP,cols,89)
            candidates[1].extend(singles[np.argsort(-ap)[:5]])
    candidates[1]=list(np.unique(np.array(candidates[1]),axis=0))
    pairs=[]
    for one in candidates[1]:
        pairs.extend(q for q in neighbors(one,allpools,SALES,995) if len(set(q)-set(ORIG))==2)
    pairs=np.unique(np.array(pairs),axis=0)
    for pred in [M[0],M[1],BLEND]:
        for cols in [[0],list(range(4)),[t for t in range(H) if t!=6]]:
            ap=approx(pairs,pred,PP,cols,89)
            candidates[2].extend(pairs[np.argsort(-ap)[:5]])
    candidates[2]=list(np.unique(np.array(candidates[2]),axis=0))
    print('Expanded single/pair candidates',len(candidates[1]),len(candidates[2]),flush=True)
    for g in range(11,20):TEMPLATES.extend([seed([g],model=m) for m in [0,1,2]])
    jsave('sok_kandidater.json',{str(n):[[ids[i] for i in s] for s in ss] for n,ss in candidates.items()})
    # Rank proposed concrete initial squads on complete rolling paths, not static sums.
    chosen={};paths={};candidate_rows=[]
    for n,ss in candidates.items():
        ranked=[]
        for s in ss:
            p=trajectory(s,fh=16);bb=choose_bb(p);score=np.mean(p['alle_BB'][bb-10]);ranked.append((score,s,p))
            candidate_rows.append(dict(bytter=n,ut=name(set(ORIG)-set(s)),inn=name(set(s)-set(ORIG)),BB=bb,score=score))
        ranked.sort(key=lambda z:-z[0]);chosen[n]=ranked[0][1]
    save('byttesok.csv',candidate_rows)
    # Joint FH/BB evaluation for each transfer count, common policy.
    joint=[]
    for n,s in chosen.items():
        for fh in range(11,20):
            p=trajectory(s,fh=fh);paths[n,fh]=p
            for bb in GWS:
                if bb!=fh:joint.append(dict(bytter=n,FH=fh,BB=bb,codex=p['alle_BB'][bb-10][0],repo_hybrid=p['alle_BB'][bb-10][1],blend=np.mean(p['alle_BB'][bb-10])))
    save('chiprutenett.csv',joint)
    bestjoint=max(joint,key=lambda r:r['blend']);fh=bestjoint['FH']
    # Same FH for A-D and E; F explicitly varies FH on the selected initial action.
    mainplans={('A' if n==0 else 'B' if n==1 else 'C' if n==2 else 'D'+str(n)):trajectory(s,fh=fh,full=True) for n,s in chosen.items()}
    choice=max(mainplans,key=lambda k:np.mean(mainplans[k]['alle_BB'][choose_bb(mainplans[k])-10]));chosen_n=len(set(chosen[int(choice[-1]) if choice.startswith('D') else {'A':0,'B':1,'C':2}[choice]])-set(ORIG))
    selected=mainplans[choice];bb=choose_bb(selected)
    alternatives=[alternative(k,p,choose_bb(p)) for k,p in mainplans.items()]
    for g in GWS:
        if g!=fh:alternatives.append(alternative('E_BB'+str(g),selected,g,'E'))
    fplans={}
    for f in range(11,20):
        p=trajectory(chosen[chosen_n],fh=f,full=True);fplans[str(f)]=p;alternatives.append(alternative('F_FH'+str(f),p,choose_bb(p),'F'))
    # G: score four best feasible captain choices on precisely the selected XI.
    r=selected['rows'][0];s=ordered(ix[p] for p in r['tropp']);z=select(s,BLEND[:,0],PP[:,0],POS,LUT,PERMS,True,bb==10)
    xi=z[2];caps=[]
    for c in xi:
        v=max([j for j in xi if j!=c],key=lambda j:BLEND[s[j],0]);extra=M[:,s[c],0]+(1-PP[s[c],0])*M[:,s[v],0]
        caps.append((float(extra.mean()),c,v,extra))
    caps.sort(reverse=True);caprows=[]
    for _,c,v,extra in caps[:4]:
        row=alternative('G_'+E[ids[s[c]]]['web_name'],selected,bb,'G');oldextra=M[:,s[z[4]],0]+(1-PP[s[z[4]],0])*M[:,s[z[5]],0];delta=extra-oldextra
        for m,model in enumerate(['codex','repo_hybrid']):
            for suff in ['R10','R10_R13','R10_R19']:row[model+'_'+suff]+=float(delta[m])
        alternatives.append(row);caprows.append(dict(id=ids[s[c]],navn=E[ids[s[c]]]['web_name'],vice=E[ids[s[v]]]['web_name'],codex=XP[s[c],0],repo_hybrid=REPO[s[c],0],ekstrakopi_codex=extra[0],ekstrakopi_repo=extra[1]))
    save('kapteiner.csv',caprows)
    backupfh=16 if fh!=16 else 15
    supplement=trajectory(chosen[chosen_n],fh=backupfh,full=True)
    alternatives.append(alternative('E_BB'+str(fh)+'_FH'+str(backupfh),supplement,fh,'E'))
    alternatives.append(alternative('E_BB10_FH'+str(backupfh),supplement,10,'E'))
    jsave('BB_kollisjon.json',dict(BB=fh,FH=backupfh,plan=supplement))
    ftrows=[]
    for ft in [1,2,3]:
        for n,s in chosen.items():
            p=trajectory(s,ft0=ft,fh=fh,full=True);ftrows.append(alternative('FT'+str(ft)+'_'+str(n),p,choose_bb(p)))
    save('ft_sensitivitet.csv',ftrows)
    benches=[]
    for k,p in mainplans.items():
        for r in p['rows']:
            benches.append(dict(alternativ=k,gw=r['gw'],FH=fh,benk=name(ix[i] for i in r['benk']),codex_brutto=r['benk_brutto'][0],repo_brutto=r['benk_brutto'][1],codex_BB_netto=r['bb_gevinst'][0],repo_BB_netto=r['bb_gevinst'][1],BB_mulig=r['gw']!=fh))
    save('benk_per_runde.csv',benches)
    gross=[];gi=named('Groß');baseps=float(md[ids[gi],10]['p_start']);basemi=float(md[ids[gi],10]['forventede_min']);oldpp=PP[gi,0]
    for ps in [0,.5,baseps,.9]:
        mats=M.copy();ratio=ps/baseps if baseps else 0;mats[:,gi,0]*=ratio;PP[gi,0]=min(1,ps+(1-ps)*roles[ids[gi]][2]) if ps else 0
        for k,p in mainplans.items():
            n=0 if k=='A' else 1 if k=='B' else 2 if k=='C' else int(k[1:]);q=trajectory(chosen[n],fh=fh,arrays=mats,full=True)
            gross.append(dict(alternativ=k,p_start_R10=ps,forventede_min=basemi*ratio,BB_best=choose_bb(q),BB10_codex=q['alle_BB'][0][0],BB10_repo=q['alle_BB'][0][1],BB19_codex=q['alle_BB'][9][0],BB19_repo=q['alle_BB'][9][1]))
    PP[gi,0]=oldpp;save('gross_sensitivitet.csv',gross)
    jsave('planer.json',dict(hoved=mainplans,FH=fplans,valg=choice,BB=bb,FH_valg=fh))
    save('alternativer.csv',alternatives)
    report(mainplans,choice,bb,fh,alternatives,ftrows,[],caprows,gross,False)
    print('Deterministic complete',round(time.time()-start,1),'seconds',choice,'BB',bb,'FH',fh,flush=True)
    if args.deterministic_only:return
    rng=np.random.default_rng(7089878);U=rng.random((args.draws,H,N));dur=np.array([1,2,3,6],dtype=np.int16)[rng.integers(0,4,size=(args.draws,H,N))]
    trials=[];sim=[]
    for probability in [.01,.02,.03]:
        allresults={k:[] for k in mainplans};extraresults=[]
        for draw in range(args.draws):
            world=np.zeros((H,N),dtype=np.int16);end=np.zeros(N,dtype=np.int16)
            # R10 uses the supplied known information. New injuries begin R11.
            for t in range(1,H):
                new=(end<=t)&(U[draw,t]<probability);end[new]=t+dur[draw,t,new];world[t]=end
            for k in mainplans:
                n=0 if k=='A' else 1 if k=='B' else 2 if k=='C' else int(k[1:]);p=trajectory(chosen[n],fh=fh,world=world,record=False)
                vals=np.array(p['alle_BB']);allresults[k].append(vals)
                for g in GWS:
                    if g!=fh:trials.append(dict(p=probability,trekk=draw,alternativ=k,BB=g,codex=vals[g-10,0],repo_hybrid=vals[g-10,1]))
            extra=trajectory(chosen[chosen_n],fh=backupfh,world=world,record=False)
            extraresults.append(extra['alle_BB'])
            for g in [10,fh]:
                trials.append(dict(p=probability,trekk=draw,alternativ='E_match_FH'+str(backupfh),BB=g,codex=extra['alle_BB'][g-10][0],repo_hybrid=extra['alle_BB'][g-10][1]))
            if (draw+1)%10==0:print('MC',probability,draw+1,'/',args.draws,'elapsed',round(time.time()-start),flush=True)
        for k,v in allresults.items():
            a=np.array(v);nom=mainplans[k]
            for g in GWS:
                if g==fh:continue
                for m,model in enumerate(['codex','repo_hybrid']):
                    delta=a[:,0,m]-a[:,g-10,m];base=nom['alle_BB'][0][m]-nom['alle_BB'][g-10][m]
                    sim.append(dict(p=probability,alternativ=k,BB_sen=g,poengsett=model,snitt=a[:,g-10,m].mean(),p10=np.quantile(a[:,g-10,m],.1),p90=np.quantile(a[:,g-10,m],.9),BB10_minus_sen=delta.mean(),delta_p10=np.quantile(delta,.1),delta_p90=np.quantile(delta,.9),paret_SE=delta.std(ddof=1)/np.sqrt(args.draws),p0_delta=base,endring_fra_p0=delta.mean()-base,antall=args.draws))
            if probability==.02:
                bbest=choose_bb(nom)-10;blend=a[:,bbest,:].mean(axis=1)
                for r in alternatives:
                    if r['alternativ']==k:r['skade_p10_blend']=float(np.quantile(blend,.1));r['skade_p90_blend']=float(np.quantile(blend,.9))
        extraa=np.array(extraresults)
        for m,model in enumerate(['codex','repo_hybrid']):
            delta=extraa[:,0,m]-extraa[:,fh-10,m];base=supplement['alle_BB'][0][m]-supplement['alle_BB'][fh-10][m]
            sim.append(dict(p=probability,alternativ='E_match_FH'+str(backupfh),BB_sen=fh,poengsett=model,snitt=extraa[:,fh-10,m].mean(),p10=np.quantile(extraa[:,fh-10,m],.1),p90=np.quantile(extraa[:,fh-10,m],.9),BB10_minus_sen=delta.mean(),delta_p10=np.quantile(delta,.1),delta_p90=np.quantile(delta,.9),paret_SE=delta.std(ddof=1)/np.sqrt(args.draws),p0_delta=base,endring_fra_p0=delta.mean()-base,antall=args.draws))
        save('skadesim.csv',sim);save('skadetrekk.csv',trials);save('alternativer.csv',alternatives)
        report(mainplans,choice,bb,fh,alternatives,ftrows,sim,caprows,gross,False)
    validate(mainplans)
    report(mainplans,choice,bb,fh,alternatives,ftrows,sim,caprows,gross,True)
    print('DONE',choice,'BB',bb,'FH',fh,'elapsed',round(time.time()-start,1),flush=True)

def report(plans,choice,bb,fh,alts,ftrows,sim,caprows,gross,complete):
    p=plans[choice];r=p['rows'][0];main=[z for z in alts if z['alternativ'] in plans];main.sort(key=lambda r:-(r['codex_R10_R19']+r['repo_hybrid_R10_R19']))
    pair=lambda a:f'{a[0]:.1f} / {a[1]:.1f}'
    txt=['# Analyse R10, 2026/27',f"Status: {'fullført og kontrollert' if complete else 'foreløpige resultater; skadesimulering/kontroll pågår'}. Tallpar er codex / repo_hybrid.",f"**Modellanbefaling: {choice}; {'Bench Boost nå i R10' if bb==10 else 'ikke Bench Boost nå; foreløpig BB i R'+str(bb)}. Free Hit R{fh}.** Selg {name(ix[i] for i in r['ut']) or 'ingen'}; kjøp {name(ix[i] for i in r['inn']) or 'ingen'}. Trekk R10: {r['trekk']}. Bank etter: £{r['bank']:.1f}m.",f"**Ellever:** {name(ix[i] for i in r['elleve'])}. **Kaptein:** {E[r['kaptein']]['web_name']}. **Visekaptein:** {E[r['visekaptein']]['web_name']}. **Benk:** {name(ix[i] for i in r['benk'])} (keeper først, deretter prioritert utespillerrekkefølge).",'## Verifiserte data og eksplisitte antakelser','API-snapshot 6. november: bank £0,4m; salgsverdi £99,1m; 15 spillere med status a. WC1 brukt R9, TC1 brukt R3. FH1/BB1 utløper R19. Ingen blanke/doble runder i horisonten. Frist 6. november 18:30 UTC / 19:30 norsk tid. Ingen lagendringer er utført.','FT=2 antas, og 1/3 testes nedenfor. Prisene holdes konstante. FH bevarer FT uten ekstra opptjening (uverifisert regel). Andre runder gir +1, maksimalt 5. Alle kjøp må ha tillatt API-status og minstekrav til forventet startandel; d justeres med API-prosent. Ingen antatt friskdato for dagens langtidsskadde/0 %-spillere: disse holdes utenfor hele horisonten. Dette kan undervurdere fremtidige kjøpsmuligheter.','Spilletid står i minutter_antatt.csv og leses som input ved senere kjøring. Baseline bruker vektede starter R1–R9, historiske minutter ved start/innhopp og en liten prior. BHA/BOU/SUN/CRY: R10 p_start og minutter ×0,95 etter torsdag–søndag. Groß: ytterligere ×0,85 etter fot-smell uten diagnose. Dette er antakelser, ikke bekreftet rotasjon/skadegrad. Claude kan overstyre CSV-en. Grealish og Crooks er null i R10; Morita/Toth holdes ute ved ukjent retur.','Poengreglene leses fra bootstrap game_config.scoring, inkludert 10 poeng per keepermål. Ingen tilpasning etter kalibreringsloggen (bare to runder). Repo-filen dekker R10–R15; repo_hybrid bruker Codex R16–R19. Begge skaleres med samme eksplisitte minutter. Repoets rå xP er frosset i input/expected_points.csv.','## A–D: rangerte konkrete planer',f'Samme FH{fh}, samme fire-runders byttepolitikk og eksakte autobytter i alle planer; BB velges blant alle øvrige runder. Rangering er lik vekt på de to poengsettene. «Beste» betyr beste i det avgrensede søket, ikke bevist globalt optimum.','| Plan | Ut → inn | BB | Trekk R10 | Bank | R10 | R10–R13 | R10–R19 | Skade p10–p90, blend |','|---|---|---:|---:|---:|---:|---:|---:|---|']
    for z in main:
        interval='pågår' if z['skade_p10_blend']=='' else f"{z['skade_p10_blend']:.1f}–{z['skade_p90_blend']:.1f}"
        txt.append(f"| {z['alternativ']} | {z['ut'] or 'ingen'} → {z['inn'] or 'ingen'} | {z['BB']} | {z['poengtrekk_R10']} | {z['bank_etter']:.1f} | {pair([z['codex_R10'],z['repo_hybrid_R10']])} | {pair([z['codex_R10_R13'],z['repo_hybrid_R10_R13']])} | {pair([z['codex_R10_R19'],z['repo_hybrid_R10_R19']])} | {interval} |")
    baseline=next(z for z in main if z['alternativ']=='A');best=next(z for z in main if z['alternativ']==choice)
    margin=(best['codex_R10_R19']+best['repo_hybrid_R10_R19']-baseline['codex_R10_R19']-baseline['repo_hybrid_R10_R19'])/2
    txt.append(f"Gjennomsnittlig fordel mot rull er bare {margin:+.2f} poeng. Handlingsanbefalingen følger dette nominelle modellgjennomsnittet, men er svak når poengsettene eller skadestressen er uenige. Ingen sikker gevinst ved å bruke FT nå er påvist.")
    txt.append(f"Valgt plan minus rull: {pair([best['codex_R10_R19']-baseline['codex_R10_R19'],best['repo_hybrid_R10_R19']-baseline['repo_hybrid_R10_R19']])} gjennom R19. D3/D4 er testede 3-/4-bytteplaner med alle trekk inkludert; et trekk anbefales bare hvis netto forventning er høyest. FT3 gjør trebytteplanen gratis.")
    outs=[ix[i] for i in r['ut']];ins=[ix[i] for i in r['inn']]
    txt+=['## Budsjettkontroll',f"£0,4m + salg £{SALES[outs].sum()/10:.1f}m − kjøp £{COST[ins].sum()/10:.1f}m = **£{r['bank']:.1f}m**. Salg bruker salgspriser.json, ikke markedsverdi. Troppen er kontrollert for 2/5/5/3 og maks tre per klubb.",'| Handling | Spiller | Pris £m |','|---|---|---:|']
    for i in outs:txt.append(f"| Selg | {name([i])} | {SALES[i]/10:.1f} |")
    for i in ins:txt.append(f"| Kjøp | {name([i])} | {COST[i]/10:.1f} |")
    txt+=['## E: Bench Boost nå eller senere',f"Fast konkret R10-handling {choice}, samme eierskapsbane og FH{fh}. Politikken optimaliserer normal ellever over neste fire runder, og er med vilje uavhengig av BB-dato. Dermed får ingen dato særskilt benkeopprusting. Dette er en kontrollert sammenligning, og kan undervurdere målrettet oppbygging før en senere BB.",'Benkens bruttopoeng omfatter fire spillere. Netto BB-gevinst trekker fra vanlig autobytteverdi og tillater optimalt kaptein/vice-valg. At alle forventes å spille betyr ikke at alle har 100 % p_play.','| BB-runde | Benk brutto | Netto BB | Total R10–R19 | BB10 minus denne |','|---|---:|---:|---:|---:|']
    for row in p['rows']:
        g=row['gw']
        txt.append(f"| {g}{' (FH, BB ikke mulig)' if g==fh else ''} | {pair(row['benk_brutto'])} | {pair(row['bb_gevinst'])} | {'–' if g==fh else pair(p['alle_BB'][g-10])} | {'–' if g==fh else pair(np.array(p['alle_BB'][0])-p['alle_BB'][g-10])} |")
    collision=read(O/'BB_kollisjon.json');cp=collision['plan'];cg=collision['BB']
    txt.append(f"BB{cg} kolliderer med hovedplanens FH{fh}. For å vurdere også denne BB-datoen flyttes FH til R{collision['FH']} i **begge** sammenligningsbanene: BB10 {pair(cp['alle_BB'][0])}, BB{cg} {pair(cp['alle_BB'][cg-10])}; forskjell {pair(np.array(cp['alle_BB'][0])-cp['alle_BB'][cg-10])}. Benk brutto R{cg}: {pair(cp['rows'][cg-10]['benk_brutto'])}, netto BB {pair(cp['boost'][cg-10])}. Dermed er alle R11–R19 vurdert uten ulovlig dobbeltchip.")
    txt+=['Full benktabell for A–D: benk_per_runde.csv. Alle kombinasjoner av FH11–19 og lovlig BB10–19 finnes i chiprutenett.csv.','## Parede nye fravær og usikkerhet','Samme tilfeldige spillerfravær i alle alternativer, inkludert ikke-eide kjøpskandidater. Nye fravær begynner R11 (R10 bygger på den oppgitte informasjonen), med 1/2/3/6 runders varighet, lik sannsynlighet. Ved hver frist er bare allerede inntruffet fravær og retur kjent; nye fremtidige fravær er skjult. Fire-runders byttepolitikk reparerer adaptivt med tilgjengelige FT. BB-/FH-datoer velges på forhånd, ikke med fasit i hver verden.','1–3 % er stressnivåer, ikke estimerte skaderater. p10–p90 måler variasjon i forventede poeng mellom skadeverdener, ikke intervallet for faktiske FPL-poeng. Kampflaks, modellfeil, felles klubbsjokk og uventede rolleendringer kommer i tillegg. Modellenes forskjell i A–D-tabellen viser en annen, viktig usikkerhet.','| Nye fravær | Mot BB | Sett | BB10 minus senere | Endring fra uten nye skader | Paret p10–p90 | MC-SE |','|---|---:|---|---:|---:|---|---:|']
    for z in sim:
        if (z['alternativ']==choice and z['BB_sen'] in sorted(set([bb,19])-{10,fh})) or z['alternativ'].startswith('E_match_'):txt.append(f"| {z['p']:.0%} | {z['BB_sen']}{' (FH'+str(collision['FH'])+')' if z['alternativ'].startswith('E_match_') else ''} | {z['poengsett']} | {z['BB10_minus_sen']:+.2f} | {z['endring_fra_p0']:+.2f} | {z['delta_p10']:+.2f} til {z['delta_p90']:+.2f} | {z['paret_SE']:.2f} |")
    if sim:txt.append(f"{sim[0]['antall']} parede verdener per skaderate. Alle senere BB-datoer og alle hovedalternativer finnes i skadesim.csv; råtrekk i skadetrekk.csv.")
    if sim:
        central=[]
        for k,q in plans.items():
            fixedbb=choose_bb(q)
            zz=[v for v in sim if v['p']==.02 and v['alternativ']==k and v['BB_sen']==fixedbb]
            if len(zz)==2:central.append((sum(v['snitt'] for v in zz)/2,k,[v['snitt'] for v in zz]))
        if central:
            central.sort(reverse=True)
            txt+=['Forhåndsvalgt BB per plan, 2 % nye fravær (gjennomsnittlig forventning):','| Plan | Codex / repo |','|---|---:|']
            for ev,k,vv in central:txt.append(f'| {k} | {pair(vv)} |')
            txt.append(f'Nominal rangering velger {choice}; sentral skadestress rangerer {central[0][1]} høyest. Skadesannsynligheten er en antakelse, ikke estimert, så se forskjellens størrelse før konklusjonen tolkes som robust.')

    txt+=['## F: Free Hit sammen med BB','| FH | Beste BB | R10–R19 |','|---:|---:|---:|']
    for z in alts:
        if z['gruppe']=='F':txt.append(f"| {z['FH']} | {z['BB']} | {pair([z['codex_R10_R19'],z['repo_hybrid_R10_R19']])} |")
    txt+=['## G: kaptein og visekaptein R10','Spiller-xP er ubetinget. Ekstrakopi inkluderer reservekaptein dersom kapteinen får null minutter. Samme konkrete ellever testes i begge poengsett.','| Kaptein | Vice | Spiller-xP | Ekstrakopi med vice |','|---|---|---:|---:|']
    for z in caprows:txt.append(f"| {z['navn']} | {z['vice']} | {pair([z['codex'],z['repo_hybrid']])} | {pair([z['ekstrakopi_codex'],z['ekstrakopi_repo']])} |")
    txt+=['## FT-følsomhet','| FT nå | Beste antall R10-bytter | BB | Trekk R10 | R10–R19 |','|---:|---:|---:|---:|---:|']
    for ft in [1,2,3]:
        z=max([z for z in ftrows if z['FT']==ft],key=lambda z:z['codex_R10_R19']+z['repo_hybrid_R10_R19'])
        txt.append(f"| {ft} | {z['alternativ'].split('_')[-1]} | {z['BB']} | {z['poengtrekk_R10']} | {pair([z['codex_R10_R19'],z['repo_hybrid_R10_R19']])} |")
    txt+=['ft_sensitivitet.csv har alle kandidatplaner. FT-verdien oppstår gjennom senere faktiske modellbytter; ingen ekstra vilkårlig sparebonus legges på.','## Groß og toppspillernes nivå','Groß-testen endrer R10 p_start, forventede minutter og begge xP-sett proporsjonalt; p_play beregnes på nytt. Senere minutter holdes faste. Eksakte autobytter og senere byttepolitikk beregnes på nytt. Kandidatlisten for R10 er fast; et helt nytt best kjøp ved alvorlig skade krever nytt søk.','| Groß p_start | Minutter | Beste BB for valgt handling | BB10 total | BB19 total |','|---:|---:|---:|---:|---:|']
    for z in gross:
        if z['alternativ']==choice:txt.append(f"| {z['p_start_R10']:.3f} | {z['forventede_min']:.1f} | {z['BB_best']} | {pair([z['BB10_codex'],z['BB10_repo']])} | {pair([z['BB19_codex'],z['BB19_repo']])} |")
    txt+=['| Spiller | Observert snitt R1–R9 | Codex R10 | Repo rå R10 | Repo justert R10 | Codex / repo R10–R15 snitt |','|---|---:|---:|---:|---:|---:|']
    for z in rows(O/'kalibrering.csv'):txt.append(f"| {z['navn']} | {float(z['observert_snitt_R1_R9']):.2f} | {float(z['codex_R10']):.2f} | {float(z['repo_raw_R10']):.2f} | {float(z['repo_hybrid_R10']):.2f} | {float(z['codex_R10_R15_snitt']):.2f} / {float(z['repo_R10_R15_snitt']):.2f} |")
    txt+=['Salah finnes ikke i de 670 bootstrap-spillerne (heller ikke ved søk i fullt navn); observert snitt og prognose kan derfor ikke kontrolleres. Palmer-raden gjelder Chelsea-spilleren (ID 154), ikke navnebroren ID 301.','Observert snitt er poeng/9 runder, ikke poeng per opptreden. Prognosen bruker xG/xA, historiske priors, motstand og minutter; den skal derfor ikke nødvendigvis treffe tidligere poengsnitt. Bonus er krympet mot historikk i Codex, mens repoets nivå bevares etter minuttskalering. Se kalibrering.csv for bonuskontrollen.','## Metode, søkegrenser og etterprøvbarhet','modell.py er en selvstendig videreføring av gw09/codex/modell_r2.py: identisk eksakt integrator for uavhengige spilleutfall, lovlige autobytter, kort innhopp som blokkerer auto, samt kaptein/vice. Keeper byttes bare mot keeper. Hovedtabellene søker alle lovlige ellevere og benkerekkefølger. Simuleringen bruker R2s begrensede elleverkandidater, men eksakt forventning for hver kandidat.','R10-kandidater inkluderer alle lovlige enkeltbytter som forslag, finansieringspar fra de beste enkeltbyttene og heltallsoptimering med 1–4 bytter, tre horisonter og begge poengsett samt blanding. Kandidatene rangeres med en rullerende eierbane. FH-søket bruker heltallsforslag fra hver dato og begge modeller, deretter lokal forbedring. Senere byttesøk bruker 12 beste + 4 billigste per posisjon, enkeltbytter og avgrensede finansieringspar; de tre beste forslagene vurderes eksakt. Gratisbytte krever >1 poeng i fire-rundersvinduet (0 ved 5 FT/R19), betalt bytte >5 brutto. BB tas ikke med i bytteobjektivet. Søket er avgrenset og hovedhorisonten stopper ved chiputløpet R19, ikke sesongslutt R38. Ingen påstand om globalt maksimum for hele sesongen.','Kjør: `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH` og `python samarbeid/gw10/codex/modell.py`. Standard 100 parede verdener per stressrate; `--draws` styrer antallet. Minuttfilen bevares og brukes ved kjøring; andre resultater gjenskapes. Ingen nettverk eller installasjon. Alle skrivinger skjer i codex/.','Kontroll: alle 670 spillere × 8 runder = 5360 rader i spillerpoeng.csv (R10–R17). R18–19 ligger separat. Budsjett, posisjoner, klubbgrense og poengvekter kontrolleres automatisk. Rapporten genereres direkte fra de samme planene som alternativer.csv.']
    body='\n\n'.join(txt)+'\n'
    while '|\n\n|' in body:body=body.replace('|\n\n|','|\n|')
    (O/'analyse.md').write_text(body)


def validate(plans):
    rr=rows(O/'spillerpoeng.csv');assert len(rr)==N*8
    assert {(int(r['id']),int(r['gw'])) for r in rr}=={(p,g) for p in ids for g in range(10,18)}
    maxerr=0
    for r in rr:
        for m,key in enumerate(['codex','repo_hybrid']):maxerr=max(maxerr,abs(float(r[key])-M[m,ix[int(r['id'])],int(r['gw'])-10]))
    assert maxerr<.000001
    for p in plans.values():
        for r in p['rows']:
            s=np.array([ix[i] for i in r['tropp']]);legal(s)
            v=(M[:,s,r['gw']-10]*np.array(r['vekter'])[None,:]).sum(axis=1)-r['trekk'];assert np.allclose(v,r['poeng'])
    assert {r['gruppe'] for r in rows(O/'alternativer.csv')}>=set('ABCDEFG')
    # Independent Monte Carlo appearance check for the exact integrator.
    z=select(ORIG,BLEND[:,0],PP[:,0],POS,LUT,PERMS,True,False);rng=np.random.default_rng(123);nd=100000;plays=rng.random((nd,15))<PP[ORIG,0];xi=z[2];bn=z[3][1:];gkb=z[3][0];gk=1-gkb
    form=[sum(POS[ORIG[j]]==k for j in xi) for k in [2,3,4]];fi=form[0]*24+form[1]*4+form[2];bi=(POS[ORIG[bn[0]]]-2)*9+(POS[ORIG[bn[1]]]-2)*3+POS[ORIG[bn[2]]]-2
    misses=np.stack([(~plays[:,[j for j in xi if POS[ORIG[j]]==k]]).sum(axis=1) for k in [2,3,4]],axis=1);mi=misses[:,0]*24+misses[:,1]*4+misses[:,2];av=plays[:,bn[0]].astype(int)+2*plays[:,bn[1]]+4*plays[:,bn[2]];masks=LUT[fi,bi,mi,av]
    conditional=np.divide(BLEND[ORIG,0],PP[ORIG,0],out=np.zeros(15),where=PP[ORIG,0]>0);draw=(plays[:,xi]*conditional[xi]).sum(axis=1);draw+=(~plays[:,gk])*plays[:,gkb]*conditional[gkb]
    for j in range(3):draw+=((masks&(1<<j))>0)*conditional[bn[j]]
    draw+=plays[:,z[4]]*conditional[z[4]]+(~plays[:,z[4]])*plays[:,z[5]]*conditional[z[5]]
    se=draw.std()/np.sqrt(nd);assert abs(draw.mean()-z[0])<5*se
    jsave('kontroll.json',dict(spillere=N,rader=len(rr),maks_csv_avvik=maxerr,eksakt_auto=z[0],MC_auto=draw.mean(),MC_SE=se,status='OK'))

if __name__=='__main__':main()
