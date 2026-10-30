#!/usr/bin/env python3
"""Read-only R1 import; exact independent-appearance autosubs, paired injury worlds.
All output filenames are new *_r2 files (report: kontroll.md). No network/install.
"""
import ast,csv,json,math,hashlib,itertools,time
from pathlib import Path
from collections import Counter
import numpy as np
from numba import njit
O=Path(__file__).resolve().parent
# Execute R1 definitions/setup with BOTH output helpers replaced by no-ops; never its main.
tree=ast.parse((O/'modell.py').read_text())
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ('save','jwrite'):node.body=[ast.Pass()]
ns={'__file__':str(O/'modell.py'),'__name__':'r1_readonly'}
exec(compile(ast.fix_missing_locations(tree),str(O/'modell.py')+' [writes disabled]','exec'),ns)
E=ns['E'];ids=ns['ids'];ix=ns['ix'];N=len(ids);T=ns['T'];md=ns['md'];roles=ns['roles'];sc=ns['sc'];fx=ns['fx'];GWS=list(range(9,20));H=11
POS=np.array([E[p]['element_type'] for p in ids]);TEAM=np.array([E[p]['team'] for p in ids]);COST=np.array([ns['cost'][p] for p in ids]);SALES=COST.copy()
for p,v in ns['osell'].items():SALES[ix[p]]=v
ORIG=np.array(sorted([ix[p] for p in ns['orig']],key=lambda i:(POS[i],i)),dtype=np.int64)
name=lambda aa:', '.join(E[ids[int(i)]]['web_name'] for i in aa)
named=lambda n:ix[ns['named'](n)]
BB=19;FH=16

def save(n,rr):
    assert n.endswith('_r2.csv') and rr
    with (O/n).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
