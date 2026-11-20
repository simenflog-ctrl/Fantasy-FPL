#!/usr/bin/env python3
"""GW11 continuation of GW10 modell.py and modell_r2.py.
Exact independent-appearance autosubs and paired adaptive injury worlds.
R11-R19; frozen local data; no network/install or writes outside this directory.
Minutes are regenerated from frozen input/minutter_overstyring.csv.
"""
import csv, json, math, hashlib, time, io
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
    buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
    payload=buf.getvalue().encode();dest=O/n
    if dest.exists() and dest.read_bytes()==payload:return
    tmp=dest.with_suffix(dest.suffix+'.tmp');tmp.write_bytes(payload);tmp.replace(dest)
def jwrite(n,obj):
    dest=O/n;tmp=dest.with_suffix(dest.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2));tmp.replace(dest)

b=read(D/'bootstrap.json'); E={e['id']:e for e in b['elements']}; ids=sorted(E); ix={p:i for i,p in enumerate(ids)}; N=len(ids)
T={t['id']:t['short_name'] for t in b['teams']}; sc=b['game_config']['scoring']; fx=read(D/'fixtures.json'); sales=read(D/'salgspriser.json')
cost={p:e['now_cost'] for p,e in E.items()}; orig=frozenset(r['id'] for r in sales); osell={r['id']:round(10*r['salgspris']) for r in sales}
assert sum(osell.values())+4==999 and sc['goals_scored']['GKP']==10
history={int(p.stem):read(p) for p in (D/'element_summary').glob('*.json')}
kinds={1:'GKP',2:'DEF',3:'MID',4:'FWD'}; COUNTS={1:2,2:5,3:5,4:3}; FIRST=11; LAST=19; LATEST=10; GWS=list(range(FIRST,LAST+1)); H=len(GWS)
forms=[(d,m,10-d-m) for d in range(3,6) for m in range(2,6) if 1<=10-d-m<=3]
name=lambda ps:', '.join(E[int(p)]['web_name'] for p in ps)
def named(n): return next((p for p,e in E.items() if e['web_name']==n),None)
# Frozen bot inputs; no mutable data/derived reads after initial snapshot.
expected_hashes={'expected_points.csv':'5e94dc6f6547db98174230d3f40aa15ad837087c2afc7abb2ada8ce33a6ead19','player_matches.csv':'c953d4a1e4a79a553882a213ea6cf9ea19fdb9f34fe6738b842cc068becc4842'}
for filename,digest in expected_hashes.items():assert hashlib.sha256((IN/filename).read_bytes()).hexdigest()==digest,filename
pm=[r for r in rows(IN/'player_matches.csv') if int(r['gw'])<=10]; agg=defaultdict(lambda:[0.,0.]); tx=defaultdict(float)
for r in pm:
    p=int(r['element']);agg[p][0]+=float(r['minutes']);agg[p][1]+=float(r['expected_goals']);tx[int(r['fixture']),int(r['team'])]+=float(r['expected_goals'])
assert all(agg[p][0]==e['minutes'] and abs(agg[p][1]-float(e['expected_goals']))<.05 for p,e in E.items())
tm=defaultdict(lambda:[0.,0.,0])
for f in fx:
    if not f['finished'] or not f['event'] or f['event']>10:continue
    for t,op in [(f['team_h'],f['team_a']),(f['team_a'],f['team_h'])]:
        tm[t][0]+=tx[f['id'],t];tm[t][1]+=tx[f['id'],op];tm[t][2]+=1
mean=sum(v[0] for v in tm.values())/sum(v[2] for v in tm.values())
strength={t:((v[0]+7*mean)/(v[2]+7)/mean,(v[1]+7*mean)/(v[2]+7)/mean) for t,v in tm.items()}
save('lagstyrke.csv',[dict(lag=T[t],xG=v[0],xGA=v[1],kamper=v[2],angrep=strength[t][0],forsvar=strength[t][1]) for t,v in sorted(tm.items())])
# News supplied by user; quantitative effects below are model assumptions, not news facts.
blocked={p for p,e in E.items() if e['status'] in ['u','n','i','s'] or e.get('chance_of_playing_next_round')==0}
roles={}
for p,e in E.items():
    hh=history.get(p,{}).get('history',[]);w=[.5**((10-r['round'])/4) for r in hh]
    ps=(sum(a*r['starts'] for a,r in zip(w,hh))+.35)/(sum(w)+.7) if hh else (e['starts']+.35)/10.7
    starts=[r for r in hh if r['starts']];subs=[r for r in hh if not r['starts'] and r['minutes']>0]
    mg=sum(r['minutes'] for r in starts)/len(starts) if starts else min(90,e['minutes']/max(1,e['starts']))
    subprob=len(subs)/max(1,len(hh)-len(starts)); submin=sum(r['minutes'] for r in subs)/max(1,len(subs))
    p60cond=(sum(r['minutes']>=60 for r in starts)+4.5)/(len(starts)+5)
    roles[p]=(ps,mg,subprob,submin,p60cond)
