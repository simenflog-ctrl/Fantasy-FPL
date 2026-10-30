#!/usr/bin/env python3
"""GW09 offline successor to modell_r3.py (archived alongside this file).
R3: same rolling policy / same chip dates / legal ownership prices / common squads.
Rebuilds R2 calibrated scores from GW8; CBC replaces local WC search.
Run with existing Anaconda Python. All writes are below this script's directory.
minutter_antatt.csv is an input: created only if absent, never overwritten.
"""
import csv, json, math, hashlib, time
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
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
assert sum(osell.values())+16==994 and sc['goals_scored']['GKP']==10
history={int(p.stem):read(p) for p in (D/'element_summary').glob('*.json')}
kinds={1:'GKP',2:'DEF',3:'MID',4:'FWD'}; COUNTS={1:2,2:5,3:5,4:3}; GWS=list(range(9,20)); H=len(GWS)
forms=[(d,m,10-d-m) for d in range(3,6) for m in range(2,6) if 1<=10-d-m<=3]
name=lambda ps:', '.join(E[int(p)]['web_name'] for p in ps)
def named(n): return next((p for p,e in E.items() if e['web_name']==n),None)
# Frozen bot inputs; no mutable data/derived reads after initial snapshot.
pm=[r for r in rows(IN/'player_matches.csv') if int(r['gw'])<=8]; agg=defaultdict(lambda:[0.,0.]); tx=defaultdict(float)
for r in pm:
    p=int(r['element']);agg[p][0]+=float(r['minutes']);agg[p][1]+=float(r['expected_goals']);tx[int(r['fixture']),int(r['team'])]+=float(r['expected_goals'])
assert all(agg[p][0]==e['minutes'] and abs(agg[p][1]-float(e['expected_goals']))<.05 for p,e in E.items())
tm=defaultdict(lambda:[0.,0.,0])
for f in fx:
    if not f['finished'] or not f['event'] or f['event']>8:continue
    for t,op in [(f['team_h'],f['team_a']),(f['team_a'],f['team_h'])]:
        tm[t][0]+=tx[f['id'],t];tm[t][1]+=tx[f['id'],op];tm[t][2]+=1
mean=sum(v[0] for v in tm.values())/sum(v[2] for v in tm.values())
strength={t:((v[0]+7*mean)/(v[2]+7)/mean,(v[1]+7*mean)/(v[2]+7)/mean) for t,v in tm.items()}
save('lagstyrke.csv',[dict(lag=T[t],xG=v[0],xGA=v[1],kamper=v[2],angrep=strength[t][0],forsvar=strength[t][1]) for t,v in sorted(tm.items())])
# News supplied by user; quantitative effects below are model assumptions, not news facts.
blocked_names={'Saka','Semenyo','Szoboszlai','João Pedro','Sesko','Shaw','Mainoo','Mitoma'}
blocked={p for p,e in E.items() if e['web_name'] in blocked_names or e['status'] in ['u','n','i','s'] or e.get('chance_of_playing_next_round')==0}
roles={}
for p,e in E.items():
    hh=history.get(p,{}).get('history',[]);w=[.5**((8-r['round'])/4) for r in hh]
    ps=(sum(a*r['starts'] for a,r in zip(w,hh))+.35)/(sum(w)+.7) if hh else (e['starts']+.35)/8.7
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
        for lo,hi in [(9,9),(10,19)]:
            av=0 if p in blocked else ((e.get('chance_of_playing_next_round') or 50)/100 if e['status']=='d' else 1)
            q=ps*av;mi=(ps*mg+(1-ps)*subprob*submin)*av
            source='Modell: vektede starter R1–8 + prior; egen min/start; API 29. okt'
            if p in blocked:source+='; ute/kjøpsforbud fra API eller brukerens kildebelagte nyheter; retur ukjent, null gjennom R19'
            elif e['status']=='d':source+='; API d-prosent videreført R9–19, ingen antatt friskdato'
            n=e['web_name']
            if n=='B.Fernandes':
                q=.85 if lo==9 else .92;mi=90*q;source='Bruker: Sky Sports 28. okt, ventet tilbake etter benk R8. Modell: p_start 0.85 R9 / 0.92 senere, 90 min gitt start'
            if lo==9 and n in ['Haaland','Verbruggen','E.Le Fée','Thiago','Tavernier','Groß','Konsa']:
                adjustments={'Haaland':(.97,88),'Verbruggen':(.97,90),'E.Le Fée':(.90,84),'Thiago':(.88,83),'Tavernier':(.88,79),'Groß':(.76,79),'Konsa':(.94,89)}
                q,mg9=adjustments[n];mi=q*mg9+(1-q)*subprob*submin
                source+='; bruker: ligacup 27.–29. okt (hvile/belastning); numerisk justering er Codex-antakelse'
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
XP=np.array([[forecast(p,g)[0] for g in GWS] for p in ids]); REPO=XP.copy(); repo_raw={};repomin={int(r['element']):float(r['exp_minutes']) for r in rows(IN/'minutes.csv')};coverage=set()
for r in rows(IN/'expected_points.csv'):
    p,g=int(r['element']),int(r['gw']);repo_raw[p,g]=r
    if p not in ix or g not in GWS:continue
    # Match new explicit minutes in BOTH point sets. Unadjusted repo is retained in calibration file.
    oldmin=float(r['exp_minutes']);newmin=float(md[p,g]['forventede_min'])
    REPO[ix[p],g-9]=float(r['xp'])*newmin/oldmin if oldmin>0 else XP[ix[p],g-9];coverage.add((p,g))