def jsave(n,obj):
    assert n.endswith('_r2.json');(O/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
def ordered(ss):return np.array(sorted(set(int(i) for i in ss),key=lambda i:(POS[i],i)),dtype=np.int64)

def legal(s):
    assert len(s)==len(set(s))==15
    assert [int(sum(POS[s]==k)) for k in range(1,5)]==[2,5,5,3]
    assert max(Counter(TEAM[s]).values())<=3

# Only requested Claude overrides; preserve conditional minutes by scaling target rows.
minute_rows=ns['rows'](O/'minutter_antatt.csv')
for r in minute_rows:
    if int(r['gw_fra'])==9 and r['navn'] in ['B.Fernandes','Calafiori']:
        ps={'B.Fernandes':.75,'Calafiori':.50}[r['navn']];ratio=ps/float(r['p_start'])
        r['forventede_min']=round(float(r['forventede_min'])*ratio,4);r['p_start']=ps;r['kilde']='Claude/forutsetninger.md 29. okt: R9 p_start; forventede minutter proporsjonalt, øvrige uendret'
    for g in range(int(r['gw_fra']),int(r['gw_til'])+1):md[int(r['id']),g]=dict(r)
save('minutter_antatt_r2.csv',minute_rows)
XP=np.array([[ns['forecast'](p,g)[0] for g in GWS] for p in ids]);REPO=XP.copy();PP=np.zeros_like(XP)
for p in ids:
    e=E[p];_,_,subprob,_,_=roles[p]
    for g in GWS:
        r=md[p,g];ps=float(r['p_start']);mi=float(r['forventede_min']);av=max(ps,(e.get('chance_of_playing_next_round') or 50)/100) if e['status']=='d' else 1
        PP[ix[p],g-9]=min(1,ps+max(0,av-ps)*subprob) if mi else 0
        if (p,g) in ns['repo_raw']:
            raw=ns['repo_raw'][p,g];oldmin=float(raw['exp_minutes']);REPO[ix[p],g-9]=float(raw['xp'])*mi/oldmin if oldmin else XP[ix[p],g-9]
for p in ns['blocked']:XP[ix[p]]=0;REPO[ix[p]]=0;PP[ix[p]]=0
M=np.array([XP,REPO]);BLEND=M.mean(axis=0)
ns['MATRICES']={'codex':M[0],'repo_hybrid':M[1],'blend':BLEND}
UI=np.array(sorted(ix[p] for p in ns['universe']),dtype=np.int64)
for label,rg in [('spillerpoeng_r2.csv',range(9,17)),('spillerpoeng_sen_r2.csv',range(17,20))]:
    save(label,[dict(id=p,navn=E[p]['web_name'],gw=g,codex=round(XP[ix[p],g-9],6),repo_hybrid=round(REPO[ix[p],g-9],6)) for p in ids for g in rg])
save('p_play_r2.csv',[dict(id=p,navn=E[p]['web_name'],gw=g,p_start=md[p,g]['p_start'],p_play=round(PP[ix[p],g-9],6)) for p in ids for g in GWS])

# LUT: legitimate substitutions by nominal formation and ordered bench positions.
# Missing slots remain slots, not a requirement that actual playing survivors satisfy 3/2/1.
# Prefer first available bench player whenever a valid matching exists; then next.
# Subset feasibility: substitute into distinct absent starter slots and retain legal XI formation.
LUT=np.zeros((144,27,144,8),dtype=np.int8)
forms=ns['forms']
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
        top=q[np.argsort(-v,kind='stable')[:9]];cheap=q[np.lexsort((q,COST[q]))[:4]]
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

BRIDGE=[]
TEMPLATES=[]
for p in ns['read'](O/'planer.json'):
    for r in p['rows']:
        if r['chip'] in ['WC','FH']:
            s=ordered(ix[z] for z in r['tropp'])
            if not any(np.array_equal(s,z) for z in TEMPLATES):TEMPLATES.append(s)

# MILP only supplies static objective seed squads, then autosub objective chooses/refines.
def integer_seed(g,bb=19,ban=None,keep=None,nmoves=None,end=19):
    olduniverse=ns['universe'];oldmat=ns['MATRICES'];ns['optcache']={} if 'optcache' in ns else {}
    ns['solve_cache'].clear();ns['MATRICES']={'blend':BLEND,'codex':M[0],'repo_hybrid':M[1]}
    if ban is not None:ns['universe']=olduniverse-{ids[ban]}
    # Keeping flags for the bridge: temporarily restrict same-position candidates by wrapping solver source.
    if keep:
        source=ast.get_source_segment((O/'modell.py').read_text(),next(n for n in ast.parse((O/'modell.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='optimize'))
        source=source.replace("    obj=[]", "    for keep_id in KEEP_IDS:prob+=x[keep_id]==1\n    obj=[]")
        ns['KEEP_IDS']=[ids[i] for i in keep];exec(compile(source,'<keep flagged>','exec'),ns)
    s=ns['optimize'](g,[h for h in range(g,end+1) if h!=FH],ns['orig'],ns['osell'],16,bb=bb,nmoves=nmoves)
    if keep:
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='optimize');exec(compile(ast.Module(body=[node],type_ignores=[]),'<restore optimize>','exec'),ns)
    ns['universe']=olduniverse;ns['MATRICES']=oldmat
    return ordered(ix[p] for p in s)

def renew(g,s,sv,cash,pred,pp,avail,fh=False,ban=None,bb=19,keep=None):
    cols=list(range(g-9,11)) if not fh else [g-9];cols=[t for t in cols if fh or t!=FH-9];ps=pools(pred,cols,avail);liquid=int(cash+sv[s].sum());seeds=[]
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
    ss=np.unique(np.array(seeds),axis=0);ap=approx(ss,pred,pp,cols,bb-9);ss=ss[np.argsort(-ap)[:4]]
    vv=obj_batch(ss,pred,pp,np.array(cols),bb-9,POS,LUT,PERMS);best=ss[vv.argmax()].copy();value=vv.max()
    for _ in range(3):
        nn=neighbors(best,ps,sv,liquid)
        if ban is not None:nn=nn[~np.any(nn==ban,axis=1)]
        if keep is not None:nn=nn[np.any(nn==keep,axis=1)]
        if not len(nn):break
        ap=approx(nn,pred,pp,cols,bb-9);nn=nn[np.argsort(-ap)[:3]]
        vv=obj_batch(nn,pred,pp,np.array(cols),bb-9,POS,LUT,PERMS);j=vv.argmax()
        if vv[j]<=value+1e-7:break
        best=nn[j].copy();value=vv[j]
    legal(best);assert all(avail[i] or i in s for i in best)
    if ban is not None:assert ban not in best
    return ordered(best)

def rolling(g,s,sv,cash,ft,pred,pp,avail,wc,bb=19):
    end=min(19,g+3,wc-1 if wc>g else 19);cols=[h-9 for h in range(g,end+1) if h!=FH];n=hits=0
    if not cols:return s,sv,cash,n,hits
    for _ in range(min(5,ft+1)):
        ps=pools(pred,cols,avail);liquid=int(cash+sv[s].sum());nn=neighbors(s,ps,sv,liquid)
        if not len(nn):break
        ap=approx(nn,pred,pp,cols,bb-9);first=np.argsort(-ap)[:3]
        # Two-swap financing candidates, same proposal rule in every WC timing.
        if n<ft:
            extra=[]
            for j in first:
                for q in neighbors(nn[j],ps,sv,liquid):
                    if len(set(q)-set(s))==2:extra.append(q)
            if extra:nn=np.concatenate([nn,np.array(extra)])
        nn=np.unique(nn,axis=0);ap=approx(nn,pred,pp,cols,bb-9);counts=np.array([len(set(q)-set(s)) for q in nn]);valid=counts<=ft-n+1;nn=nn[valid];ap=ap[valid];counts=counts[valid]
        costhit=4*np.maximum(0,counts-(ft-n));rank=np.argsort(-(ap-costhit));short=nn[rank[:3]];counts=counts[rank[:3]]
        base=obj_batch(s[None,:],pred,pp,np.array(cols),bb-9,POS,LUT,PERMS)[0]
        vv=obj_batch(short,pred,pp,np.array(cols),bb-9,POS,LUT,PERMS);scores=vv-4*np.maximum(0,counts-(ft-n));j=scores.argmax();cnt=int(counts[j]);gain=vv[j]-base
        paid=max(0,cnt-(ft-n));free=cnt-paid;threshold=(0 if ft-n==5 or g==19 else free)+5*paid
        if gain<=threshold+1e-7:break
        s,sv,cash=transact(s,short[j],sv,cash);n+=cnt;hits+=4*paid
        if paid:break
    return s,sv,cash,n,hits

def bridge_choice(g,s,sv,cash,ft,pred,pp,avail,wc,bb):
    # Explicit two-deadline lookahead prevents a known financing option being lost
    # by greedy R9 ranking. Uses only current predicted availability, never future shocks.
    rolled=rolling(g,s,sv,cash,ft,pred,pp,avail,wc,bb)
    candidates=[s,rolled[0]]+BRIDGE
    evaluated=[]
    for q in candidates:
        n=len(set(q)-set(s))
        if n>ft or not all(avail[i] for i in set(q)-set(s)):continue
        if cash+sum(sv[i] for i in set(s)-set(q))-sum(COST[i] for i in set(q)-set(s))<0:continue
        new,nsv,ncash=transact(s,q,sv,cash)
        val=select(new,pred[:,0],pp[:,0],POS,LUT,PERMS,False,False)[0]
        if wc==11:
            # A predicted return before R10 is known from today's absence end date.
            future_av=pp[:,1]>0
            ns_,_,_,_,hit=rolling(10,new,nsv,ncash,min(5,ft-n+1),pred,pp,future_av,wc,bb)
            val+=select(ns_,pred[:,1],pp[:,1],POS,LUT,PERMS,False,False)[0]-hit
        evaluated.append((val,new,nsv,ncash,n))
    base=next(v for v in evaluated if v[4]==0)[0]
    valid=[v for v in evaluated if v[4]==0 or v[0]>base+v[4]]
    best=max(valid,key=lambda v:v[0]);return best[1],best[2],best[3],best[4],0

# Worlds contain ONLY absence end dates already announced by the current deadline.
# All future innovations are hidden from every planner. Duration is known at onset.
def path(wc,world=None,initial=None,ban=None,bb=19,arrays=None,full=False,record=True,keep=None):
    mats=M if arrays is None else arrays;blend=mats.mean(axis=0);s=ORIG.copy();sv=SALES.copy();cash=16;ft=2;rr=[];tot=np.zeros(2);allhits=0
    if world is None:world=np.zeros((11,N),dtype=np.int16)
    for t in range(11):
        g=t+9;release=world[t];av=release<=t;known=(np.arange(11)[None,:]>=release[:,None])|av[:,None];pred=blend*known;pp=PP*known
        before=s.copy();ftbefore=ft;n=hit=0;chip='';active=s
        if g==wc:
            new=renew(g,s,sv,cash,pred,pp,av,ban=ban if g==9 else None,bb=bb,keep=keep if g==9 else None);s,sv,cash=transact(s,new,sv,cash);active=s;chip='WC'
        elif g==FH:active=renew(g,s,sv,cash,pred,pp,av,fh=True,bb=bb);chip='FH'
        elif g==9 and initial is not None:
            new=initial;assert all(av[i] for i in set(new)-set(s));n=len(set(new)-set(s));s,sv,cash=transact(s,new,sv,cash);active=s;hit=4*max(0,n-ft)
        else:
            if g==9 and wc in [10,11]:s,sv,cash,n,hit=bridge_choice(g,s,sv,cash,ft,pred,pp,av,wc,bb)
            else:s,sv,cash,n,hit=rolling(g,s,sv,cash,ft,pred,pp,av,wc,bb)
            active=s
        if g==bb:chip='BB'
        z=select(active,pred[:,t],pp[:,t],POS,LUT,PERMS,full,chip=='BB');weights=z[1];points=(mats[:,active,t]*known[active,t][None,:]*weights[None,:]).sum(axis=1)-hit;tot+=points;allhits+=hit
        if chip not in ['WC','FH']:ft=min(5,max(0,ft-n)+1)
        if record:rr.append(dict(gw=g,chip=chip,tropp=[ids[i] for i in active],permanent=[ids[i] for i in s],elleve=[ids[active[j]] for j in z[2]],benk=[ids[active[j]] for j in z[3]],kaptein=ids[active[z[4]]],visekaptein=ids[active[z[5]]],vekter=weights.tolist(),poeng=points.tolist(),inn=[ids[i] for i in sorted(set(active)-set(before))],ut=[ids[i] for i in sorted(set(before)-set(active))],bank=cash/10,FT_for=ftbefore,FT_etter=ft,trekk=hit))
        legal(s);assert cash>=0 and 1<=ft<=5
    return dict(WC=wc,BB=bb,FH=FH,total=tot.tolist(),trekk=allhits,rows=rr)

def fixed_path(original,arrays=None,auto=True):
    mats=M if arrays is None else arrays;blend=mats.mean(axis=0);rr=[]
    for r in original['rows']:
        g=r['gw'];t=g-9;s=ordered(ix[p] for p in r['tropp']);chip=r['chip'];z=select(s,blend[:,t],PP[:,t],POS,LUT,PERMS,True,chip=='BB')
        if auto:w=z[1]
        else:
            v,xi,cap=ns['lineup'](frozenset(ids[i] for i in s),g,'blend');w=np.zeros(15)
            for j,i in enumerate(s):w[j]=int(ids[i] in xi or chip=='BB')+int(ids[i]==cap)
        pts=(mats[:,s,t]*w[None,:]).sum(axis=1)-r['trekk'];rr.append(dict(r,poeng=pts.tolist(),vekter=w.tolist(),tropp=[ids[i] for i in s],elleve=[ids[s[j]] for j in z[2]],benk=[ids[s[j]] for j in z[3]],kaptein=ids[s[z[4]]],visekaptein=ids[s[z[5]]]))
    return dict(original,total=np.sum([r['poeng'] for r in rr],axis=0).tolist(),rows=rr)

def promoted_stress():
    delta=np.zeros_like(XP)
    for i,p in enumerate(ids):
        e=E[p];po=ns['kinds'][e['element_type']]
        if T[e['team']] not in ['HUL','LEE','COV']:continue
        for f in fx:
            g=f['event']
            if g not in GWS or e['team'] not in [f['team_h'],f['team_a']]:continue
            home=e['team']==f['team_h'];op=f['team_a'] if home else f['team_h'];lam=ns['mean']*ns['strength'][op][0]*ns['strength'][e['team']][1]*(.9 if home else 1.1)
            r=md[p,g];mi=float(r['forventede_min']);ps=float(r['p_start']);p60=min(ps*roles[p][4],mi/60)
            oldgc=sum(z//2*math.exp(-lam)*lam**z/math.factorial(z) for z in range(25));newlam=lam*1.2;newgc=sum(z//2*math.exp(-newlam)*newlam**z/math.factorial(z) for z in range(25))
            delta[i,g-9]+=sc['clean_sheets'][po]*(math.exp(-newlam)-math.exp(-lam))*p60+sc['goals_conceded'][po]*(newgc-oldgc)*mi/90
    # Repo lacks separable CS/GC fields: apply the SAME structural absolute component delta.
    # Do not change attack, saves, bonus, or assumed appearances in this requested stress.
    return np.maximum(0,M+delta[None,:,:]),delta

if __name__=='__main__' and '--bench' in __import__('sys').argv:
    t=time.time()
    for full in [False,True]:
        for _ in range(5):z=select(ORIG,BLEND[:,0],PP[:,0],POS,LUT,PERMS,full,False)
        print('select',full,'time',time.time()-t,'val',z[0],flush=True)
    t=time.time();p=path(9);print('path9 sec',time.time()-t,p['total'],flush=True)
    t=time.time();p=path(11);print('path11 sec',time.time()-t,p['total'],flush=True)

def given(s,xi_ids,bench_ids,cap_id,vice_id,t,arrays=None):
    mats=M if arrays is None else arrays;loc={ids[i]:j for j,i in enumerate(s)};xi=np.array([loc[p] for p in xi_ids]);bn=np.array([loc[p] for p in bench_ids[1:]]);gkb=loc[bench_ids[0]]
    w=np.zeros(15);w[xi]=1.;bw=benchweights(s,xi,bn,PP[:,t],POS,LUT)
    for j in range(3):w[bn[j]]=bw[j]
    w[gkb]=1-PP[s[1-gkb],t];w[loc[cap_id]]+=1.;w[loc[vice_id]]+=1-PP[ix[cap_id],t]
    return (mats[:,s,t]*w[None,:]).sum(axis=1)

def main():
    global BRIDGE
    start=time.time();protected={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in O.iterdir() if p.is_file() and '_r2' not in p.name and p.name!='kontroll.md'}
    print('R2 starts; forecast rows',N*8,flush=True)
    # Structural rule tests additionally compare exact expected score with independent appearance draws.
    z=select(ORIG,BLEND[:,0],PP[:,0],POS,LUT,PERMS,True,False)
    rng=np.random.default_rng(7089878);ncheck=100000;plays=rng.random((ncheck,15))<PP[ORIG,0];xi=z[2];bn=z[3][1:];gkb=z[3][0];gk=1-gkb
    form=[sum(POS[ORIG[j]]==k for j in xi) for k in [2,3,4]];fi=form[0]*24+form[1]*4+form[2];bi=(POS[ORIG[bn[0]]]-2)*9+(POS[ORIG[bn[1]]]-2)*3+POS[ORIG[bn[2]]]-2
    misses=np.stack([(~plays[:,[j for j in xi if POS[ORIG[j]]==k]]).sum(axis=1) for k in [2,3,4]],axis=1);mi=misses[:,0]*24+misses[:,1]*4+misses[:,2];av=plays[:,bn[0]].astype(int)+2*plays[:,bn[1]]+4*plays[:,bn[2]];masks=LUT[fi,bi,mi,av]
    conditional=np.divide(BLEND[ORIG,0],PP[ORIG,0],out=np.zeros(15),where=PP[ORIG,0]>0);draw=(plays[:,xi]*conditional[xi]).sum(axis=1)
    draw+=(~plays[:,gk])*plays[:,gkb]*conditional[gkb]
    for j in range(3):draw+=((masks&(1<<j))>0)*conditional[bn[j]]
    draw+=plays[:,z[4]]*conditional[z[4]]+(~plays[:,z[4]])*plays[:,z[5]]*conditional[z[5]]
    se=float(draw.std()/np.sqrt(ncheck));assert abs(draw.mean()-z[0])<5*se
    jsave('autokontroll_r2.json',dict(eksakt=z[0],montecarlo=float(draw.mean()),SE=se,trekk=ncheck))
    # Symmetric seed set across WC dates and Gross tests, including new two-transfer options.
    gross=named('Groß');seedlog=[];bridge=[];keepflags=[]
    for gw in [9,10,11]:
        q=integer_seed(gw);TEMPLATES.append(q);seedlog.append(dict(test='WC'+str(gw),tropp=name(q)))
    for bb in [19,99]:
        for restriction in ['ban','keep']:
            q=integer_seed(9,bb=bb,ban=gross if restriction=='ban' else None,keep=[gross] if restriction=='keep' else None);TEMPLATES.append(q);seedlog.append(dict(test='Gross_'+restriction+'_BB'+str(bb),tropp=name(q)))
    for end in [9,10,12]:
        bridge.append(integer_seed(9,nmoves=2,end=end))
    keepflags.append(integer_seed(9,nmoves=2,end=10,keep=[named('Calafiori'),named('N.Williams')]))
    bridge.extend(keepflags);bridge.append(ordered(ix[p] for p in next(p for p in ns['read'](O/'planer.json') if p['label']=='C')['rows'][0]['tropp']))
    BRIDGE=bridge+[integer_seed(9,nmoves=1,end=10)]
    candidates=[path(11,initial=q,full=True) for q in bridge];bestc=max(candidates,key=lambda p:np.mean(p['total']));cinit=ordered(ix[p] for p in bestc['rows'][0]['tropp'])
    plans={'A':path(11,initial=ORIG,full=True),'C':bestc,'C_behold_flagg':path(11,initial=keepflags[0],full=True),'E':path(9,full=True),'F_WC10':path(10,full=True),'F_WC11':path(11,full=True),'F_WC10_samme_C':path(10,initial=cinit,full=True),'F_WC11_samme_C':bestc}
    print('Nominal', {k:[round(v,2) for v in p['total']] for k,p in plans.items()},flush=True)
    # Recompute the exact R1 ownership paths to isolate autosub effect from reoptimization.
    audit=[]
    for old in ns['read'](O/'planer.json'):
        if old['label'] not in ['A','C','E','F_WC10','F_WC11']:continue
        no=fixed_path(old,auto=False);yes=fixed_path(old)
        for m,label in enumerate(['codex','repo_hybrid']):audit.append(dict(alternativ=old['label'],poengsett=label,R9_uten_auto=no['rows'][0]['poeng'][m],R9_med_auto=yes['rows'][0]['poeng'][m],R9_autogevinst=yes['rows'][0]['poeng'][m]-no['rows'][0]['poeng'][m],R9_R19_uten_auto=no['total'][m],R9_R19_med_auto=yes['total'][m]))
    save('autobytter_r2.csv',audit)
    claude_xi=[ns['named'](n) for n in ['Verbruggen','Konsa','Calafiori','N.Williams','B.Fernandes','Mbeumo','Tavernier','E.Le Fée','Groß','Haaland','Thiago']]
    claude_bn=[ns['named'](n) for n in ['Steele','van Ewijk','Maguire','Kusi-Asare']]
    claude_points=given(ORIG,claude_xi,claude_bn,ns['named']('Haaland'),ns['named']('Tavernier'),0)
    appearance=[];oldpp=PP[named('Calafiori'),0]
    for ppval in [.5,oldpp]:
        PP[named('Calafiori'),0]=ppval
        for lab in ['A','C','C_behold_flagg','E']:
            r=plans[lab]['rows'][0];s=ordered(ix[p] for p in r['tropp']);z=select(s,BLEND[:,0],PP[:,0],POS,LUT,PERMS,True,False);pts=(M[:,s,0]*z[1][None,:]).sum(axis=1)
            appearance.append(dict(alternativ=lab,Calafiori_p_play=ppval,codex=pts[0],repo_hybrid=pts[1],elleve=name(s[z[2]]),benk=name(s[z[3]])))
    PP[named('Calafiori'),0]=oldpp;save('innhopp_sensitivitet_r2.csv',appearance)
    # Gross forced sold vs retained at WC9, with and without BB19. Later transfers remain legal/free.
    grossplans={};grossrows=[]
    for bb in [19,99]:
        for keep in [True,False]:
            p=path(9,keep=gross if keep else None,ban=None if keep else gross,bb=bb,full=True);lab=('behold' if keep else 'selg')+('_BB19' if bb==19 else '_uten_BB');grossplans[lab]=p
            grossrows.append(dict(test=lab,bank_R9=p['rows'][0]['bank'],tropp_R9=name([ix[z] for z in p['rows'][0]['tropp']]),Gross_i_BB19=ids[gross] in p['rows'][-1]['tropp'],codex=p['total'][0],repo_hybrid=p['total'][1]))
    save('gross_r2.csv',grossrows);jsave('grossplaner_r2.json',grossplans)
    stress,delta=promoted_stress();stressrows=[]
    for lab in ['E','F_WC10','F_WC11','C','A']:
        p=plans[lab];q=fixed_path(p,arrays=stress);stressrows.append(dict(alternativ=lab,codex_for=p['total'][0],codex_etter=q['total'][0],repo_for=p['total'][1],repo_etter=q['total'][1],codex_tap=q['total'][0]-p['total'][0],repo_tap=q['total'][1]-p['total'][1]))
    save('opprykk_r2.csv',stressrows)
    # MC baseline uses exactly the same optimizer and information policy as stochastic paths.
    baseline={};benchmark=[]
    for lab,wc in [('E',9),('F_WC10',10),('F_WC11',11),('A',11)]:
        p=path(wc,initial=ORIG if lab=='A' else None);baseline[lab]=p
        for m,model in enumerate(['codex','repo_hybrid']):benchmark.append(dict(alternativ=lab,poengsett=model,full=plans[lab]['total'][m],lett=p['total'][m],forskjell=p['total'][m]-plans[lab]['total'][m]))
    save('simkontroll_r2.csv',benchmark)
    out=[]
    for label,p in plans.items():
        r=p['rows'][0];z=dict(alternativ=label,WC=p['WC'],BB=19,FH=16,ut=name([ix[i] for i in r['ut']]),inn=name([ix[i] for i in r['inn']]),bank_R9=r['bank'],FT_R10=r['FT_etter'],trekk=sum(z['trekk'] for z in p['rows']))
        for m,model in enumerate(['codex','repo_hybrid']):
            for suffix,nn in [('R9',1),('R9_R12',4),('R9_R16',8),('R9_R19',11)]:z[model+'_'+suffix]=round(sum(row['poeng'][m] for row in p['rows'][:nn]),2)
        out.append(z)
    out.sort(key=lambda r:-(r['codex_R9_R19']+r['repo_hybrid_R9_R19']));save('alternativer_r2.csv',out);jsave('planer_r2.json',plans);save('starttropper_r2.csv',seedlog)
    print('Deterministic complete at',round(time.time()-start,1),'seconds',flush=True)
    # Potential new absence for EVERY player including candidates; fresh draw forbidden during absence.
    DRAWS=200;SEED=7089878;rng=np.random.default_rng(SEED);U=rng.random((DRAWS,11,N));dur=np.array([1,2,3,6],dtype=np.int16)[rng.integers(0,4,size=(DRAWS,11,N))]
    sim=[];trials=[]
    for probability in [.01,.02,.03]:
        results={lab:[] for lab in baseline};hitlog={lab:[] for lab in baseline}
        for draw in range(DRAWS):
            world=np.zeros((11,N),dtype=np.int16);end=np.zeros(N,dtype=np.int16)
            for t in range(11):
                new=(end<=t)&(U[draw,t]<probability);end[new]=t+dur[draw,t,new];world[t]=end
            for lab,wc in [('E',9),('F_WC10',10),('F_WC11',11),('A',11)]:
                p=path(wc,world=world,initial=ORIG if lab=='A' else None,record=False);results[lab].append(p['total']);hitlog[lab].append(p['trekk'])
            if (draw+1)%20==0:print('MC',probability,draw+1,'/',DRAWS,'elapsed',round(time.time()-start),flush=True)
        for m,model in enumerate(['codex','repo_hybrid']):
            ee=np.array(results['E'])[:,m]
            for late in ['F_WC10','F_WC11','A']:
                zz=np.array(results[late])[:,m];diff=ee-zz;base=baseline['E']['total'][m]-baseline[late]['total'][m]
                row=dict(p=probability,trekk=DRAWS,poengsett=model,mot=late,E_snitt=float(ee.mean()),F_snitt=float(zz.mean()),E_minus_F=float(diff.mean()),E_vinner=float((diff>0).mean()),p10=float(np.quantile(diff,.1)),p90=float(np.quantile(diff,.9)),paret_SE=float(diff.std(ddof=1)/np.sqrt(DRAWS)),p0_delta=base,endring_fra_p0=float(diff.mean()-base),E_trekk=float(np.mean(hitlog['E'])),F_trekk=float(np.mean(hitlog[late])))
                sim.append(row)
                for j in range(DRAWS):trials.append(dict(p=probability,poengsett=model,mot=late,trekk=j,E=ee[j],F=zz[j],delta=diff[j]))
        save('skadesim_r2.csv',sim);save('skadetrekk_r2.csv',trials)
        print('MC RESULT',probability,[(r['poengsett'],r['mot'],round(r['E_minus_F'],2)) for r in sim if r['p']==probability],flush=True)
    # Recommendation maximizes average expected score under the central paired injury model.
    central=[r for r in sim if r['p']==.02];ev={'E':np.mean([r['E_snitt'] for r in central])}
    for lab in ['F_WC10','F_WC11','A']:ev[lab]=np.mean([r['F_snitt'] for r in central if r['mot']==lab])
    choice=max(ev,key=ev.get);selected=plans[choice]
    # Hold R9 / C remain compared deterministically; do not invent an FT or information bonus.
    report(plans,out,audit,sim,benchmark,grossrows,stressrows,appearance,claude_points,choice,protected,start)

def report(plans,out,audit,sim,benchmark,grossrows,stressrows,appearance,claude_points,choice,protected,start):
    selected=plans[choice];r=selected['rows'][0];tab={z['alternativ']:z for z in out};models=['codex','repo_hybrid']
    def names(pids):return name([ix[p] for p in pids])
    lines=['# Kontroll R9, runde 2','',f"**Anbefaling: {choice}; WC i R{selected['WC']}.**",f"R9 ut: {names(r['ut']) or 'ingen'}. Inn: {names(r['inn']) or 'ingen'}. Bank £{r['bank']:.1f}m; trekk {r['trekk']}. BB19/FH16 i alle hovedbaner.",'',
        '**Ellever:** '+names(r['elleve'])+'.','**Kaptein:** '+names([r['kaptein']])+'. **Visekaptein:** '+names([r['visekaptein']])+'.','**Benk:** '+names(r['benk'])+' (keeper først, deretter prioritert rekkefølge).','',
        'Anbefalingen følger høyest beregnet gjennomsnittsforventning ved skaderate 2 % per frisk spiller/runde, med lik vekt på codex og repo_hybrid. Skaderatene er antatte stressnivåer, ikke estimerte faktiske skaderater. Tallene nedenfor viser hvor mye konklusjonen avhenger av modellen. Ingen FPL-handlinger er utført.', '',
        '## 1. Autobytter og revidert rangering','',
        'Poengfilen inneholder spillerens ubetingede xP. Autobytter legges til på lagnivå. Jeg summerer over sannsynlighetene for antall fravær per posisjon og samtlige åtte spilleutfall for utespillerbenken. Første lovlige benkespiller prioriteres; nominel formasjon etter erstatning må fortsatt ha minst 3 forsvarere, 2 midtbanespillere og 1 spiss. Keeper erstattes bare av benkekeeper. Ved 0 minutter for kapteinen overføres ekstrakopien til visekapteinen hvis han spiller. Et kort innhopp blokkerer autobytte.',
        'Dette er eksakt forventningsverdi gitt uavhengige p_play, ikke en simulering av kamppoeng. Uavhengigheten er en antakelse; særlig keeperne fra samme klubb kan være negativt korrelerte. Det oppstår heller ingen automatisk rolleoppgradering av en reserve når en klubbkamerat skades. Fullt elleversøk tester alle lovlige ellevere, benkerekkefølger og kaptein/vice-par. En særskilt test med 100 000 spilleutfall kontrollerer integrasjonen (autokontroll_r2.json).','',
        'Først isoleres autobytter på de samme eierbanene som R1, men med Claudes to nye minuttantakelser. Elleveren velges på nytt i begge beregningene:','',
        '| Plan fra R1 | Poengsett | R9 uten auto | R9 med auto | Gevinst | R9–19 med auto |','|---|---|---:|---:|---:|---:|']
    for z in audit:lines.append(f"| {z['alternativ']} | {z['poengsett']} | {z['R9_uten_auto']:.1f} | {z['R9_med_auto']:.1f} | {z['R9_autogevinst']:+.1f} | {z['R9_R19_med_auto']:.1f} |")
    lines+=['','Oppdatert planvalg med autobytter i byttepolitikken (tall codex/repo):','', '| Plan | WC | R9-handling | Bank | R9 | R9–12 | R9–16 | R9–19 |','|---|---:|---|---:|---:|---:|---:|---:|']
    for z in out:lines.append(f"| {z['alternativ']} | {z['WC']} | {z['ut'] or 'ingen'} → {z['inn'] or 'ingen'} | {z['bank_R9']:.1f} | {z['codex_R9']:.1f}/{z['repo_hybrid_R9']:.1f} | {z['codex_R9_R12']:.1f}/{z['repo_hybrid_R9_R12']:.1f} | {z['codex_R9_R16']:.1f}/{z['repo_hybrid_R9_R16']:.1f} | {z['codex_R9_R19']:.1f}/{z['repo_hybrid_R9_R19']:.1f} |")
    lines+=['', 'A ruller R9, deretter samme løpende byttepolitikk og WC11. C er beste testede kandidat med nøyaktig to R9-bytter og WC11. F_WC10/F_WC11 bruker samme adaptive byttepolitikk som WC9, fra første runde uten WC. Derfor kan R9-handlingen variere når vinduet før WC er ulikt. Radene med «samme_C» isolerer i tillegg WC-datoen med identisk konkret R9-handling. Samme BB19/FH16 og samme policy gjelder gjennomgående.', '',
        '**De flaggede og Claudes ellever:** R1-C solgte Calafiori; begge kan derfor ikke startes i akkurat den troppen. C_behold_flagg er en ekstra tobyttevariant der begge beholdes. Alle lovlige startkombinasjoner er undersøkt i det fulle elleversøket.',f"Claudes foreslåtte A-ellever, med Haaland/Tavernier som C/VC og van Ewijk før Maguire på benken, gir {claude_points[0]:.1f}/{claude_points[1]:.1f} i R9. Beste A-ellever gir {tab['A']['codex_R9']:.1f}/{tab['A']['repo_hybrid_R9']:.1f}.", '', '| Plan | Valgt R9-ellever | Benk |','|---|---|---|']
    for lab in ['A','C','C_behold_flagg']:
        z=plans[lab]['rows'][0];lines.append(f"| {lab} | {names(z['elleve'])} | {names(z['benk'])} |")
    lines+=['','## 2. Parede skadesimuleringer: verdien av å vente','',
        '200 felles verdener per skaderate (1 %, 2 %, 3 %), seed 7089878. Nye fravær kan starte i alle runder R9–R19 for alle 669 spillere, også ikke-eide kjøpskandidater. Varighet 1/2/3/6 runder trekkes med lik sannsynlighet. Ingen ny skade mens spilleren allerede er ute. R9-fravær er kjent før den aktuelle R9-handlingen. Alle baner og begge poengsett møter samme spillerfravær.',
        'Ved hver frist kjenner beslutningstakeren bare fravær som allerede har oppstått, og antatt sluttdato for disse. Fremtidige nye fravær er skjult. WC11 får dermed bruke skader som har oppstått før R11; WC9 får gjøre reparasjoner med opptjente FT. Ingen kjent skadet spiller kjøpes, mens en allerede eid skadet spiller kan beholdes dersom prognosen etter retur forsvarer det. WC-datoene er faste; det er ingen automatisk fremskynding.',
        'Samme neste-fire-runder-politikk i alle baner, avkortet før WC og uten FH-runden. For R9-broen til WC10/WC11 vurderes også de heltallsoptimerte R9-kandidatene; WC11-broen tar med neste frists mulige gratisbytter, beregnet bare med allerede kjent fravær. Dette hindrer at en kjent finansieringsmulighet faller ut av det grådige søket. Gratisbytter krever >1 poeng per brukt FT (null ved fem FT eller R19); ett ekstra betalt bytte krever >5 brutto, altså >1 netto. Enkeltbytter og et avgrenset søk etter tobytte-finansiering vurderes. Maks fem lagrede FT. WC/FH bevarer FT uten opptjening, som R1; denne sesongregelen er fortsatt en antakelse i grunnlaget. A er eksplisitt tvunget til å rulle R9, også når et nytt R9-fravær oppstår.', '',
        '| p | Mot | Sett | E snitt | Sen/hold snitt | E minus | E vinner | Δ p10–p90 | MC-SE | Endring fra p=0 |','|---|---|---|---:|---:|---:|---:|---|---:|---:|']
    for z in sim:lines.append(f"| {z['p']:.0%} | {z['mot']} | {z['poengsett']} | {z['E_snitt']:.1f} | {z['F_snitt']:.1f} | {z['E_minus_F']:+.1f} | {z['E_vinner']:.1%} | {z['p10']:+.1f} til {z['p90']:+.1f} | {z['paret_SE']:.2f} | {z['endring_fra_p0']:+.1f} |")
    lines+=['','«E vinner» gjelder forventede poeng gitt de trukne skadeforløpene, ikke sannsynligheten for at laget faktisk får flest kamppoeng. p10–p90 er for den parede forskjellen. MC-SE gjelder bare numerisk simuleringsstøy. Spilletids-/bonusfeil, tilfeldige mål og felles lagsjokk er ikke inkludert. Skaderaten økes ikke særskilt i landslagspausen, og nye rolleendringer, friskmeldinger av dagens blokkerte kandidater og endret kampprogram modelleres ikke.',
        'For kjøretid brukes samme begrensede søk i begge baner: ni beste + fire billigste kjøpskandidater per posisjon, symmetriske WC/FH-starttropper, opptil tre lokale forbedringer. Aktuelle bytteforslag velges fra en rask poengtilnærming; de tre beste vurderes med eksakt autobytteforventning. MC-ellever velges fra fire rangeringer og alle formasjoner; alle benkerekkefølger i dette utvalget vurderes eksakt. Ingen global optimalitetsgaranti. Hovedtabellen bruker full elleveroptimering. Forskjellen mot den identiske lette MC-politikken ved p=0 er kontrollert:','',
        '| Plan | Sett | Full ellever | MC-policy p=0 | Forskjell |','|---|---|---:|---:|---:|']
    for z in benchmark:lines.append(f"| {z['alternativ']} | {z['poengsett']} | {z['full']:.1f} | {z['lett']:.1f} | {z['forskjell']:+.2f} |")
    lines+=['','## 3. Groß: bundet benkebudsjett og BB19','',
        'Begge WC9-troppene har samme salgsverdi + bank £99,4m. «Behold» pålegger at Groß inngår ved WC9; «selg» utelukker ham ved WC9. Senere bytter er frie under samme policy, og eventuell tilbakekjøping er synlig i grossplaner_r2.json. Testen gjentas helt uten BB for å undersøke forklaringen. FH16 beholdes.', '',
        '| WC9-krav | BB | R9-bank | Groß i R19-tropp | Codex R9–19 | Repo R9–19 |','|---|---|---:|---|---:|---:|']
    for z in grossrows:lines.append(f"| {z['test'].split('_')[0]} | {'19' if z['test'].endswith('BB19') else 'ingen'} | {z['bank_R9']:.1f} | {'ja' if z['Gross_i_BB19'] else 'nei'} | {z['codex']:.1f} | {z['repo_hybrid']:.1f} |")
    gr={z['test']:z for z in grossrows}
    for suffix in ['BB19','uten_BB']:
        a,b_=gr['selg_'+suffix],gr['behold_'+suffix];lines.append(f"Selg minus behold ({suffix}): {a['codex']-b_['codex']:+.1f}/{a['repo_hybrid']-b_['repo_hybrid']:+.1f} poeng.")
    effect=[(gr['behold_BB19'][m]-gr['selg_BB19'][m])-(gr['behold_uten_BB'][m]-gr['selg_uten_BB'][m]) for m in models]
    lines+=['',f"BB endrer den relative fordelen ved å beholde Groß med {effect[0]:+.1f}/{effect[1]:+.1f} poeng. Dette måles med reoptimerte starttropper og fremtidige bytter, ikke ved å tilskrive all benkeverdi i R19 til Groß. Forskjellen er betinget av det avgrensede søket. Groß har også vanlig benke-/rotasjonsverdi gjennom autobytter; at han står på R9-benken betyr ikke at pengene bare arbeider på BB-dagen.", '',
        '## 4. Opprykksforsvar: 20 % flere forventede innslupne','',
        'For HUL, LEE og COV settes λ for innslupne mål til 1,2 × λ i hver kamp R9–R19. Dermed endres både P(nullen)=exp(−λ) og forventet straff for hvert annet innslupne mål. Dette er ikke et flatt 20 %-kutt i nullsannsynligheten. Angrep, minutter, redninger, bonus og DC holdes uendret. Repo-filen mangler rene CS/GC-komponenter; samme absolutte Codex-komponentendring legges derfor på repo_hybrid. Dette er en eksplisitt hybridtilnærming.',
        'Faste kjøpsbaner; ellever, kaptein og benkerekkefølge velges på nytt under stresstallene. Testen isolerer prognosefeilen og inkluderer ikke nye kjøp som svar på en ny erkjennelse av lagstyrke.', '',
        '| Plan | Codex før → etter | Repo før → etter | Tap codex/repo |','|---|---:|---:|---:|']
    for z in stressrows:lines.append(f"| {z['alternativ']} | {z['codex_for']:.1f} → {z['codex_etter']:.1f} | {z['repo_for']:.1f} → {z['repo_etter']:.1f} | {z['codex_tap']:.1f}/{z['repo_tap']:.1f} |")
    st={z['alternativ']:z for z in stressrows};lines+=['',f"Etter stresstesten: E minus F_WC11 = {st['E']['codex_etter']-st['F_WC11']['codex_etter']:+.1f}/{st['E']['repo_etter']-st['F_WC11']['repo_etter']:+.1f} poeng. E minus C = {st['E']['codex_etter']-st['C']['codex_etter']:+.1f}/{st['E']['repo_etter']-st['C']['repo_etter']:+.1f}.", '',
        '## 5. Claudes spilletid og innhoppsusikkerheten','',
        'B.Fernandes settes til p_start 0,75 og Calafiori til 0,50 i R9. Deres forventede minutter skaleres tilsvarende fra R1, slik at minuttforventningen følger den nye startsannsynligheten. Alle øvrige spiller-/rundeminutter er identiske med R1. Full fil: minutter_antatt_r2.csv. Ingen av Claudes øvrige minuttforslag er sneket inn.',
        f"Fernandes p_play R9 = {PP[named('B.Fernandes'),0]:.2f}; Calafiori p_play = {PP[named('Calafiori'),0]:.2f}. For Calafiori kommer forskjellen fra innhoppsandelen blant observerte kamper uten start og API-tilgjengelighet 75 %. Utvalget er lite, og dette er en modellantakelse – ikke et nytt medisinsk faktum. Jeg viser derfor også p_play=0,50 ved samme ubetingede xP. Det isolerer mer benkedekning fremfor å endre spillerprognosen samtidig.", '',
        '| Plan | Calafiori p_play | Codex R9 | Repo R9 | Calafiori starter |','|---|---:|---:|---|']
    for z in appearance:lines.append(f"| {z['alternativ']} | {z['Calafiori_p_play']:.2f} | {z['codex']:.1f} | {z['repo_hybrid']:.1f} | {'ja' if 'Calafiori' in z['elleve'] else 'nei'} |")
    lines+=['','## 6. Direkte vurdering av Claudes forslag','']
    for other in ['C','E']:
        d9=[tab[other][m+'_R9']-tab['A'][m+'_R9'] for m in models];d19=[tab[other][m+'_R9_R19']-tab['A'][m+'_R9_R19'] for m in models]
        lines.append(f"Å rulle (A) koster mot {other}: {d9[0]:.1f}/{d9[1]:.1f} forventede poeng i R9 og {d19[0]:.1f}/{d19[1]:.1f} gjennom R19 i den nominelle beregningen med autobytter.")
    lines+=['','Claude har rett i at autobytter må med. Det følger derimot ikke at de svekker WC9-fordelen: en WC-tropp med en sterkere spillende benk får også merverdi. Tabellen i punkt 1 måler virkningen for begge sider. En fast «+1,5 til A» uten å beregne E på samme måte er ikke en sammenligning.',
        'Informasjon etter landslagspausen er reell, men er ikke gratis poeng. Sen WC kan velge med nyere skadeinfo; tidlig WC gir en bedre benk og FT som kan reparere. Den parede skadesimuleringen priser akkurat denne delen under identiske fravær og samme byttepolitikk. Den beregnede endringen fra p=0 er riktig mål på skadeinformasjonens nettovirkning i testen. Det er ikke grunnlag for å legge ytterligere «1–2 poeng per spart FT» på A etter at FT allerede er brukt i den simulerte politikken.',
        'Testen avgjør ikke verdien av ukjente trener-/rolleendringer, pressekilders kvalitet eller retur for dagens utelukkede kjøpskandidater etter pausen. Å velge venting på grunn av dette er et skjønn om umodellert informasjon, ikke et resultat fra skadeberegningen. Et bevis for at all informasjonsverdi er null finnes ikke her.', '',
        '## Konkret tropp og budsjett for anbefalingen','', '| Spiller | Lag/status | Behold/kjøp | Budsjettverdi |','|---|---|---|---:|']
    squad=[ix[p] for p in r['tropp']]
    for i in squad:lines.append(f"| {E[ids[i]]['web_name']} | {T[E[ids[i]]['team']]}/{E[ids[i]]['status']} | {'behold' if i in ORIG else 'kjøp'} | {SALES[i]/10 if i in ORIG else COST[i]/10:.1f} |")
    lines+=['', 'Statuskolonnen viser API-flagg. Thomas (COV, forsvar) er d/75 %, og er en annen spiller enn Thomas-Asante. Hvis Thomas inngår, er den reduserte spilletiden og benkedekningen med i prognosen; han er ingen bekreftet frisk spiller. Eventuelt salg av Fernandes i WC-troppen er en budsjett-/poengprioritering over R9–19, ikke en påstand om at han er ute i R9.']
    outs=[ix[p] for p in r['ut']];ins=[ix[p] for p in r['inn']];sold=sum(SALES[i] for i in outs)/10;bought=sum(COST[i] for i in ins)/10;assert abs(1.6+sold-bought-r['bank'])<1e-7
    lines+=['',f"Budsjett: £1,6m + verifiserte salg £{sold:.1f}m − kjøp £{bought:.1f}m = £{r['bank']:.1f}m. Salgspris brukes for beholdte egne spillere i WC-verdien; markedspris for nye kjøp. Alle steg kontrolleres for 15 spillere, 2/5/5/3, maks tre per klubb, bank ≥0 og tilgjengelige nye kjøp.",'', '**Salg enkeltvis:** '+', '.join(f"{E[ids[i]]['web_name']} £{SALES[i]/10:.1f}m" for i in outs)+'.','',
        '## Kjøring og avgrensning','',
        'Kjør `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH` og `python samarbeid/gw09/codex/modell_r2.py`. Bruker eksisterende numpy, numba og PuLP/CBC. Ingen nettverk/installasjon. R1-koden leses som metodegrunnlag med alle skrivefunksjoner deaktivert; R1s hovedkjøring utføres ikke. R1-filene har uendrede sjekksummer etter kjøringen.',
        'spillerpoeng_r2.csv dekker alle 669 spillere R9–R16 i begge poengsett. Den inneholder spiller-xP uten lagavhengige autobytter; vektene som gjenskaper lagpoengene ligger i planer_r2.json. Repo-hybrid bruker repoets R9–R14 og Codex R15–R19, med samme minuttskalering som R1. Prognoseevalueringen må bruke spillerfilen på spillernivå og ta autobytter fra lagplanen separat.',
        'Hovedbegrensninger: konstante priser, ingen nye blanke/doble runder, uavhengige normale spilleutfall, dagens kjøpsfilter og utestengte/skadde holdt ute til ukjent retur. WC/FH- og transfer-søk er avgrenset; samme starttropper og metode benyttes symmetrisk. Tall med én desimal er for etterprøvbarhet, ikke et løfte om tilsvarende prognosepresisjon.']
    text='\n'.join(lines)+'\n';(O/'kontroll.md').write_text(text)
    for z in out:assert f"{z['codex_R9_R19']:.1f}/{z['repo_hybrid_R9_R19']:.1f}" in text
    for z in sim:assert f"{z['E_minus_F']:+.1f}" in text
    for p,h in protected.items():assert hashlib.sha256((O/p).read_bytes()).hexdigest()==h,p
    assert len(ns['rows'](O/'spillerpoeng_r2.csv'))==N*8
    hashes={p:hashlib.sha256((O/p).read_bytes()).hexdigest() for p in ['modell_r2.py','minutter_antatt_r2.csv','spillerpoeng_r2.csv','alternativer_r2.csv','skadesim_r2.csv','planer_r2.json','kontroll.md']}
    jsave('validering_r2.json',dict(anbefaling=choice,spillere=N,spillerpoengrader=N*8,trekk_per_p=200,p=[.01,.02,.03],BB=19,FH=16,seed=7089878,R1_uendret=True,sekunder=round(time.time()-start,1),sha256=hashes,kontroller='Regeltester, 100000 spillutfall, budsjett/klubbgrenser, prognosedekning og rapport/CSV-konsistens passerte'))
    print('DONE',choice,'seconds',round(time.time()-start,1),flush=True)

if __name__=='__main__' and '--bench' not in __import__('sys').argv:main()