# Only the frozen Claude overrides may change the standard minute model.
mp=O/'minutter_antatt.csv'
overrides=rows(IN/'minutter_overstyring.csv');rr=[]
for p,e in E.items():
    ps,mg,subprob,submin,p60c=roles[p]
    for g in GWS:
        av=0 if p in blocked else ((e.get('chance_of_playing_next_round') or 50)/100 if e['status']=='d' else 1)
        q=ps*av;mi=(ps*mg+(1-ps)*subprob*submin)*av
        source='Modell: vektede starter R1–10 + prior; egne min/start; API 19. nov'
        if p in blocked:source+='; API ute: null uten eksplisitt returoverstyring'
        elif e['status']=='d':source+='; API d-prosent holdt konstant'
        for ov in overrides:
            match=(ov['id'] and int(ov['id'])==p) or (ov['lag'] and ov['lag']==T[e['team']])
            if not match or not int(ov['gw_fra'])<=g<=int(ov['gw_til']):continue
            if ov['faktor']:q*=float(ov['faktor']);mi*=float(ov['faktor'])
            if ov['p_start']:q=float(ov['p_start'])
            if ov['forventede_min']:mi=float(ov['forventede_min'])
            source+='; '+ov['kilde']
        rr.append(dict(id=p,navn=e['web_name'],lag=T[e['team']],gw_fra=g,gw_til=g,p_start=round(q,4),forventede_min=round(mi,2),kilde=source))
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
        PP[ix[p],g-FIRST]=min(1,ps+max(0,av-ps)*subprob) if mi else 0
        if (p,g) in repo_raw:
            raw=repo_raw[p,g];oldmin=float(raw['exp_minutes']);REPO[ix[p],g-FIRST]=float(raw['xp'])*mi/oldmin if oldmin else XP[ix[p],g-FIRST]