for p in blocked:REPO[ix[p],:]=0;XP[ix[p],:]=0
MATRICES={'codex':XP,'repo_hybrid':REPO,'blend':(XP+REPO)/2}
save('spillerpoeng.csv',[dict(id=p,navn=E[p]['web_name'],gw=g,codex=round(XP[ix[p],g-9],5),repo_hybrid=round(REPO[ix[p],g-9],5)) for p in ids for g in range(9,17)])
save('spillerpoeng_R17_R19.csv',[dict(id=p,navn=E[p]['web_name'],gw=g,codex=round(XP[ix[p],g-9],5),repo_hybrid=round(REPO[ix[p],g-9],5)) for p in ids for g in range(17,20)])
cal=[]
for n in ['Haaland','B.Fernandes','Salah','Mbeumo','Rogers','Gabriel','Palmer','Isak','Watkins','Tavernier','Thiago']:
    p=named(n)
    if p is None:continue
    e=E[p];r=repo_raw.get((p,9),{})
    cal.append(dict(id=p,navn=n,pris=e['now_cost']/10,status=e['status'],observert_per_runde=round(e['total_points']/8,2),codex_R9=round(XP[ix[p],0],2),repo_raw_R9=round(float(r.get('xp',0)),2),repo_justert_R9=round(REPO[ix[p],0],2),codex_R9_R14_snitt=round(XP[ix[p],:6].mean(),2),repo_R9_R14_snitt=round(REPO[ix[p],:6].mean(),2),bonus_observert_per_runde=round(e['bonus']/8,2),bonus_codex_R9=round(forecast(p,9)[1],2),bonus_repo_raw_R9=round(float(r.get('xp_bonus',0)),2),prior=';'.join(prior_sources[p]) or 'posisjon'))
save('kalibrering.csv',cal)
# Conservative R2 role filter. d flags allowed at a lower floor because availability already reduced.
universe=frozenset(p for p,e in E.items() if p not in blocked and e.get('can_select',True) and float(md[p,9]['p_start'])>=(.35 if e['status']=='d' else .5))
save('kjopsunivers.csv',[dict(id=p,navn=E[p]['web_name'],status=E[p]['status'],p_start=md[p,9]['p_start'],godkjent=int(p in universe)) for p in ids])
def legal(s):return len(s)==15 and all(sum(E[p]['element_type']==k for p in s)==n for k,n in COUNTS.items()) and max(Counter(E[p]['team'] for p in s).values())<=3

def lineup(s,g,model='blend'):
    a=MATRICES[model][:,g-9];by={k:sorted([p for p in s if E[p]['element_type']==k],key=lambda p:(-a[ix[p]],p)) for k in COUNTS};best=None
    for d,m,f in forms:
        xi=by[1][:1]+by[2][:d]+by[3][:m]+by[4][:f];cap=max(xi,key=lambda p:(a[ix[p]],-p));v=sum(a[ix[p]] for p in xi)+a[ix[cap]]
        if best is None or v>best[0]:best=(float(v),xi,cap)
    return best

def execute(s,sv,cash,new):
    assert legal(new);cash+=sum(sv[p] for p in s-new)-sum(cost[p] for p in new-s);assert cash>=0
    return new,{p:sv[p] if p in s else cost[p] for p in new},cash

# Integer program: exact legal XI and captain per objective round; static squad, actual ownership values.
# CBC gap/bound are recorded. This is not a proof of globally optimal adaptive season policy.
solve_cache={};solve_log=[]
def optimize(g,cols,s,sv,cash,bb=None,nmoves=None,model='blend',fh=False):
    key=(g,tuple(cols),tuple(sorted(s)),tuple(sorted(sv.items())),cash,bb,nmoves,model,fh)
    if key in solve_cache:return solve_cache[key]
    candidates=sorted(universe|s) if nmoves is not None else sorted(universe)
    prob=pulp.LpProblem('FPL',pulp.LpMaximize);x=pulp.LpVariable.dicts('s',candidates,cat='Binary');price={p:sv.get(p,cost[p]) for p in candidates};liquid=cash+sum(sv.values())
    for k,n in COUNTS.items():prob+=pulp.lpSum(x[p] for p in candidates if E[p]['element_type']==k)==n
    for t in T:prob+=pulp.lpSum(x[p] for p in candidates if E[p]['team']==t)<=3
    prob+=pulp.lpSum(price[p]*x[p] for p in candidates)<=liquid
    if nmoves is not None:prob+=pulp.lpSum(x[p] for p in candidates if p not in s)==nmoves
    obj=[]
    for gw in cols:
        y=pulp.LpVariable.dicts('xi%d'%gw,candidates,cat='Binary');c=pulp.LpVariable.dicts('c%d'%gw,candidates,cat='Binary')
        prob+=pulp.lpSum(y.values())==11;prob+=pulp.lpSum(c.values())==1
        for p in candidates:prob+=y[p]<=x[p];prob+=c[p]<=y[p]
        for k,lo,hi in [(1,1,1),(2,3,5),(3,2,5),(4,1,3)]:
            prob+=pulp.lpSum(y[p] for p in candidates if E[p]['element_type']==k)>=lo;prob+=pulp.lpSum(y[p] for p in candidates if E[p]['element_type']==k)<=hi
        obj.extend(float(MATRICES[model][ix[p],gw-9])*( (x[p] if bb==gw else y[p])+c[p]) for p in candidates)
    prob+=pulp.lpSum(obj)
    solver=pulp.PULP_CBC_CMD(msg=False,timeLimit=15,gapRel=.00005,threads=1);solver.tmpDir=str(O)
    prob.solve(solver);new=frozenset(p for p in candidates if x[p].value() and x[p].value()>.5)
    assert legal(new) and sum(price[p] for p in new)<=liquid
    if nmoves is not None:assert len(new-s)==nmoves
    assert new-s<=universe
    solve_log.append(dict(gw=g,kolonner=','.join(map(str,cols)),BB=bb,bytter=nmoves,status=pulp.LpStatus[prob.status],losning_status=prob.sol_status,objektiv=round(pulp.value(prob.objective),4),bank=cash/10,modus='FH' if fh else 'WC' if nmoves is None else 'bytter'))
    solve_cache[key]=new;return new

