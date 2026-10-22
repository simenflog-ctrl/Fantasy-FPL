#!/usr/bin/env python3
"""Final offline paired chip/injury tests. Run existing Anaconda Python + numpy.
Only *_r3 files are written. R2 point estimates/roles are frozen inputs.
"""
import ast,csv,json,math,time
from pathlib import Path
from collections import Counter
import numpy as np
O=Path(__file__).resolve().parent; D=O.parent/'data'
def read(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open()))
def save(name,data):
 assert '_r3.' in name
 with (O/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
b=read(D/'bootstrap.json');E={e['id']:e for e in b['elements']};ids=sorted(E);ix={p:i for i,p in enumerate(ids)};N=len(ids);cost={p:e['now_cost'] for p,e in E.items()};sales=read(D/'salgspriser.json');orig=frozenset(r['id'] for r in sales);osell={r['id']:round(10*r['salgspris']) for r in sales};universe=frozenset(int(r['id']) for r in rows(O/'kjopsunivers_r2.csv') if r['godkjent']=='1');COMEBACK=False
TAV=next(p for p,e in E.items() if e['web_name']=='Tavernier');SZ=next(p for p,e in E.items() if e['web_name']=='Szoboszlai')
MATRICES={m:np.zeros((N,12)) for m in ['codex','repo_hybrid']}
for r in rows(O/'spillerpoeng_r2.csv'):
 for m in MATRICES:MATRICES[m][ix[int(r['id'])],int(r['gw'])-8]=float(r[m])
formations=[(d,m,10-d-m) for d in range(3,6) for m in range(2,6) if 1<=10-d-m<=3];evalcache={};optcache={};searchlog=[]
# Compile functions only: NEVER execute R2 top-level code or its writes.
keep={'scores','lineup','saleprice','legal','allowed','pool','optimize','enact','transfers','simulate'}
tree=ast.parse((O/'modell_r2.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in keep];assert len(defs)==len(keep)
exec(compile(ast.Module(body=defs,type_ignores=[]),str(O/'modell_r2.py')+' [functions only]','exec'),globals())
PAIRS=[(15,9),(17,13),(19,13),(19,9)]
chip=[];detpaths=[]
for model in MATRICES:
 for bb,fh in PAIRS:
  print('Chips',model,bb,fh,flush=True);e=simulate(model,8,bb,fh);z=simulate(model,11,bb,fh);detpaths.extend([e,z]);chip.append(dict(poengsett=model,test='samme_datoer',E_BB=bb,E_FH=fh,B_BB=bb,B_FH=fh,E=sum(r['poeng'] for r in e['rows']),B_WC11=sum(r['poeng'] for r in z['rows']),E_minus_B=e['total']-z['total'],E_R8_R15=sum(r['poeng'] for r in e['rows'][:8]),B_R8_R15=sum(r['poeng'] for r in z['rows'][:8])))
 # Best among this common candidate set; includes both R2 models' own selected date pairs.
 ep=max([p for p in detpaths if p['model']==model and p['wc']==8],key=lambda p:p['total']);bp=max([p for p in detpaths if p['model']==model and p['wc']==11],key=lambda p:p['total']);chip.append(dict(poengsett=model,test='eget_beste_av_fire_par',E_BB=ep['bb'],E_FH=ep['fh'],B_BB=bp['bb'],B_FH=bp['fh'],E=ep['total'],B_WC11=bp['total'],E_minus_B=ep['total']-bp['total'],E_R8_R15=sum(r['poeng'] for r in ep['rows'][:8]),B_R8_R15=sum(r['poeng'] for r in bp['rows'][:8])))
# Warm-start both plans symmetrically with every already found nominal squad.
# A local search may otherwise miss a financing combination and exaggerate timing value.
first_paths=list(detpaths);first_chip=list(chip);EXTRA_SEEDS={m:[] for m in MATRICES}
for p in first_paths:
 for r in p['rows']:
  if r['chip'] in ['WC','FH']:
   q=frozenset(r['tropp'])
   if q not in EXTRA_SEEDS[p['model']]:EXTRA_SEEDS[p['model']].append(q)
opt_source=ast.get_source_segment((O/'modell_r2.py').read_text(),next(n for n in defs if n.name=='optimize'))
old_seed="best=max(seeds,key=val);beam=list(set(seeds));seen=set(beam)"
new_seed="for q in EXTRA_SEEDS[model]:\n  if q<=allowed(g) and legal(q) and sum(price[p] for p in q)<=liquid:seeds.append(q)\n best=max(seeds,key=val);beam=list(set(seeds));seen=set(beam)"
assert old_seed in opt_source
exec(compile(opt_source.replace(old_seed,new_seed),'<r3 symmetric warm starts>','exec'),globals());optcache.clear();chip=[];detpaths=[]
for model in MATRICES:
 for bb,fh in PAIRS:
  print('Warm chips',model,bb,fh,flush=True);e=simulate(model,8,bb,fh);z=simulate(model,11,bb,fh);detpaths.extend([e,z]);chip.append(dict(poengsett=model,test='samme_datoer',E_BB=bb,E_FH=fh,B_BB=bb,B_FH=fh,E=sum(r['poeng'] for r in e['rows']),B_WC11=sum(r['poeng'] for r in z['rows']),E_minus_B=e['total']-z['total'],E_R8_R15=sum(r['poeng'] for r in e['rows'][:8]),B_R8_R15=sum(r['poeng'] for r in z['rows'][:8])))
 ep=max([p for p in detpaths if p['model']==model and p['wc']==8],key=lambda p:p['total']);bp=max([p for p in detpaths if p['model']==model and p['wc']==11],key=lambda p:p['total']);chip.append(dict(poengsett=model,test='eget_beste_av_fire_par',E_BB=ep['bb'],E_FH=ep['fh'],B_BB=bp['bb'],B_FH=bp['fh'],E=ep['total'],B_WC11=bp['total'],E_minus_B=ep['total']-bp['total'],E_R8_R15=sum(r['poeng'] for r in ep['rows'][:8]),B_R8_R15=sum(r['poeng'] for r in bp['rows'][:8])))
save('sokekontroll_r3.csv',[dict(poengsett=r['poengsett'],BB=r['E_BB'],FH=r['E_FH'],forste_delta=round(z['E_minus_B'],2),varm_delta=round(r['E_minus_B'],2)) for r,z in zip(chip,first_chip) if r['test']=='samme_datoer'])
save('chipdatoer_r3.csv',[{k:round(v,1) if isinstance(v,float) else v for k,v in r.items()} for r in chip]);(O/'chipplaner_r3.json').write_text(json.dumps(detpaths,ensure_ascii=False,indent=2));print('Deterministic finished',flush=True)
# Fast Monte Carlo uses the same vectorized scoring identity as R2.
POS=np.array([E[p]['element_type'] for p in ids]);TEAM=np.array([E[p]['team'] for p in ids]);COST=np.array([cost[p] for p in ids]);UI=np.array(sorted(ix[p] for p in universe));ORIG=np.array(sorted([ix[p] for p in orig],key=lambda i:(POS[i],i)));SALES=COST.copy()
for p,v in osell.items():SALES[ix[p]]=v
SLICES=[slice(0,2),slice(2,7),slice(7,12),slice(12,15)];COUNTS=[2,5,5,3];MC_BB=17;MC_FH=13;DRAWS=300;SEED=7089878

def ordered(s):return np.array(sorted(set(int(i) for i in s),key=lambda i:(POS[i],i)),dtype=int)
def mclegal(s):
 assert len(s)==15 and len(set(s))==15
 assert [int(sum(POS[s]==k)) for k in range(1,5)]==COUNTS
 assert max(np.bincount(TEAM[s]))<=3

def components(squads,forecast,cols):
 squads=np.atleast_2d(squads);v=forecast[squads][:,:,cols];B=len(squads);W=len(cols);cs=[]
 for sl in SLICES:
  a=np.sort(v[:,sl,:],axis=1)[:,::-1,:];cs.append(np.concatenate([np.zeros((B,1,W)),np.cumsum(a,axis=1)],axis=1))
 cap=v.max(axis=1);best=np.zeros((B,W))
 for d,m,f in formations:best=np.maximum(best,cs[0][:,1]+cs[1][:,d]+cs[2][:,m]+cs[3][:,f]+cap)
 bench=v.sum(axis=1)-(best-cap);return best,bench

def objective(squads,forecast,cols,bb=None,renew=False,fh=False):
 a,bn=components(squads,forecast,cols);val=a.sum(axis=1)
 if bb is not None and bb in cols:val+=bn[:,cols.index(bb)]
 elif renew and not fh:val+=.35*bn.max(axis=1)
 return val

def cpools(pred,cols,available):
 pools=[]
 for k in range(1,5):
  q=UI[(POS[UI]==k)&available[UI]];v=pred[q][:,cols].sum(axis=1);rank=np.lexsort((q,-v));cheap=np.lexsort((q,COST[q]));pools.append(np.array(sorted(set(q[rank[:6]])|set(q[cheap[:3]])),dtype=int))
 return pools

def neighbours(s,pools,prices,liquid):
 result=[];clubs=np.bincount(TEAM[s],minlength=int(TEAM.max())+1);spent=int(prices[s].sum())
 for slot,out in enumerate(s):
  inc=pools[POS[out]-1];inc=inc[~np.isin(inc,s)]
  mask=(spent-prices[out]+prices[inc]<=liquid)&(clubs[TEAM[inc]]-(TEAM[inc]==TEAM[out])<3);inc=inc[mask]
  if len(inc):
   ss=np.repeat(s[None,:],len(inc),axis=0);ss[:,slot]=inc;result.append(ss)
 return np.concatenate(result) if result else np.empty((0,15),dtype=int)

# Templates are not scenario-oracle solutions: all come from injury-free local-data runs.
TEMPLATES={m:[] for m in MATRICES}
for p in first_paths+detpaths:
 for r in p['rows']:
  if r['chip'] in ['WC','FH']:
   s=ordered(ix[z] for z in r['tropp'])
   if not any(np.array_equal(s,z) for z in TEMPLATES[p['model']]):TEMPLATES[p['model']].append(s)
INIT={}

def fast_renew(model,g,s,sv,cash,pred,available,fh=False):
 cols=list(range(g-8,12)) if not fh else [g-8];pools=cpools(pred,cols,available);liquid=int(cash+sv[s].sum());held=set(s);can=set(int(i) for i in UI if available[i])|held.intersection(set(UI));seeds=[]
 def repair(template):
  cur=list(template.copy());clubs=Counter(TEAM[cur]);used=set(cur)
  for slot,out in enumerate(cur):
   if out in can:continue
   clubs[TEAM[out]]-=1;used.remove(out);q=[int(i) for i in UI if available[i] and POS[i]==POS[out] and i not in used and clubs[TEAM[i]]<3]
   if not q:return None
   inc=min(q,key=lambda i:(sv[i],i));cur[slot]=inc;clubs[TEAM[inc]]+=1;used.add(inc)
  a=ordered(cur)
  if sv[a].sum()>liquid:return None
  return a
 for a in [s]+TEMPLATES[model]:
  r=repair(a)
  if r is not None:seeds.append(r)
 cheap=[];clubs=Counter()
 for k,n in enumerate(COUNTS,1):
  for i in sorted([int(i) for i in UI if POS[i]==k and available[i]],key=lambda i:(sv[i],i)):
   if clubs[TEAM[i]]<3:
    cheap.append(i);clubs[TEAM[i]]+=1
    if sum(POS[z]==k for z in cheap)==n:break
 cheap=ordered(cheap);mclegal(cheap)
 if sv[cheap].sum()<=liquid:seeds.append(cheap)
 assert seeds,'No affordable healthy squad'
 ss=np.array(seeds);vv=objective(ss,pred,cols,renew=True,fh=fh);best=ss[int(vv.argmax())].copy();value=float(vv.max())
 # Width one, at most six improving single swaps; templates provide financing starts.
 for _ in range(6):
  ns=neighbours(best,pools,sv,liquid)
  if not len(ns):break
  vv=objective(ns,pred,cols,renew=True,fh=fh);i=int(vv.argmax())
  if vv[i]<=value+1e-8:break
  best=ns[i].copy();value=float(vv[i])
 mclegal(best);assert all(i in can for i in best);return ordered(best)

def execute(s,new,sv,cash):
 old=set(s);ns=set(new);out=old-ns;ins=ns-old;cash=int(cash+sum(sv[i] for i in out)-sum(COST[i] for i in ins));assert cash>=0
 sv=sv.copy()
 for i in out|ins:sv[i]=COST[i]
 mclegal(new);return new,sv,cash

def fast_transfers(g,s,sv,cash,ft,pred,available,next_wc):
 end=min(19,g+3,next_wc-1 if next_wc and next_wc>g else 19);cols=[h-8 for h in range(g,end+1) if h!=MC_FH];pools=cpools(pred,cols,available);n=0;hit=0;bb=MC_BB-8 if MC_BB in range(g,end+1) else None
 for _ in range(min(5,ft+1)):
  base=float(objective(s,pred,cols,bb=bb)[0]);ns=neighbours(s,pools,sv,int(cash+sv[s].sum()))
  if not len(ns):break
  vv=objective(ns,pred,cols,bb=bb);j=int(vv.argmax());gain=float(vv[j]-base);threshold=(0 if ft-n>=5 or g==19 else 1) if n<ft else 5
  if gain<=threshold+1e-9:break
  s,sv,cash=execute(s,ordered(ns[j]),sv,cash);n+=1
  if n>ft:hit+=4;break
 return s,sv,cash,n,hit

def nominal_xi(s,model,t):
 # Only used to count normally starting players absent before transfers.
 pred=MATRICES[model][:,t];by=[sorted([int(i) for i in s if POS[i]==k],key=lambda i:(pred[i],-i),reverse=True) for k in range(1,5)];best=None
 for d,m,f in formations:
  xi=by[0][:1]+by[1][:d]+by[2][:m]+by[3][:f];v=sum(pred[i] for i in xi)+max(pred[i] for i in xi)
  if best is None or v>best[0]:best=(v,xi)
 return best[1]

def mcpath(model,late,world):
 s=ORIG.copy();sv=SALES.copy();cash=10;ft=2;wc_done=False;used_wc=0;total=0.;hits=0
 for t in range(12):
  g=t+8;release=world[t];available=release<=t
  # Information set: only absences already started, return date known at onset.
  pred=MATRICES[model]*((np.arange(12)[None,:]>=release[:,None])|available[:,None]);wc=(not late and g==8) or (late and not wc_done and (g==11 or (g in [9,10] and sum(not available[i] for i in nominal_xi(s,model,t))>=3)))
  n=hit=0;transferchip=False;active=s
  if wc:
   if g==8 and model in INIT:new=INIT[model].copy()
   else:
    new=fast_renew(model,g,s,sv,cash,pred,available)
    if g==8:INIT[model]=new.copy()
   s,sv,cash=execute(s,new,sv,cash);active=s;wc_done=True;used_wc=g;transferchip=True
  elif g==MC_FH:
   active=fast_renew(model,g,s,sv,cash,pred,available,fh=True);transferchip=True
  elif g==8:
   new=ordered((set(s)-{ix[SZ]})|{ix[TAV]});s,sv,cash=execute(s,new,sv,cash);active=s;n=1
  else:
   s,sv,cash,n,hit=fast_transfers(g,s,sv,cash,ft,pred,available,11 if late and not wc_done else None);active=s
  a,bn=components(active,pred,[t]);v=float(a[0,0]+(bn[0,0] if g==MC_BB else 0)-hit);total+=v;hits+=hit
  if not transferchip:ft=min(5,max(0,ft-n)+1)
  assert 1<=ft<=5 and cash>=0
 assert wc_done and used_wc in ([9,10,11] if late else [8])
 return total,used_wc,hits

# Common potential injury world for BOTH ownership paths and both point sets.
# Non-owned candidates can also be absent, preventing purchase of known injured players.
rng=np.random.default_rng(SEED);U=rng.random((DRAWS,12,N));duration=np.array([1,2,3,6],dtype=np.int16)[rng.integers(0,4,size=(DRAWS,12,N))];U[:,0,:]=1
sim=[];trials=[];zero=np.zeros((12,N),dtype=np.int16);base={}
for model in MATRICES:
 e,_,_=mcpath(model,False,zero);z,_,_=mcpath(model,True,zero);base[model]=(e,z);sim.append(dict(poengsett=model,p=0.,trekk=1,BB=MC_BB,FH=MC_FH,E=e,B_WC11=z,E_minus_B=e-z,andel_E_vinner=float(e>z),paret_SE=0.,delta_q10=e-z,delta_q90=e-z,B_tidlig_WC=0.,E_trekk=0.,B_trekk=0.,endring_delta_fra_p0=0.))
for probability in [.01,.02,.03]:
 worlds=np.zeros((DRAWS,12,N),dtype=np.int16)
 for draw in range(DRAWS):
  end=np.zeros(N,dtype=np.int16)
  for t in range(1,12):
   new=(end<=t)&(U[draw,t]<probability);end[new]=t+duration[draw,t,new];worlds[draw,t]=end
 for model in MATRICES:
  print('MC',model,probability,'n',DRAWS,flush=True);ee=[];zz=[];early=[];eh=[];zh=[]
  for draw in range(DRAWS):
   e,_,h1=mcpath(model,False,worlds[draw]);z,wg,h2=mcpath(model,True,worlds[draw]);ee.append(e);zz.append(z);early.append(wg<11);eh.append(h1);zh.append(h2);trials.append(dict(poengsett=model,p=probability,trekk=draw,E=round(e,4),B_WC11=round(z,4),E_minus_B=round(e-z,4),B_faktisk_WC=wg,E_trekk=h1,B_trekk=h2))
  ee=np.array(ee);zz=np.array(zz);delta=ee-zz;sim.append(dict(poengsett=model,p=probability,trekk=DRAWS,BB=MC_BB,FH=MC_FH,E=float(ee.mean()),B_WC11=float(zz.mean()),E_minus_B=float(delta.mean()),andel_E_vinner=float((delta>0).mean()),paret_SE=float(delta.std(ddof=1)/np.sqrt(DRAWS)),delta_q10=float(np.quantile(delta,.1)),delta_q90=float(np.quantile(delta,.9)),B_tidlig_WC=float(np.mean(early)),E_trekk=float(np.mean(eh)),B_trekk=float(np.mean(zh)),endring_delta_fra_p0=float(delta.mean()-(base[model][0]-base[model][1]))))
  print('MC result',model,probability,round(delta.mean(),1),'SE',round(sim[-1]['paret_SE'],2),flush=True)
save('skadesim_r3.csv',[{k:round(v,4) if isinstance(v,float) else v for k,v in r.items()} for r in sim]);save('skadetrekk_r3.csv',trials)
# Deterministic comparison with exactly the same lightweight policy used in MC.
benchmark=[]
for model in MATRICES:
 full=next(r for r in chip if r['poengsett']==model and r['test']=='samme_datoer' and r['E_BB']==MC_BB and r['E_FH']==MC_FH);e,z=base[model];benchmark.append(dict(poengsett=model,full_E=full['E'],full_B=full['B_WC11'],full_delta=full['E_minus_B'],lett_E=e,lett_B=z,lett_delta=e-z,delta_sokeforskjell=e-z-full['E_minus_B']))
save('simkontroll_r3.csv',[{k:round(v,2) if isinstance(v,float) else v for k,v in r.items()} for r in benchmark])

def grade(d):return 'bedre' if d>5 else 'dårligere' if d < -5 else 'likeverdig'
central=[r for r in sim if r['p']==.02];grades=[grade(r['E_minus_B']) for r in central];conclusion=grades[0] if len(set(grades))==1 else 'modellavhengig'
# Conservative action in an unresolved ±5-point/model-disagreement decision.
recommend_wc=all(r['E_minus_B']>5 for r in central) and all(r['E_minus_B']>0 for r in chip if r['test']=='samme_datoer')
lines=['# Siste beregningsrunde: WC8 mot WC11','',('**Anbefaling R8: WC nå.**' if recommend_wc else '**Anbefaling R8: Hold WC til R11. Szoboszlai → Tavernier nå; ingen trekk.**'),'',
'## 1. Identiske chipdatoer','',
'WC8 og B+WC11 er kjørt på nytt med samme BB/FH-par og samme R2-byttepolitikk. Begge søk får alle nominelle tropper som ekstra startpunkter; dette hindrer at en oversett finansieringskombinasjon blåser opp WC-fordelen. Endringen fra første søk står i sokekontroll_r3.csv. Alle fire felles par omfatter også hvert hovedløps valgte R2-par. «Eget beste» betyr beste av disse fire, ikke et bevist optimum over alle mulige chipdatoer.','',
'| Poengsett | BB/FH felles | E | B_WC11 | E minus B |','|---|---|---:|---:|---:|']
for r in chip:
 if r['test']=='samme_datoer':lines.append(f"| {r['poengsett']} | {r['E_BB']}/{r['E_FH']} | {r['E']:.1f} | {r['B_WC11']:.1f} | {r['E_minus_B']:+.1f} |")
for r in chip:
 if r['test']!='samme_datoer':lines+=['',f"Eget beste, {r['poengsett']}: E BB{r['E_BB']}/FH{r['E_FH']} = {r['E']:.1f}; B BB{r['B_BB']}/FH{r['B_FH']} = {r['B_WC11']:.1f}; forskjell {r['E_minus_B']:+.1f}."]
lines+=['',
'At B leder til R15 med tidligere BB, viser ikke alene at E-fordelen skyldes chips; en tidligere chip flytter poeng frem i tid. Tabellen over isolerer datoene. Bytter og tropper kan fortsatt utvikles forskjellig som følge av selve WC-tidspunktet.', '',
'## 2. Ukjente nye fravær','',
f'{DRAWS} parede trekk per p og poengsett, seed {SEED}. Her brukes **BB17/FH13 i begge baner**, så skadeeffekten blandes ikke med ulik chipkalender. Kampresultater trekkes ikke: poengene er forventede FPL-poeng gitt det trukne fraværet.', '',
'| Poengsett | p | E snitt | B snitt | E minus B | E vinner | Paret MC-SE | B WC9/10 |','|---|---:|---:|---:|---:|---:|---:|---:|']
for r in sim:
 if r['p']>0:lines.append(f"| {r['poengsett']} | {r['p']:.2f} | {r['E']:.1f} | {r['B_WC11']:.1f} | {r['E_minus_B']:+.1f} | {r['andel_E_vinner']:.1%} | {r['paret_SE']:.1f} | {r['B_tidlig_WC']:.1%} |")
lines+=['',
'Paret MC-SE måler bare numerisk usikkerhet fra 300 fraværstrekk, ikke feil i spillerprognosene. Andelen E vinner er heller ikke sannsynligheten for å vinne i faktiske kampresultater. 10/90-persentiler, trekkostnader og forskjell mot p=0 står i CSV-en.', '',
'Forenklinger:', '',
'- Samme potensielle fravær for hver spiller/runde brukes i begge baner og begge poengsett. Det trekkes for hele kjøpsuniverset, også ikke-eide kandidater; man kan dermed ikke kjøpe en spiller som nettopp er kjent skadet. Dette utvider «eide spillere» til en felles fotballverden og unngår kunstig friske erstattere.',
'- Fra R9 får en frisk spiller nytt fravær med p per runde; varighet 1/2/3/6 runder med lik sannsynlighet, startunden inkludert. Ingen ny hendelse mens spilleren allerede er ute. Varigheten blir kjent når fraværet starter. Fremtidige hendelser er skjult for byttepolitikken.',
'- B bruker WC i R11, fremskyndet til R9/R10 når minst tre av troppens nominelle beste elleve er ute før bytter. Etter R11 er WC brukt i begge baner; å vente til R11 gir ikke WC-forsikring gjennom hele julen.',
'- Samme grådige neste-fire-runder-regel i begge baner: rull ved gevinst ≤1, maks fem FT; ved taket/R19 terskel null. Ett ekstra trekk tillates bare ved brutto gevinst >5. Vinduet stopper før planlagt WC, utelater FH og inkluderer BB. FT ved WC/FH bevares uten opptjening, som R2-hovedantakelsen.',
'- For kjøretid: seks beste + tre billigste kandidater per posisjon; WC/FH starter fra skadefrie referansetroppsmaler/reparert tropp/billig tropp og bruker bredde én, maks seks forbedringsbytter. Innkjøp må være tilgjengelige og passere R2-rollefilteret; eide korttidsskadde kan beholdes når kjent retur forsvarer det. Salgspriser, bank og klubbgrense kontrolleres.',
'- Ingen nye rolleendringer, prisendringer, endret kampprogram eller tilfeldig normalrotasjon. Kjent fravær gir null poeng og beste lovlige ellever velges fra resten. BB gir bare poeng for tilgjengelige spillere. Forventede minutter og bonus er fortsatt R2-antakelser.', '',
'### Kontroll av det enklere søket, uten nye fravær','',
'| Poengsett | Fullt R2-søk E−B, BB17/FH13 | Lett MC-politikk, p=0 | Forskjell i margin |','|---|---:|---:|---:|']
for r in benchmark:lines.append(f"| {r['poengsett']} | {r['full_delta']:+.1f} | {r['lett_delta']:+.1f} | {r['delta_sokeforskjell']:+.1f} |")
for r in central:lines+=['',f"p=0,02, {r['poengsett']}: skadeverdenen flytter E−B med {r['endring_delta_fra_p0']:+.1f} poeng mot den samme lette politikkens p=0. Etter ±5-regelen: WC8 mot WC11 er **{grade(r['E_minus_B'])}**."]
lines+=['',
'## 3. Sluttvurdering','',
f'Klassifisering ved hovedverdien p=0,02: **{conclusion}**. «Likeverdig» betyr innenfor ±5 poeng. Dette er en praktisk beslutningsgrense, ikke en statistisk test.', '',
('WC nå leder over fem poeng i begge hovedsimuleringer og vinner med like chipdatoer. Jeg beholder anbefalingen om WC8, men bare innenfor de testede poeng- og fraværsmodellene.' if recommend_wc else 'Jeg trekker tilbake den svake R2-anbefalingen om WC nå. WC8 har ikke en entydig fordel over fem poeng i begge hovedsimuleringer med lik chipkalender. Når gevinsten er så liten/modellavhengig, anbefaler jeg å beholde muligheten til å velge tropp med oppdatert informasjon i R11. Dette er et beslutningsskjønn ved liten margin, ikke en ekstra beregnet «informasjonsbonus».'), '',
'Claude har rett i at rollestøy kan være større enn en ettpoengsmargin. Informasjonsverdi må likevel ikke dobbelttelles: forventet skadevern er nå simulert, og bedre benkedekning etter en tidlig WC kan også redusere skadetap. Nettovirkningen av skader trenger derfor ikke peke bare én vei.', '',
'R14–19-vurderingen er tatt med gjennom de faktiske kampene i Codex-poengene; repo-hybrid bruker Codex etter R13. COVs programskifte er dermed ikke ignorert. Fraværsmodellen øker ikke p særskilt i julen og simulerer ikke europeisk rotasjon: Claudes bekymring for BB i R17–19 er fortsatt en restusikkerhet, ikke et verifisert fratrekk.', '',
'Anbefalingen kan endres av nye bekreftede fravær/roller før R8-fristen, særlig hvis flere startere faller bort, eller hvis en ny felles tropp gir en klar >5-poengsfordel i begge poengsett. Ved hold: start Thiago foran Maguire, Haaland kaptein og Fernandes vice, som støttet i R2. Full oppstilling etter ett bytte står i rekonstruksjonen under.', '',
'Kjør: `/Users/simenflogstad/opt/anaconda3/bin/python3 samarbeid/gw08/codex/modell_r3.py`. Skriptet leser frosne R2-poeng, kompilierer bare funksjonsdefinisjoner fra R2-koden og tilføyer symmetriske starttropper; ingen R2-kjøring eller R2-skriving skjer. Alle nye filer har _r3. Ingen nett/installasjon.']
if not recommend_wc:
 s=orig-{SZ}|{TAV};_,xi,cap=lineup(s,8,'codex');bn=sorted(s-set(xi),key=lambda p:(E[p]['element_type']!=1,-MATRICES['codex'][ix[p],0]));name=lambda ps:', '.join(E[p]['web_name'] for p in ps)
 lines+=['','**R8 etter ett bytte:** '+name(xi)+'. Benk (keeper først, så utespillere i rekkefølge): '+name(bn)+'. Bank £1,6m; to FT til R9.']
text='\n'.join(lines)+'\n';(O/'kontroll_r3.md').write_text(text)
# Every displayed headline comes from a CSV-bound result object; precise simulations saved for audit.
assert len([r for r in chip if r['test']=='samme_datoer'])==8
assert len([r for r in sim if r['p']>0 and r['trekk']>=300])==6
for r in chip:assert f"{r['E_minus_B']:+.1f}" in text
for r in sim:
 if r['p']>0:assert f"{r['E_minus_B']:+.1f}" in text
(O/'validering_r3.json').write_text(json.dumps(dict(seed=SEED,trekk_per_p=DRAWS,chippar=PAIRS,MC_BB=MC_BB,MC_FH=MC_FH,anbefal_WC=recommend_wc,klassifisering=conclusion,main_delta={r['poengsett']:round(r['E_minus_B'],3) for r in central},legalitet_og_budsjett='assertions passerte',tidligere_filer='kun lest'),ensure_ascii=False,indent=2));print('DONE',conclusion,'WC now?',recommend_wc,flush=True)