# Blocked players already have zero minutes, except the explicit Thiago return.
PURCHASE=np.array([[p not in blocked or (p==106 and g>=14) for g in GWS] for p in ids])
M=np.array([XP,REPO]);BLEND=M.mean(axis=0)
UI=np.array([ix[p] for p in ids if PURCHASE[ix[p]].any() and E[p].get('can_select',True) and float(md[p,14 if p==106 else FIRST]['p_start'])>=(.35 if E[p]['status']=='d' else .5)],dtype=np.int64)
save('spillerpoeng.csv',[dict(id=p,navn=E[p]['web_name'],gw=g,codex=round(XP[ix[p],g-FIRST],6),repo_hybrid=round(REPO[ix[p],g-FIRST],6)) for p in ids for g in GWS])
save('p_play.csv',[dict(id=p,navn=E[p]['web_name'],gw=g,p_start=md[p,g]['p_start'],p_play=PP[ix[p],g-FIRST]) for p in ids for g in GWS])
save('kalibrering.csv',[dict(id=p,navn=E[p]['web_name'],observert_snitt_R1_R10=E[p]['total_points']/10,codex_R11=XP[ix[p],0],repo_raw_R11=float(repo_raw.get((p,FIRST),{}).get('xp',0)),repo_hybrid_R11=REPO[ix[p],0],codex_R11_R16_snitt=XP[ix[p],:6].mean(),repo_R11_R16_snitt=REPO[ix[p],:6].mean(),bonus_observert=E[p]['bonus']/10,bonus_codex_R11=forecast(p,FIRST)[1]) for p in ids if E[p]['now_cost']>=60 and E[p]['web_name'] in ['Haaland','Salah','Palmer','B.Fernandes','Mbeumo','Gabriel','Isak','Watkins','Tavernier','Rogers']])
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
        q=UI[(POS[UI]==k)&avail[UI]&PURCHASE[UI,cols[0]]];v=pred[q][:,cols].sum(axis=1)
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
    end=min(19,g+3,wc-1 if wc>g else 19);cols=[h-FIRST for h in range(g,end+1) if h!=FH];n=hits=0
    if not cols:return s,sv,cash,n,hits
    for _ in range(min(5,ft+1)):
        ps=pools(pred,cols,avail);liquid=int(cash+sv[s].sum());nn=neighbors(s,ps,sv,liquid)
        if not len(nn):break
        ap=approx(nn,pred,pp,cols,bb-FIRST);first=np.argsort(-ap)[:3]
        # Two-swap financing candidates, same proposal rule in every WC timing.
        if n<ft:
            extra=[]
            for j in first:
                for q in neighbors(nn[j],ps,sv,liquid):
                    if len(set(q)-set(s))==2:extra.append(q)
            if extra:nn=np.concatenate([nn,np.array(extra)])
        nn=np.unique(nn,axis=0);ap=approx(nn,pred,pp,cols,bb-FIRST);counts=np.array([len(set(q)-set(s)) for q in nn]);valid=counts<=ft-n+1;nn=nn[valid];ap=ap[valid];counts=counts[valid]
        costhit=4*np.maximum(0,counts-(ft-n));rank=np.argsort(-(ap-costhit));short=nn[rank[:3]];counts=counts[rank[:3]]
        base=obj_batch(s[None,:],pred,pp,np.array(cols),bb-FIRST,POS,LUT,PERMS)[0]
        vv=obj_batch(short,pred,pp,np.array(cols),bb-FIRST,POS,LUT,PERMS);scores=vv-4*np.maximum(0,counts-(ft-n));j=scores.argmax();cnt=int(counts[j]);gain=vv[j]-base
        paid=max(0,cnt-(ft-n));free=cnt-paid;threshold=(0 if ft-n==5 or g==19 else free)+5*paid
        if gain<=threshold+1e-7:break
        s,sv,cash=transact(s,short[j],sv,cash);n+=cnt;hits+=4*paid
        if paid:break
    return s,sv,cash,n,hits


TEMPLATES=[]
def renew(g,s,sv,cash,pred,pp,avail,fh=False,ban=None,bb=19,keep=None):
    cols=list(range(g-FIRST,H)) if not fh else [g-FIRST];cols=[t for t in cols if fh or t!=FH-FIRST];ps=pools(pred,cols,avail);liquid=int(cash+sv[s].sum());seeds=[]
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
    ss=np.unique(np.array(seeds),axis=0);ap=approx(ss,pred,pp,cols,bb-FIRST);ss=ss[np.argsort(-ap)[:4]]
    vv=obj_batch(ss,pred,pp,np.array(cols),bb-FIRST,POS,LUT,PERMS);best=ss[vv.argmax()].copy();value=vv.max()
    for _ in range(3):
        nn=neighbors(best,ps,sv,liquid)
        if ban is not None:nn=nn[~np.any(nn==ban,axis=1)]
        if keep is not None:nn=nn[np.any(nn==keep,axis=1)]
        if not len(nn):break
        ap=approx(nn,pred,pp,cols,bb-FIRST);nn=nn[np.argsort(-ap)[:3]]
        vv=obj_batch(nn,pred,pp,np.array(cols),bb-FIRST,POS,LUT,PERMS);j=vv.argmax()
        if vv[j]<=value+1e-7:break
        best=nn[j].copy();value=vv[j]
    legal(best);assert all(avail[i] or i in s for i in best)
    if ban is not None:assert ban not in best
    return ordered(best)