# R3 vectorized adjacent-squad scoring; same four-GW policy for EVERY WC timing.
def components(ss,cols,model='blend'):
    ss=np.atleast_2d(ss);v=MATRICES[model][ss][:,:,np.array(cols)-9];cums=[]
    for sl in [slice(0,2),slice(2,7),slice(7,12),slice(12,15)]:
        a=np.sort(v[:,sl,:],axis=1)[:,::-1,:];cums.append(np.concatenate([np.zeros((len(ss),1,len(cols))),np.cumsum(a,axis=1)],axis=1))
    cap=v.max(axis=1);best=np.zeros_like(cap)
    for d,m,f in forms:best=np.maximum(best,cums[0][:,1]+cums[1][:,d]+cums[2][:,m]+cums[3][:,f]+cap)
    return best,v.sum(axis=1)-(best-cap)
def ordered(s):return np.array([ix[p] for p in sorted(s,key=lambda p:(E[p]['element_type'],p))])
def objective(ss,cols,bb):
    a,bn=components(ss,cols);v=a.sum(axis=1)
    if bb in cols:v+=bn[:,cols.index(bb)]
    return v

def transfers(g,s,sv,cash,ft,wc,bb,fh):
    end=min(19,g+3,wc-1 if wc and wc>g else 19);cols=[h for h in range(g,end+1) if h!=fh];n=0;hit=0
    if not cols:return s,sv,cash,n,hit
    for _ in range(min(5,ft+1)):
        a=ordered(s);base=objective(a,cols,bb)[0];cand=[]
        for out in sorted(s):
            for inc in universe-s:
                if E[inc]['element_type']!=E[out]['element_type'] or cost[inc]>cash+sv[out]:continue
                if sum(E[p]['team']==E[inc]['team'] for p in s-{out})>=3:continue
                cand.append(s-{out}|{inc})
        if not cand:break
        vv=objective(np.array([ordered(z) for z in cand]),cols,bb);j=int(vv.argmax());gain=vv[j]-base
        threshold=(0 if ft-n>=5 or g==19 else 1) if n<ft else 5
        if gain<=threshold:break
        s,sv,cash=execute(s,sv,cash,cand[j]);n+=1
        if n>ft:hit+=4;break
    return s,sv,cash,n,hit

path_cache={}
def simulate(label,initial,wc,bb=None,fh=None,ft_rule='preserve'):
    assert len([z for z in [wc,bb,fh] if z is not None])==len(set(z for z in [wc,bb,fh] if z is not None))
    key=(tuple(sorted(initial)),wc,bb,fh,ft_rule)
    if key in path_cache:return dict(path_cache[key],label=label)
    s=orig;sv=dict(osell);cash=16;ft=2;rr=[]
    for g in GWS:
        before=s;bankbefore=cash;ftbefore=ft;chip='';n=hit=0
        if g==wc:
            new=optimize(g,[h for h in range(g,20) if h!=fh],s,sv,cash,bb=bb);s,sv,cash=execute(s,sv,cash,new);active=s;chip='WC'
        elif g==fh:
            active=optimize(g,[g],s,sv,cash,fh=True);chip='FH'
        elif g==9:
            n=len(initial-s);s,sv,cash=execute(s,sv,cash,initial);active=s;hit=max(0,n-ft)*4
        else:
            s,sv,cash,n,hit=transfers(g,s,sv,cash,ft,wc,bb,fh);active=s
        if g==bb:chip='BB'
        value,xi,cap=lineup(active,g);vice=max([p for p in xi if p!=cap],key=lambda p:MATRICES['blend'][ix[p],g-9])
        bench=sorted(active-set(xi),key=lambda p:(E[p]['element_type']!=1,-MATRICES['blend'][ix[p],g-9],p))
        if chip in ['WC','FH']:ft=ftbefore if ft_rule=='preserve' else min(5,ftbefore+1) if ft_rule=='plus' else 1
        else:ft=min(5,max(0,ftbefore-n)+1)
        assert legal(s) and legal(active) and cash>=0 and 1<=ft<=5
        rr.append(dict(gw=g,chip=chip,ft_for=ftbefore,ft_etter=ft,trekk=hit,bank_for=bankbefore/10,bank=cash/10,inn=sorted(active-before),ut=sorted(before-active),tropp=sorted(active),permanent=sorted(s),owned=sv.copy(),elleve=xi,kaptein=cap,visekaptein=vice,benk=bench))
    p=dict(label=label,wc=wc,bb=bb,fh=fh,rows=rr);path_cache[key]=p;return p

def values(path,model):
    arr=MATRICES[model];out=[]
    for r in path['rows']:
        pp=r['tropp'] if r['chip']=='BB' else r['elleve'];g=r['gw']-9
        out.append(float(sum(arr[ix[p],g] for p in pp)+arr[ix[r['kaptein']],g]-r['trekk']))
    return np.array(out)
def total(p):return float(values(p,'blend').sum())