# MILP proposes candidates; all final comparisons use R2's exact autosub integrator.
def seed(cols,nmoves=None,model=2,bb=None):
    eligible=UI[PURCHASE[UI,FIRST-FIRST if nmoves is not None else min(cols)-FIRST]]
    candidates=sorted(set(eligible)|set(ORIG)) if nmoves is not None else list(eligible)
    pred=BLEND if model==2 else M[model]
    prob=pulp.LpProblem('GW11',pulp.LpMaximize)
    x=pulp.LpVariable.dicts('s',candidates,cat='Binary');price=SALES.copy()
    for k,n in [(1,2),(2,5),(3,5),(4,3)]:prob+=pulp.lpSum(x[i] for i in candidates if POS[i]==k)==n
    for t in T:prob+=pulp.lpSum(x[i] for i in candidates if TEAM[i]==t)<=3
    prob+=pulp.lpSum(int(price[i])*x[i] for i in candidates)<=999
    if nmoves is not None:prob+=pulp.lpSum(x[i] for i in candidates if i not in ORIG)==nmoves
    obj=[]
    for g in cols:
        y=pulp.LpVariable.dicts('xi'+str(g),candidates,cat='Binary');c=pulp.LpVariable.dicts('c'+str(g),candidates,cat='Binary')
        prob+=pulp.lpSum(y.values())==11;prob+=pulp.lpSum(c.values())==1
        for i in candidates:prob+=y[i]<=x[i];prob+=c[i]<=y[i]
        for k,lo,hi in [(1,1,1),(2,3,5),(3,2,5),(4,1,3)]:
            prob+=pulp.lpSum(y[i] for i in candidates if POS[i]==k)>=lo
            prob+=pulp.lpSum(y[i] for i in candidates if POS[i]==k)<=hi
        obj.extend(float(pred[i,g-FIRST])*((x[i] if bb==g else y[i])+c[i]) for i in candidates)
    prob+=pulp.lpSum(obj)
    solver=pulp.PULP_CBC_CMD(msg=False,timeLimit=8,gapRel=.0001,threads=1);solver.tmpDir=str(O)
    prob.solve(solver);s=ordered(i for i in candidates if x[i].value() is not None and x[i].value()>.5)
    legal(s);assert SALES[s].sum()<=999
    if nmoves is not None:assert len(set(s)-set(ORIG))==nmoves
    return s


def trajectory(initial,ft0=3,fh=16,world=None,full=False,arrays=None,record=True):
    """Identical four-round normal-XI transfer policy for every BB date.
    BB does not alter ownership, FT use or FH date. This permits paired comparison
    of all nine BB dates on one adaptive ownership trajectory, without hindsight.
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
        elif g==fh:active=renew(g,s,sv,cash,pred,pp,av&PURCHASE[:,t],fh=True,bb=99)
        else:
            s,sv,cash,n,hit=rolling(g,s,sv,cash,ft,pred,pp,av&PURCHASE[:,t],99,bb=99);active=s
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
    totals=normal.sum(axis=0)[None,:]+boost;totals[fh-FIRST]=np.nan
    return dict(FH=fh,FT=ft0,total_uten_BB=normal.sum(axis=0).tolist(),alle_BB=totals.tolist(),normal=normal.tolist(),boost=boost.tolist(),rows=rr)


def choose_bb(p):return int(np.nanargmax(np.mean(p['alle_BB'],axis=1)))+FIRST

def alternative(label,p,bb,group=None):
    r=p['rows'][0];points=np.array(p['normal']).copy();points[bb-FIRST]+=p['boost'][bb-FIRST]
    z=dict(alternativ=label,gruppe=group or label[0],FT=p['FT'],BB=bb,FH=p['FH'],ut=name(ix[i] for i in r['ut']),inn=name(ix[i] for i in r['inn']),poengtrekk_R11=r['trekk'],poengtrekk_totalt=sum(r['trekk'] for r in p['rows']),bank_etter=r['bank'])
    for m,model in enumerate(['codex','repo_hybrid']):
        for suffix,n in [('R11',1),('R11_R14',4),('R11_R19',H)]:z[model+'_'+suffix]=float(points[:n,m].sum())
    z['modellspredning_R11_R19']=abs(z['codex_R11_R19']-z['repo_hybrid_R11_R19'])
    z['skade_p10_blend']='';z['skade_p90_blend']=''
    return z


def validate(plans):
    rr=rows(O/'spillerpoeng.csv');assert len(rr)==N*H
    assert {(int(r['id']),int(r['gw'])) for r in rr}=={(p,g) for p in ids for g in GWS}
    maxerr=0
    for r in rr:
        for m,key in enumerate(['codex','repo_hybrid']):maxerr=max(maxerr,abs(float(r[key])-M[m,ix[int(r['id'])],int(r['gw'])-FIRST]))
    assert maxerr<.000001
    for p in plans.values():
        for r in p['rows']:
            s=np.array([ix[i] for i in r['tropp']]);legal(s)
            v=(M[:,s,r['gw']-FIRST]*np.array(r['vekter'])[None,:]).sum(axis=1)-r['trekk'];assert np.allclose(v,r['poeng'])
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

if __name__=='__main__':
    import sys
    from modell_r2 import run
    run(sys.modules[__name__])