if __name__=='__main__':
    print('Forecasts ready; eligible',len(universe),'repo GWs',sorted({g for p,g in coverage}),flush=True)
    # Initial actions optimized over the bridge to WC11; retain two horizons for candidate diversity.
    initials={'A':orig};initial_variants={}
    for n,label in [(1,'B'),(2,'C'),(3,'D3'),(4,'D4'),(5,'D5')]:
        variants=[]
        for end in [9,10,12]:
            s=optimize(9,list(range(9,end+1)),orig,osell,16,nmoves=n)
            if s not in variants:variants.append(s)
        initial_variants[label]=variants
    # Neutral common calendar for initial action selection. WC10/11/12/14 tested later.
    for label,variants in initial_variants.items():
        evaluated=[simulate(label,s,11,17,13) for s in variants];best=max(evaluated,key=total);initials[label]=frozenset(best['rows'][0]['tropp'])
        print('Initial',label,name(orig-initials[label]),'->',name(initials[label]-orig),round(total(best),1),flush=True)
    bestaction=max(initials,key=lambda k:total(simulate(k,initials[k],11,17,13)))
    # Enumerate marginal BB/FH dates for each WC timing on chip-free trajectories.
    date_rows=[];candidate_pairs={(17,13),(19,13),(15,18)}
    for wc in [9,10,11,12,14]:
        base=simulate('dates',initials[bestaction],wc)
        pairs=[];marg={}
        for r in base['rows']:
            g=r['gw'];s=frozenset(r['permanent']);a,bn=components(ordered(s),[g]);bbgain=float(bn[0,0])
            if g==wc:continue
            q=optimize(g,[g],s,r['owned'],round(r['bank']*10),fh=True);fhgain=lineup(q,g)[0]-lineup(s,g)[0]
            marg[g]=(bbgain,fhgain)
            date_rows.append(dict(WC=wc,gw=g,BB_marginal=round(bbgain,2),FH_marginal=round(fhgain,2)))
        for bg,(bv,_) in marg.items():
            for fg,(_,fv) in marg.items():
                if bg!=fg:pairs.append((bv+fv,bg,fg))
        candidate_pairs.update((bg,fg) for _,bg,fg in sorted(pairs,reverse=True)[:2])
    # All retained pairs replayed for ALL WC timings; common action policy; no date confounding.
    pairs=sorted(candidate_pairs);timing=[]
    for wc in [9,10,11,12,14]:
        for bb,fh in pairs:
            if wc in [bb,fh]:continue
            p=simulate('E' if wc==9 else 'F_WC'+str(wc),initials[bestaction],wc,bb,fh);timing.append(p)
        print('WC timing',wc,'done',flush=True)
    # Select common calendar by mean across WC9/10/11, not one side's preferred calendar.
    common=max([pair for pair in pairs if all(w not in pair for w in [9,10,11,12,14])],key=lambda pair:np.mean([total(p) for p in timing if p['wc'] in [9,10,11] and (p['bb'],p['fh'])==pair]))
    bb,fh=common;plans=[]
    for label,s in initials.items():plans.append(simulate(label,s,11,bb,fh))
    for wc in [9,10,11,12,14]:plans.append(simulate('E' if wc==9 else 'F_WC'+str(wc),initials[bestaction],wc,bb,fh))
    # G: actual executable alternative calendars incl early chips, late chips and no-chip counterfactual.
    anchor=max([p for p in plans if p['label'] in ['E','F_WC10','F_WC11']],key=total)
    for pair in pairs:
        if anchor['wc'] not in pair:plans.append(simulate('G_BB%d_FH%d'%pair,initials[bestaction],anchor['wc'],*pair))
    # Explicit R9 BB / FH candidates with delayed WC; FH restores original squad and FT.
    plans.append(simulate('G_BB9',initials[bestaction],11,9,fh))
    plans.append(simulate('G_FH9',orig,11,bb,9))
    no=simulate('G_uten_BB_FH',initials[bestaction],anchor['wc']);plans.append(no)
    # Fixed concrete decisions scored under both models, including same XI and captain.
    ranked=sorted([p for p in plans if p['label']!='G_uten_BB_FH'],key=total,reverse=True)
    choice=ranked[0]
    # Recommend highest computed expected score; do not invent an information-value bonus.
    early=next(p for p in plans if p['label']=='E');late=max([p for p in plans if p['label'].startswith('F_')],key=total)
    # Parametric model-uncertainty interval; common random numbers across all paths/models.
    rng=np.random.default_rng(7089878);draws=1000
    factors=np.exp(rng.normal(-.5*.20**2,.20,(draws,N,1))+rng.normal(-.5*.10**2,.10,(draws,N,H)))
    def distribution(p,m):
        arr=MATRICES[m];out=np.zeros(draws)
        for r in p['rows']:
            t=r['gw']-9;pp=r['tropp'] if r['chip']=='BB' else r['elleve'];ii=[ix[z] for z in pp]+[ix[r['kaptein']]]
            out+=(factors[:,ii,t]*arr[ii,t]).sum(axis=1)-r['trekk']
        return out
    out=[];dists={}
    for rank,p in enumerate(sorted(plans,key=total,reverse=True),1):
        r=p['rows'][0];record=dict(alternativ=p['label'],rang_blend=rank,WC=p['wc'],BB=p['bb'],FH=p['fh'],inn=name(r['inn']),ut=name(r['ut']),poengtrekk_R9=r['trekk'],poengtrekk_R9_R19=sum(z['trekk'] for z in p['rows']),bank_etter_R9=r['bank'],FT_R10=r['ft_etter'])
        for m in ['codex','repo_hybrid']:
            vv=values(p,m);dd=distribution(p,m);dists[p['label'],m]=dd
            for suffix,n in [('R9',1),('R9_R12',4),('R9_R16',8),('R9_R19',11)]:record[m+'_'+suffix]=round(float(vv[:n].sum()),1)
            record[m+'_p10_R9_R19']=round(float(np.quantile(dd,.1)),1);record[m+'_p90_R9_R19']=round(float(np.quantile(dd,.9)),1)
        out.append(record)
    for record in out:
        for m in ['codex','repo_hybrid']:
            dd=dists[record['alternativ'],m]-dists['A',m]
            record[m+'_delta_A_p10']=round(float(np.quantile(dd,.1)),1)
            record[m+'_delta_A_p90']=round(float(np.quantile(dd,.9)),1)
    paired=[]
    for other in ['A','B','C','F_WC10','F_WC11','D3']:
        for m in ['codex','repo_hybrid']:
            dd=dists[choice['label'],m]-dists[other,m]
            paired.append(dict(anbefalt=choice['label'],mot=other,poengsett=m,delta=round(float(values(choice,m).sum()-values(next(z for z in plans if z['label']==other),m).sum()),2),p10=round(float(np.quantile(dd,.1)),2),p90=round(float(np.quantile(dd,.9)),2)))
    save('paret_usikkerhet.csv',paired)
    save('alternativer.csv',out);save('chipdatoer_marginal.csv',date_rows)
    save('wildcard_tidspunkt.csv',[dict(WC=p['wc'],BB=p['bb'],FH=p['fh'],codex=round(values(p,'codex').sum(),2),repo_hybrid=round(values(p,'repo_hybrid').sum(),2)) for p in timing])
    save('sokelog.csv',solve_log);jwrite('planer.json',plans)
    # Minutes stress on frozen concrete squads; reselect XI/captain, but no clairvoyant new transfers.
    sens=[]
    for who,probs in [('B.Fernandes',[.55,.85,.98]),('Calafiori',[0,.35,.65,.9])]:
        p=named(who);baseline={m:MATRICES[m][ix[p]].copy() for m in MATRICES};baseps=float(md[p,9]['p_start'])
        for ps in probs:
            ratio=ps/baseps
            for m in MATRICES:MATRICES[m][ix[p],0]=baseline[m][0]*ratio
            for label in dict.fromkeys(['A','B','C','E',choice['label']]):
                plan=next(z for z in plans if z['label']==label);r=plan['rows'][0];v,xi,cap=lineup(r['tropp'],9)
                rec=dict(spiller=who,p_start_R9=ps,alternativ=label,ellever=name(xi),kaptein=name([cap]))
                for m in ['codex','repo_hybrid']:rec[m+'_R9']=round(sum(MATRICES[m][ix[z],0] for z in xi)+MATRICES[m][ix[cap],0]-r['trekk'],2)
                sens.append(rec)
            for m in MATRICES:MATRICES[m][ix[p]]=baseline[m].copy()
    save('folsomhet.csv',sens)
    multistress=[]
    scenarios=[('Fernandes p_start 0.55 R9–10',[(named('B.Fernandes'),[9,10],.55)]),('Calafiori p_start 0.90 R9–10',[(named('Calafiori'),[9,10],.90)]),('Calafiori helt ute R9–10',[(named('Calafiori'),[9,10],0)]),('Begge flaggede friske fra R10',[(named(n),list(range(10,20)),float(md[named(n),10]['p_start'])/.75) for n in ['Calafiori','N.Williams']])]
    for scenario,changes in scenarios:
        backup={m:a.copy() for m,a in MATRICES.items()}
        for player,rounds_,ps in changes:
            for g in rounds_:
                ratio=ps/max(float(md[player,g]['p_start']),1e-8)
                for m in MATRICES:MATRICES[m][ix[player],g-9]*=ratio
        for lab in ['A','B','C','E','F_WC10','F_WC11']:
            p=next(z for z in plans if z['label']==lab);rr=[]
            for row in p['rows']:
                _,xi,cap=lineup(row['tropp'],row['gw']);rr.append(dict(row,elleve=xi,kaptein=cap))
            q=dict(p,rows=rr)
            multistress.append(dict(scenario=scenario,alternativ=lab,codex=round(values(q,'codex').sum(),2),repo_hybrid=round(values(q,'repo_hybrid').sum(),2)))
        for m in MATRICES:MATRICES[m]=backup[m]
    save('folsomhet_fleruker.csv',multistress)
    ft_tests=[]
    for wc in [9,10,11]:
        for rule in ['preserve','plus','reset']:
            p=simulate('ft',initials[bestaction],wc,bb,fh,rule);ft_tests.append(dict(WC=wc,FT_regel=rule,codex=round(values(p,'codex').sum(),1),repo_hybrid=round(values(p,'repo_hybrid').sum(),1)))
    save('FT_regler.csv',ft_tests);save('sokelog.csv',solve_log)
    # Report is generated from the same full-precision result objects as every CSV.
    tab={r['alternativ']:r for r in out};r=choice['rows'][0];sel=tab[choice['label']]
    lines=['# R9: beregning og anbefaling','',f"**Anbefaling: {choice['label']} – "+('wildcard i R9.' if choice['wc']==9 else f"WC i R{choice['wc']}.")+'**',
        f"R9: ut {name(r['ut']) or 'ingen'}; inn {name(r['inn']) or 'ingen'}. Trekk {r['trekk']} poeng; bank £{r['bank']:.1f}m. Dette er beregningsgrunnlag før Claudes endelige spilletidsvurdering, ikke gjennomførte FPL-handlinger.",'',
        '**Ellever:** '+name(r['elleve'])+'.', '**Kaptein:** '+name([r['kaptein']])+'. **Visekaptein:** '+name([r['visekaptein']])+'.', '**Benk:** '+name(r['benk'])+' (keeper først, deretter utespillere i prioritert rekkefølge).','',
        '## Verifisert og manglende grunnlag','',
        'Frosset API 29. okt: 15 spillere, bank £1,6m, to FT, salgsverdi £97,8m; kjøpekraft £99,4m. MUN og BHA har tre hver. Frist R9 31. okt 11:00 UTC. WC10-frist 6. nov; WC11-frist 21. nov, etter landslagspausen. TC brukt; WC1/FH1/BB1 utløper R19. Ingen blanke/doble runder i filene.',
        f"Repoets expected_points.csv har {len(coverage)} spiller/runde-rader, samtlige {N} spillere R9–R14. R15–R19 bruker Codex også i repo_hybrid. Kopier av botens filer er frosset i codex/input; datoen 26. okt er oppgitt av bruker, ikke en datostemplet kolonne i CSV. Historiske minutter og xG kontrolleres mot bootstrap for alle spillere.",
        'Salah finnes ikke i bootstrap eller repoets spillerunivers: ingen Salah-prognose eller observert snitt kan beregnes. Historikk for tidligere sesonger finnes bare for utvalget i element_summary; øvrige får posisjonsprior. Ingen returdag oppfinnes for kjøpsforbudte/skadde spillere; de er utelatt gjennom R19. Dette er konservativt og kan særlig påvirke senere WC.', '',
        '## Rangering av konkrete planer','',
        f"Alle hovedalternativer bruker BB{bb}/FH{fh}. A–D har WC11; F varierer WC-dato med identisk rullerende byttepolitikk. Rangering bygger på 50/50 gjennomsnitt av de to poengsettene. Hver rad er én konkret troppsbane med samme ellever og kaptein vurdert under begge modeller.",'',
        '| Plan | WC/BB/FH | R9 codex/repo | R9–12 | R9–16 | R9–19 | Trekk R9 | Bank |','|---|---|---:|---:|---:|---:|---:|---:|']
    for z in out:
        lines.append(f"| {z['alternativ']} | {z['WC']}/{z['BB'] or '–'}/{z['FH'] or '–'} | {z['codex_R9']:.1f}/{z['repo_hybrid_R9']:.1f} | {z['codex_R9_R12']:.1f}/{z['repo_hybrid_R9_R12']:.1f} | {z['codex_R9_R16']:.1f}/{z['repo_hybrid_R9_R16']:.1f} | {z['codex_R9_R19']:.1f}/{z['repo_hybrid_R9_R19']:.1f} | {z['poengtrekk_R9']} | {z['bank_etter_R9']:.1f} |")
    lines+=['','A = ingen R9-bytter, tre FT i R10. B/C = ett/to gratisbytter. D3/D4/D5 = tre/fire/fem bytter med −4/−8/−12, vurdert netto. E = WC9. F = senere WC. G = alternative chipkalendere; G_uten_BB_FH er bare verdireferanse, ikke anbefalt å la chips utløpe.','',
        '| Handling R9 | Ut | Inn |','|---|---|---|']
    for lab in ['A','B','C','D3','D4','D5','E']:
        z=tab[lab];lines.append(f"| {lab} | {z['ut'] or 'ingen'} | {z['inn'] or 'ingen'} |")
    lines+=['', '## Hvor robust er R9-valget?', '',
        'Anbefalingen følger høyest beregnet forventning; det er ikke lagt inn et vilkårlig poengtillegg for å vente på informasjon. Fordelen er likevel liten mot de nærmeste alternativene og må vurderes på nytt når Claude leverer minutter. Intervallene under er parede modellscenarioer, ikke sannsynligheter for faktisk gevinst.', '',
        '| Anbefalt minus | Poengsett | Forskjell R9–19 | p10–p90 |','|---|---|---:|---|']
    for z in paired:
        lines.append(f"| {z['mot']} | {z['poengsett']} | {z['delta']:+.1f} | {z['p10']:+.1f} til {z['p90']:+.1f} |")
    lines+=['', 'Uten WC er C beste testede gratisbytteplan. D-alternativene vurderes etter poengtrekk; de må slå den beste gratisplanen, ikke bare A, for å forsvare trekket. WC10/11-tabellen bruker samme konkrete R9-handling som C, slik at bytteantall ikke blandes inn i tidssammenligningen.', '']
    lines+=['','## Budsjett og faktisk tropp','', '| Spiller | Klubb | Marked | Budsjettverdi salg/kjøp | Behold/kjøp |','|---|---|---:|---:|---|']
    for p in sorted(r['tropp'],key=lambda p:(E[p]['element_type'],p)):
        lines.append(f"| {E[p]['web_name']} | {T[E[p]['team']]} | {cost[p]/10:.1f} | {osell[p]/10 if p in osell else cost[p]/10:.1f} | {'behold' if p in orig else 'kjøp'} |")
    lines+=['', '| Utgående spiller | Verifisert salgspris |','|---|---:|']
    for p in r['ut']:lines.append(f"| {E[p]['web_name']} | £{osell[p]/10:.1f}m |")
    sold=sum(osell[p] for p in r['ut']);bought=sum(cost[p] for p in r['inn'])
    if r['chip']!='FH':assert 16+sold-bought==round(r['bank']*10)
    lines+=['',f"Kontroll: £1,6m + salg £{sold/10:.1f}m − kjøp £{bought/10:.1f}m = £{r['bank']:.1f}m. Alle baner kontrolleres for 2/5/5/3 posisjoner, maks tre per klubb, ikke-negativ bank og lovlig kjøpsunivers. Beholdte spillere belastes salgsverdi i WC-budsjettet; man betaler ikke markedspris for å beholde egne prisstigninger.", '',
        '## Foreløpig viderebane for anbefalingen','', '| Runde | Chip | Ut | Inn | FT etter | Bank |','|---|---|---|---|---:|---:|']
    for step in choice['rows']:
        lines.append(f"| {step['gw']} | {step['chip'] or '–'} | {name(step['ut']) or 'ingen'} | {name(step['inn']) or 'ingen'} | {step['ft_etter']} | {step['bank']:.1f} |")
    lines+=['', 'FH-troppen er midlertidig; oppgitt bank er den permanente bankbeholdningen som kommer tilbake etter FH. Alle fremtidige kjøp er foreløpige med frosne priser og nyheter.', '',
        '## WC-tidspunkt med lik chipkalender','', '| WC | codex R9–19 | repo R9–19 |','|---|---:|---:|']
    for wc in [9,10,11,12,14]:
        p=next(z for z in timing if z['wc']==wc and (z['bb'],z['fh'])==common);lines.append(f"| {wc} | {values(p,'codex').sum():.1f} | {values(p,'repo_hybrid').sum():.1f} |")
    lines+=['',f"Felles kalender valgt fra {len(pairs)} kandidatpar etter gjennomsnittlig resultat for WC9/10/11. wildcard_tidspunkt.csv inneholder alle par som er spilt gjennom. Søket vurderer marginal BB/FH-verdi i alle lovlige runder, spiller gjennom topprangerte sene par og faste kontrollpar, samt BB9/FH9. Dette er ikke et uttømmende globalt optimum over alle datoer og fremtidige bytter.",
        'Alle bruker neste fire runder (avkortet før WC, FH utelatt, BB inkludert). Gratisbytte krever >1 poeng forbedring, ved fem FT eller R19 >0; ett ekstra betalt bytte krever >5 brutto. Maks fem lagrede FT. WC/FH antas å bevare FT uten opptjening; reset og +1 er prøvd i FT_regler.csv. Prisene fryses. Fremtidige skader, ny informasjon og informasjonsverdien av landslagspausen er ikke simulert eller priset.', '',
        '## BB og FH','',
        f"Valgt konkret plan: BB{choice['bb']} og FH{choice['fh']}. chipdatoer_marginal.csv viser separat benkeverdi og FH-gevinst fra chipfrie baner; G-radene inkluderer den endrede byttebanen. BB/FH-overlapp og overlapp med WC er utelukket. Cupflyttinger og juleturnover kan endre dette; datoene er foreløpige.", '',
        f"Med samme WC{anchor['wc']} og samme R9-handling gir BB{bb}/FH{fh} samlet {values(anchor,'codex').sum()-values(no,'codex').sum():.1f}/{values(anchor,'repo_hybrid').sum()-values(no,'repo_hybrid').sum():.1f} ekstra poeng mot den beregnede banen uten BB/FH. Dette inkluderer endrede bytter, ikke bare en løs chipbonus.", '',
        '## Kalibrering og bonus','',
        '| Spiller | Observert/runde | Codex R9 | Repo rå R9 | Repo justert R9 | Bonus obs./Codex/repo rå |','|---|---:|---:|---:|---:|---|']
    for z in cal:lines.append(f"| {z['navn']} | {z['observert_per_runde']:.1f} | {z['codex_R9']:.1f} | {z['repo_raw_R9']:.1f} | {z['repo_justert_R9']:.1f} | {z['bonus_observert_per_runde']:.1f}/{z['bonus_codex_R9']:.1f}/{z['bonus_repo_raw_R9']:.1f} |")
    lines+=['','Codex viderefører R2/R3: nåværende xG/xA/bonus per 90 krympes mot inntil to tidligere sesonger (540 prior-minutter; ellers posisjonsprior 270). Lagstyrke krympes med syv kamper; xGA er motstanderens samlede xG. Poisson for nullen/innslupne/redninger; empirisk defensive-contribution-treffrate. Alle poengvekter kommer fra game_config.scoring, keepermål 10. Bonus følger historisk bonusrate, ikke en ny premiumrabatt. Ingen ny kalibrering ut fra én enkelt R8-kamp. Repoets høyere premiumbonus beholdes i repo_hybrid og synliggjøres i tabellen.',
        'Repo-hybrid skalerer rå xP med våre forventede minutter / repoets minutter for å bruke samme nyhetsgrunnlag. Dette er en tilnærming, særlig ved 60-minuttersgrensen. R15–19 er lik Codex, så modellspennet der er ikke uavhengig. Modellen beregner forventet valgt ellever + kaptein, uten autobytter eller visekaptein-overføring ved null minutter; benkedekning kan derfor være undervurdert.', '',
        '## Usikkerhet og følsomhet','',
        f"For valgt plan er forventning R9 {sel['codex_R9']:.1f}/{sel['repo_hybrid_R9']:.1f}; R9–19 {sel['codex_R9_R19']:.1f}/{sel['repo_hybrid_R9_R19']:.1f}. Modellfølsomhet p10–p90: Codex {sel['codex_p10_R9_R19']:.1f}–{sel['codex_p90_R9_R19']:.1f}, repo {sel['repo_hybrid_p10_R9_R19']:.1f}–{sel['repo_hybrid_p90_R9_R19']:.1f}.",
        'Intervallene kommer fra 1 000 parede lognormale rater: 20 % vedvarende spillerusikkerhet og 10 % ekstra per runde, middel 1. Dette er antatt modellspredning, ikke kalibrerte konfidensintervaller eller intervaller for faktiske kamppoeng. Ingen kamputfallsstøy, ny skadeprosess eller ny bytteoptimering i trekkene. Spillerfaktorer er felles på tvers av planene. Tall vises med én desimal for kontroll, men små forskjeller er ikke beslutningspresisjon.', '',
        '| Følsomhet valgt handling | p_start R9 | Codex R9 | Repo R9 | Valgt minus C, codex/repo R9 |','|---|---:|---:|---:|---:|']
    for z in sens:
        if z['alternativ']==choice['label']:
            c=next(t for t in sens if t['alternativ']=='C' and t['spiller']==z['spiller'] and t['p_start_R9']==z['p_start_R9'])
            lines.append(f"| {z['spiller']} | {z['p_start_R9']:.2f} | {z['codex_R9']:.1f} | {z['repo_hybrid_R9']:.1f} | {z['codex_R9']-c['codex_R9']:+.1f}/{z['repo_hybrid_R9']-c['repo_hybrid_R9']:+.1f} |")
    lines+=['', '| Flerukescenario, faste kjøp | E minus WC10, codex/repo | E minus C/WC11, codex/repo |','|---|---:|---:|']
    for scenario,_ in scenarios:
        ss={z['alternativ']:z for z in multistress if z['scenario']==scenario}
        lines.append(f"| {scenario} | {ss['E']['codex']-ss['F_WC10']['codex']:+.1f}/{ss['E']['repo_hybrid']-ss['F_WC10']['repo_hybrid']:+.1f} | {ss['E']['codex']-ss['C']['codex']:+.1f}/{ss['E']['repo_hybrid']-ss['C']['repo_hybrid']:+.1f} |")
    lines+=['','Flerukescenarioene er betingede antakelser, ikke nye nyheter. XI/kaptein velges på nytt; kjøpsbanen er frosset, så tabellen måler følsomhet for de konkrete planene, ikke reoptimalt byttevalg. Full tabell i folsomhet_fleruker.csv.', '', 'Følsomhet endrer R9-poeng proporsjonalt med start/minutter og velger ny lovlig ellever/kaptein i samme tropp. Calafiori testes også helt ute. Dette er ikke en medisinsk returmodell. Full tabell for A/B/C/E og anbefalingen i folsomhet.csv. Fernandes har 0,85 start R9 og 0,92 senere; Calafioris og N.Williams’ 75 %-flagg videreføres uten sikker retur. Groß reduseres etter cupbelastning; hvile for Haaland/Verbruggen/Le Fée og belastning for Thiago/Tavernier er eksplisitte antakelser i minutter_antatt.csv. Claude kan endre denne filen og kjøre modellen på nytt.', '',
        '## Søkeavgrensning og reproduksjon','',
        'B/C/D har heltallsoptimaliserte kandidater for R9 alene, R9–10 og R9–12; beste faktiske viderebane av disse velges. Tre, fire og fem bytter med trekk vurderes. WC/FH optimaliseres som statisk tropp over relevante runder med eksakt lovlig ellever/kaptein i hvert ledd, hele det godkjente kjøpsuniverset, CBC maks 15 sekunder og relativ toleranse 0,005 %. Ingen global optimalitetsgaranti for adaptiv sesongplan. sokelog.csv viser løserstatus; begrenset tid kan gi bare en gjennomførbar løsning. Kjøpsunivers krever normalt p_start ≥0,5 (d ≥0,35), samme konservative rolleprinsipp som R8; derfor er optimum betinget av filteret.',
        'Kjør: `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH` og `python samarbeid/gw09/codex/modell.py`. Bruker eksisterende numpy/PuLP/CBC. Ingen nettverk eller installasjon. modell_r3_original.py er urørt kopi som metodeproveniens; modell.py er selvstendig og leser ikke R8-filer. minutter_antatt.csv overskrives ikke. Rå input, minuttscenario og spillerprognoser har SHA256 i validering.json. Alle CSV-er og denne rapporten genereres i samme kjøring; planer.json gir hele byttebanen.']
    report='\n'.join(lines)+'\n';(O/'analyse.md').write_text(report)
    forecast_rows=rows(O/'spillerpoeng.csv');assert len(forecast_rows)==N*8 and len({(x['id'],x['gw']) for x in forecast_rows})==N*8
    assert {z['alternativ'][0] for z in out}>={'A','B','C','D','E','F','G'}
    assert tab['A']['FT_R10']==3
    for z in out:assert f"{z['codex_R9_R19']:.1f}/{z['repo_hybrid_R9_R19']:.1f}" in report
    hashes={str(p.relative_to(O.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*sorted(D.rglob('*.json')),O/'modell.py',mp,O/'spillerpoeng.csv',O/'spillerpoeng_R17_R19.csv',*sorted(IN.glob('*.csv'))]}
    jwrite('validering.json',dict(spillere=N,spillerpoengrader=len(forecast_rows),repo_runder=sorted({g for p,g in coverage}),anbefaling=choice['label'],felles_BB_FH=common,solver_ikke_bevist_optimal=sum(z['losning_status']!=1 for z in solve_log),kontroller='Alle assertions passerte; rapport/CSV fra samme objekter',sha256=hashes))
    print('DONE recommendation',choice['label'],'common calendar',common,'files',len(list(O.iterdir())),flush=True)
