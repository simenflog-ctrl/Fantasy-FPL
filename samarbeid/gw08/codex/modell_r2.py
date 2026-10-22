#!/usr/bin/env python3
"""Offline revision. Existing Anaconda Python + numpy; all writes inside codex.
Deterministic bounded search, rolling four-GW transfers, actual ownership prices.
"""
import csv,json,math,time,hashlib
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
O=Path(__file__).resolve().parent;ROOT=O.parents[2];D=O.parent/'data';DER=ROOT/'data/derived'
def load(p):return json.loads(p.read_text())
def csvrows(p):return list(csv.DictReader(p.open()))
def save(n,rows):
 with (O/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
b=load(D/'bootstrap.json'); E={e['id']:e for e in b['elements']};ids=sorted(E);ix={p:i for i,p in enumerate(ids)};N=len(ids);teamnames={t['id']:t['short_name'] for t in b['teams']};kinds={1:'GKP',2:'DEF',3:'MID',4:'FWD'};sc=b['game_config']['scoring'];fx=load(D/'fixtures.json');sales=load(D/'salgspriser.json');orig=frozenset(r['id'] for r in sales);osell={r['id']:int(round(10*r['salgspris'])) for r in sales};cost={p:e['now_cost'] for p,e in E.items()};history={int(p.stem):load(p) for p in sorted((D/'element_summary').glob('*.json'))};ks=np.array([E[p]['element_type'] for p in ids]);team=np.array([E[p]['team'] for p in ids]);formations=[(d,m,10-d-m) for d in range(3,6) for m in range(2,6) if 1<=10-d-m<=3];old={(int(r['id']),int(r['gw'])):float(r['xp']) for r in csvrows(O/'spillerpoeng.csv')}
# Verify local derived historical inputs against the frozen bootstrap.
pm=[r for r in csvrows(DER/'player_matches.csv') if int(r['gw'])<=7 and int(r['fixture']) in {f['id'] for f in fx if f['finished']}];agg=defaultdict(lambda:[0.,0.]);tx=defaultdict(float)
for r in pm:
 p=int(r['element']);agg[p][0]+=float(r['minutes']);agg[p][1]+=float(r['expected_goals']);tx[int(r['fixture']),int(r['team'])]+=float(r['expected_goals'])
assert all(agg[p][0]==e['minutes'] and abs(agg[p][1]-float(e['expected_goals']))<.05 for p,e in E.items())
# xGA comes from opponent's total xG, never sum overlapping player xGA.
tm=defaultdict(lambda:[0.,0.,0]);done=[f for f in fx if f['finished'] and f['event']<=7]
for f in done:
 for t,op in [(f['team_h'],f['team_a']),(f['team_a'],f['team_h'])]:tm[t][0]+=tx[f['id'],t];tm[t][1]+=tx[f['id'],op];tm[t][2]+=1
mean=sum(v[0] for v in tm.values())/sum(v[2] for v in tm.values());strength={t:((v[0]+7*mean)/(v[2]+7)/mean,(v[1]+7*mean)/(v[2]+7)/mean) for t,v in tm.items()};save('lagstyrke_r2.csv',[dict(lag=teamnames[t],xG=v[0],xGA=v[1],kamper=v[2],angrep=strength[t][0],forsvar=strength[t][1]) for t,v in tm.items()])
stats=['expected_goals','expected_assists','bonus','yellow_cards','red_cards','own_goals','penalties_saved','penalties_missed','saves'];pri={}
for k in range(1,5):
 ee=[e for e in E.values() if e['element_type']==k and e['minutes']>0];m=sum(e['minutes'] for e in ee);pri[k]={s:sum(float(e.get(s,0)) for e in ee)*90/m for s in stats}
# Role assumptions use all newly available histories. CSV remains overrideable.
mp=O/'minutter_antatt_r2.csv'
if not mp.exists():
 rows=[]
 for p,e in E.items():
  h=history.get(p,{}).get('history',[]);w=[.5**((7-r['round'])/4) for r in h];den=sum(w)+.7;ps=(sum(a*r['starts'] for a,r in zip(w,h))+.35)/den if h else (e['starts']+.35)/7.7
  starts=[r for r in h if r['starts']];mg=sum(r['minutes'] for r in starts)/len(starts) if starts else min(90,e['minutes']/max(1,e['starts']));sub=[r['minutes'] for r in h if not r['starts'] and r['minutes']>0];psub=(1-ps)*len(sub)/max(1,len(h)-len(starts));mi=ps*mg+psub*(sum(sub)/len(sub) if sub else 0);p60=ps*(sum(r['minutes']>=60 for r in starts)+4.5)/(len(starts)+5)
  avail=0 if e['status'] in ['i','u','n','s'] else (e['chance_of_playing_next_round']/100 if e.get('chance_of_playing_next_round') is not None else .5 if e['status']=='d' else 1)
  rows.append(dict(id=p,navn=e['web_name'],lag=teamnames[e['team']],gw_fra=8,gw_til=19,p_start=round(ps*avail,3),forventede_min=round(mi*avail,1),p_play=round((ps+psub)*avail,3),p_60=round(p60*avail,3),kilde='Vektede starter R1–7, egen min/start og 60+-andel; API-status viderefoert'))
 save(mp.name,rows)
mins=csvrows(mp);md={}
for r in mins:
 for g in range(int(r['gw_fra']),int(r['gw_til'])+1):md[int(r['id']),g]=r
rates={};prior_sources={};dc_rates={}
for p,e in E.items():
 k=e['element_type'];past=[r for r in history.get(p,{}).get('history_past',[]) if r.get('minutes',0)>=450 and r['season_name']<'2026/27'][-2:];prior={};weights=[.5**(len(past)-1-j) for j in range(len(past))]
 for s in stats:
  valid=[(w,r) for w,r in zip(weights,past) if s in r and (s not in ['expected_goals','expected_assists'] or r[s] is not None)]
  prior[s]=sum(w*float(r.get(s,0)) for w,r in valid)*90/sum(w*r['minutes'] for w,r in valid) if valid else pri[k][s]
 weight=540 if past else 270;rates[p]={s:(float(e.get(s,0))*90+weight*prior[s])/(e['minutes']+weight) for s in stats};prior_sources[p]=[r['season_name'] for r in past]
 h=[r for r in history.get(p,{}).get('history',[]) if r['minutes']>=60];threshold=10 if k==2 else 12
 # Empirical DC hit rate; no artificial mean->tail conversion.
 kh=[r for pp,hh in history.items() if E[pp]['element_type']==k for r in hh.get('history',[]) if r['minutes']>=60];base=sum(r.get('defensive_contribution',0)>=threshold for r in kh)/max(1,len(kh)) if k!=1 else 0
 dc_rates[p]=(sum(r.get('defensive_contribution',0)>=threshold for r in h)+3*base)/(len(h)+3)

def forecast(p,g,healthy=False):
 e=E[p];k=e['element_type'];po=kinds[k];r=rates[p];mm=md[p,g];ps=float(mm['p_start']);mi=float(mm['forventede_min']);pp=float(mm['p_play']);p60=float(mm['p_60'])
 if healthy:
  h=history[p]['history'];st=[r for r in h if r['starts']];ps=(e['starts']+.35)/7.7;mi=ps*sum(r['minutes'] for r in st)/len(st);pp=ps;p60=ps*(sum(r['minutes']>=60 for r in st)+4.5)/(len(st)+5)
 val=att=0
 for f in fx:
  if f['event']!=g or e['team'] not in [f['team_h'],f['team_a']]:continue
  home=e['team']==f['team_h'];op=f['team_a'] if home else f['team_h'];lam=mean*strength[op][0]*strength[e['team']][1]*(.9 if home else 1.1);scale=strength[op][1]*(1.1 if home else .9)
  a=(r['expected_goals']*sc['goals_scored'][po]+r['expected_assists']*sc['assists'])*mi/90*scale
  gc=sum(z//2*math.exp(-lam)*lam**z/math.factorial(z) for z in range(25));sv=r['saves']*mi/max(ps,1e-8)/90 if ps else 0;sp=ps*sum(z//3*math.exp(-sv)*sv**z/math.factorial(z) for z in range(40)) if k==1 else 0
  other=sum(r[s]*sc[s] for s in stats if s not in ['expected_goals','expected_assists','saves'])*mi/90
  val+=pp+p60+a+sc['clean_sheets'][po]*math.exp(-lam)*p60+sc['goals_conceded'][po]*gc*mi/90+sp+dc_rates[p]*sc['defensive_contribution'][po]*p60+other;att+=a
 return max(0,val),att
XP=np.array([[forecast(p,g)[0] for g in range(8,20)] for p in ids]);ATT=np.array([[forecast(p,g)[1] for g in range(8,20)] for p in ids]);REPO=XP.copy();repo_rows=csvrows(DER/'expected_points.csv');coverage=set()
for r in repo_rows:
 p=int(r['element']);g=int(r['gw'])
 if p in ix and 8<=g<=13:REPO[ix[p],g-8]=float(r['xp']);coverage.add((p,g))
# Injury availability applies equally, even if derived projections are stale.
for p,e in E.items():
 if e['status'] in ['u','n','i','s'] or e.get('chance_of_playing_next_round')==0:REPO[ix[p],:]=0
names=['Haaland','B.Fernandes','Mbeumo','Rogers','Thiago','Tavernier'];cal=[]
for name in names:
 p=next(p for p,e in E.items() if e['web_name']==name);e=E[p];cal.append(dict(id=p,navn=name,forrige_per_runde=sum(old[p,g] for g in range(8,14))/6,ny_per_runde=float(XP[ix[p],:6].mean()),repo_per_runde=float(REPO[ix[p],:6].mean()),observert_per_runde=e['total_points']/7,ny_xG90=rates[p]['expected_goals'],ny_xA90=rates[p]['expected_assists'],prior=';'.join(prior_sources[p]) or 'posisjon'))
save('kalibrering_r2.csv',[{k:round(v,3) if isinstance(v,float) else v for k,v in r.items()} for r in cal]);save('spillerpoeng_r2.csv',[dict(id=p,navn=E[p]['web_name'],gw=g,codex=round(XP[ix[p],g-8],4),repo_hybrid=round(REPO[ix[p],g-8],4)) for p in ids for g in range(8,20)])
COMEBACK=False
# Every purchase must be available AND a plausible starter, including both keepers.
def eligible(p):
 e=E[p];return e.get('can_select',True) and e['status'] not in ['u','n','i','s'] and e.get('chance_of_playing_next_round')!=0 and float(md[p,8]['p_start'])>=.5
universe=frozenset(p for p in ids if eligible(p));save('kjopsunivers_r2.csv',[dict(id=p,navn=E[p]['web_name'],lag=teamnames[E[p]['team']],status=E[p]['status'],p_start=md[p,8]['p_start'],godkjent=int(p in universe)) for p in ids]);assert all(E[p]['web_name'] not in ['Dennis','Hughes'] for p in universe)
# A finite history/configuration remains deterministic across runs.
REPEAT=REPO.copy();REPEAT[:,6:]=REPO[:,:6].mean(axis=1)[:,None]
MATRICES={'codex':XP,'repo_hybrid':REPO,'repo_repeat':REPEAT};optcache={};evalcache={};searchlog=[];evaln=0

def scores(s,model):
 """Vectorized exact best legal XI + captain for all twelve rounds."""
 key=(model,tuple(sorted(s)))
 if key in evalcache:return evalcache[key]
 x=MATRICES[model];parts={};cs={}
 for k in range(1,5):
  q=np.array([ix[p] for p in s if E[p]['element_type']==k],dtype=int);a=np.sort(x[q],axis=0)[::-1];parts[k]=a;cs[k]=np.vstack((np.zeros(12),np.cumsum(a,axis=0)))
 best=np.zeros(12)
 for d,m,f in formations:
  v=cs[1][1]+cs[2][d]+cs[3][m]+cs[4][f]+np.maximum.reduce([parts[k][0] for k in range(1,5)])
  best=np.maximum(best,v)
 allpts=x[[ix[p] for p in s]].sum(axis=0);cap=np.maximum.reduce([parts[k][0] for k in range(1,5)]);bench=allpts-(best-cap)
 evalcache[key]=(best,bench);return best,bench

def lineup(s,g,model,force=None,exclude=None):
 arr=MATRICES[model];v=lambda p:arr[ix[p],g-8];by={k:sorted([p for p in s if E[p]['element_type']==k],key=lambda p:(v(p),-p),reverse=True) for k in range(1,5)};best=(-1,None,None)
 for d,m,f in formations:
  xi=by[1][:1]+by[2][:d]+by[3][:m]+by[4][:f]
  if force and force not in xi:continue
  if exclude and exclude in xi:continue
  cap=max(xi,key=v);val=sum(v(p) for p in xi)+v(cap)
  if val>best[0]:best=(val,xi,cap)
 return best

def saleprice(p,owned):return owned.get(p,cost[p])
def legal(s):return len(s)==15 and all(sum(E[p]['element_type']==k for p in s)==n for k,n in [(1,2),(2,5),(3,5),(4,3)]) and max(Counter(E[p]['team'] for p in s).values())<=3

def allowed(g):return universe|{SZ} if COMEBACK and g>=11 else universe

def pool(model,g,end,base):
 x=MATRICES[model];out={}
 for k in range(1,5):
  ps=[p for p in allowed(g) if E[p]['element_type']==k];top=sorted(ps,key=lambda p:(float(x[ix[p],g-8:end-7].sum()),-p),reverse=True)[:16];cheap=sorted(ps,key=lambda p:(cost[p],p))[:7];out[k]=sorted(set(top+cheap)|{p for p in base if E[p]['element_type']==k and p in allowed(g)})
 return out

def optimize(model,g,end,base,owned,bank,mode='wc'):
 key=(model,g,end,tuple(sorted(base)),tuple(sorted(owned.items())),bank,mode)
 if key in optcache:return optcache[key]
 pools=pool(model,g,end,base);liquid=bank+sum(saleprice(p,owned) for p in base);price={p:saleprice(p,owned) for p in ids};bbweight=.0 if mode=='fh' else .35
 def val(s):
  a,bn=scores(s,model);return float(a[g-8:end-7].sum()+bbweight*max(bn[g-8:end-7]))
 def adjacent(s):
  spent=sum(price[p] for p in s);clubs=Counter(E[p]['team'] for p in s)
  for out in sorted(s):
   for inc in pools[E[out]['element_type']]:
    if inc in s or spent-price[out]+price[inc]>liquid:continue
    if clubs[E[inc]['team']]-(E[out]['team']==E[inc]['team'])>=3:continue
    yield frozenset(s-{out}|{inc})
 cheap=set()
 for k,n in [(1,2),(2,5),(3,5),(4,3)]:
  for p in sorted([p for p in allowed(g) if E[p]['element_type']==k],key=lambda p:(price[p],p)):
   if sum(E[z]['team']==E[p]['team'] for z in cheap)<3:
    cheap.add(p)
    if sum(E[z]['element_type']==k for z in cheap)==n:break
 assert legal(cheap) and sum(price[p] for p in cheap)<=liquid
 # Seed with legal filtered current team, cheap squad, and previous best at same date.
 seeds=[frozenset(cheap)]
 if base<=allowed(g):seeds.append(frozenset(base))
 # Repair original zero-minute bench for starting seed, including financing by cheap swaps.
 repair=set(base)
 for bad in sorted(base-allowed(g)):
  candidates=[p for p in pools[E[bad]['element_type']] if p not in repair and sum(E[z]['team']==E[p]['team'] for z in repair-{bad})<3]
  if candidates:repair.remove(bad);repair.add(min(candidates,key=lambda p:(price[p],p)))
 if repair<=allowed(g) and legal(repair) and sum(price[p] for p in repair)<=liquid:seeds.append(frozenset(repair))
 best=max(seeds,key=val);beam=list(set(seeds));seen=set(beam)
 for step in range(18 if mode=='wc' else 13):
  cand=set(z for s in beam for z in adjacent(s) if z not in seen)
  if not cand:break
  ranked=sorted(cand,key=lambda s:(val(s),tuple(sorted(s))),reverse=True);beam=ranked[:3];seen.update(beam)
  if val(beam[0])>val(best):best=beam[0]
  if step>5 and val(beam[0])<val(best)-2:break
 assert best<=allowed(g) and legal(best);optcache[key]=best;searchlog.append(dict(model=model,gw=g,mode=mode,evaluated=len(seen),objective=round(val(best),2)));return best

def enact(base,owned,bank,new):
 out=base-new;ins=new-base;cash=bank+sum(owned[p] for p in out)-sum(cost[p] for p in ins);assert cash>=0
 no={p:owned[p] if p in base else cost[p] for p in new};assert legal(new);return no,cash

def transfers(model,g,base,owned,bank,ft,next_wc=None,next_fh=None,next_bb=None):
 # Same greedy four-round rule for E and every delayed-WC plan. One extra paid move max.
 s=frozenset(base);n=0;hits=0;log=[];end=min(19,g+3,next_wc-1 if next_wc and next_wc>g else 19)
 columns=[h-8 for h in range(g,end+1) if h!=next_fh]
 def objective(s):
  a,bn=scores(s,model);return float(a[columns].sum()+(bn[next_bb-8] if next_bb and next_bb-8 in columns else 0))
 for _ in range(min(5,ft+1)):
  pools=pool(model,g,end,s);v0=objective(s);best=None;clubs=Counter(E[p]['team'] for p in s)
  for out in sorted(s):
   for inc in pools[E[out]['element_type']]:
    if inc in s or bank+owned[out]<cost[inc] or clubs[E[inc]['team']]-(E[out]['team']==E[inc]['team'])>=3:continue
    new=frozenset(s-{out}|{inc});gain=objective(new)-v0
    if best is None or (gain,-inc,-out)>best[:3]:best=(gain,-inc,-out,new,out,inc)
  threshold=(0 if ft-n>=5 or g==19 else 1.) if n<ft else 5.
  if best is None or best[0]<=threshold:break
  gain,_,_,new,out,inc=best
  owned,bank=enact(s,owned,bank,new);s=new;n+=1;hits+=4 if n>ft else 0;log.append(dict(ut=out,inn=inc,gevinst_4=round(gain,2),trekk=4 if n>ft else 0))
  if n>ft:break
 return s,owned,bank,n,hits,log

TAV=next(p for p,e in E.items() if e['web_name']=='Tavernier');SZ=next(p for p,e in E.items() if e['web_name']=='Szoboszlai');DH=next(p for p,e in E.items() if e['web_name']=='Dewsbury-Hall');TH=next(p for p,e in E.items() if e['web_name']=='Thiago');MAG=next(p for p,e in E.items() if e['web_name']=='Maguire')

def simulate(model,wg,bb=None,fh=None,chip_ft='preserve',r8buy=TAV):
 s=orig;owned=dict(osell);bank=10;ft=2;rows=[];total=0
 for g in range(8,20):
  before=s;cashbefore=bank;ftbefore=ft;chip='';hit=0;n=0;logs=[];temporary=None
  if g==wg:
   chip='WC';new=optimize(model,g,19,s,owned,bank);owned,bank=enact(s,owned,bank,new);s=new;n=len(s-before)
  elif g==fh:
   chip='FH';temporary=optimize(model,g,g,s,owned,bank,mode='fh')
  elif g==8:
   new=frozenset(s-{SZ}|{r8buy});assert r8buy in universe;owned,bank=enact(s,owned,bank,new);s=new;n=1;logs=[dict(ut=SZ,inn=r8buy,gevinst_4=None,trekk=0)]
  else:
   s,owned,bank,n,hit,logs=transfers(model,g,s,owned,bank,ft,next_wc=wg,next_fh=fh,next_bb=bb)
  active=temporary or s;v,xi,cap=lineup(active,g,model);bench=scores(active,model)[1][g-8]
  if g==bb:chip='BB';v+=bench
  v-=hit;total+=v
  if chip in ['WC','FH']:ft=1 if chip_ft=='reset' else min(5,ftbefore+1) if chip_ft=='plus' else ftbefore
  else:ft=min(5,max(0,ftbefore-n)+1)
  assert legal(s) and bank>=0 and 1<=ft<=5
  if chip in ['WC','FH']:assert active<=allowed(g)
  rows.append(dict(gw=g,chip=chip,ft_for=ftbefore,ft_etter=ft,bytter=n,trekk=hit,bank_for=cashbefore/10,bank=bank/10,inn=sorted(active-before) if chip=='FH' else sorted(s-before),ut=sorted(before-active) if chip=='FH' else sorted(before-s),tropp=sorted(active),permanent=sorted(s),owned=owned.copy(),elleve=xi,kaptein=cap,poeng=round(v,6),bb_merverdi=round(bench,6),logs=logs))
 return dict(model=model,wc=wg,bb=bb,fh=fh,chip_ft=chip_ft,total=total,rows=rows)

def schedule(model,wg,chip_ft='preserve'):
 baseline=simulate(model,wg,chip_ft=chip_ft);gains=[]
 for row in baseline['rows']:
  g=row['gw']
  if g==wg or g==8:continue # All schedules use a permanent action in R8.
  s=frozenset(row['permanent']);new=optimize(model,g,g,s,row['owned'],round(row['bank']*10),mode='fh');gain=scores(new,model)[0][g-8]-scores(s,model)[0][g-8];gains.append((float(gain),g))
 pairs=[]
 for row in baseline['rows']:
  a=row['gw']
  if a==wg:continue
  for gain,z in gains:
   if a!=z:pairs.append((gain+row['bb_merverdi'],a,z))
 # Replay top two schedules with actual FT/no permanent FH move and own budgets.
 pairs=sorted(pairs,reverse=True);paths=[]
 for _,a,z in pairs[:2]:paths.append(simulate(model,wg,bb=a,fh=z,chip_ft=chip_ft))
 best=max(paths,key=lambda p:p['total']);best['baseline_total']=baseline['total'];best['schedules_tested']=[(p['bb'],p['fh'],round(p['total'],2)) for p in paths];return best

plans=[]
for model in ['codex','repo_hybrid','repo_repeat']:
 for wg in [8,11,13,15,17]:
  print('Run',model,'WC',wg,flush=True);p=schedule(model,wg);plans.append(p);print('Result',round(p['total'],1),'BB',p['bb'],'FH',p['fh'],'cached squads',len(evalcache),flush=True)
# Cross-score the exact implemented paths, not just each model's chosen lineup.
def pathscore(plan,model):
 total=0
 for r in plan['rows']:
  g=r['gw'];s=frozenset(r['tropp']);v=scores(s,model)[0][g-8]
  if r['chip']=='BB':v+=scores(s,model)[1][g-8]
  total+=v-r['trekk']
 return total
out=[]
for p in plans:
 vals={r['gw']:r['poeng'] for r in p['rows']};out.append(dict(poengsett=p['model'],alternativ='E' if p['wc']==8 else 'B_WC'+str(p['wc']),WC=p['wc'],BB=p['bb'],FH=p['fh'],R8=round(vals[8],1),R8_R11=round(sum(vals[g] for g in range(8,12)),1),R8_R13=round(sum(vals[g] for g in range(8,14)),1),R8_R15=round(sum(vals[g] for g in range(8,16)),1),R8_R19=round(p['total'],1),uten_BB_FH=round(p['baseline_total'],1),trekk=sum(r['trekk'] for r in p['rows']),bank_R8=p['rows'][0]['bank'],bank_R19=p['rows'][-1]['bank'],FT_R20=p['rows'][-1]['ft_etter'],kryss_codex=round(pathscore(p,'codex'),1),kryss_repo=round(pathscore(p,'repo_hybrid'),1)))
save('alternativer_r2.csv',out);save('wildcard_tidspunkt_r2.csv',[dict(r,E_minus_plan=round(next(z['R8_R19'] for z in out if z['poengsett']==r['poengsett'] and z['WC']==8)-r['R8_R19'],1)) for r in out]);(O/'planer_r2.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2));save('sokelog_r2.csv',searchlog)
# Targeted R8 sensitivities, with unchanged four-round/12-round lineup selection.
sens=[]
for model in ['codex','repo_hybrid']:
 for buy in [TAV,DH]:
  s=frozenset(orig-{SZ}|{buy});a=scores(s,model)[0];v,xi,cap=lineup(s,8,model);vt=lineup(s,8,model,force=TH,exclude=MAG)[0];vm=lineup(s,8,model,force=MAG,exclude=TH)[0];sens.append(dict(poengsett=model,scenario=E[buy]['web_name'],R8=round(v,2),R8_R13=round(float(a[:6].sum()),2),R8_R19=round(float(a.sum()),2),Thiago_i_XI=round(vt,2),Maguire_i_XI=round(vm,2),Thiago_minus_Maguire=round(vt-vm,2)))
 # Tavernier role downside: requested p_start=.75 and expected minutes=70; recompute points from forecast.
 mm=md[TAV,8];saved={g:md[TAV,g].copy() for g in range(8,20)};arr=MATRICES[model];before=arr[ix[TAV]].copy()
 for g in range(8,20):
  r=md[TAV,g].copy();ratio=.75/max(float(r['p_start']),1e-8);r.update(p_start=.75,forventede_min=52.5,p_play=.75,p_60=.75*.95);md[TAV,g]=r
  # Repo lacks components for remodelling: apply ratio of recomputed Codex forecast.
  arr[ix[TAV],g-8]=before[g-8]*forecast(TAV,g)[0]/max(XP[ix[TAV],g-8] if model!='codex' else before[g-8],1e-8)
 evalcache.clear();s=frozenset(orig-{SZ}|{TAV});a=scores(s,model)[0];sens.append(dict(poengsett=model,scenario='Tavernier .75 start / 70 min gitt start (52.5 forventet)',R8=round(float(a[0]),2),R8_R13=round(float(a[:6].sum()),2),R8_R19=round(float(a.sum()),2),Thiago_i_XI='',Maguire_i_XI='',Thiago_minus_Maguire=''))
 arr[ix[TAV]]=before
 for g,r in saved.items():md[TAV,g]=r
 evalcache.clear()
 # Unknown comeback: explicit conditional stress, healthy from R11, no medical claim.
 szsaved=arr[ix[SZ]].copy()
 for g in range(11,20):arr[ix[SZ],g-8]=forecast(SZ,g,healthy=True)[0]
 evalcache.clear();a=scores(orig,model)[0];bs=scores(frozenset(orig-{SZ}|{TAV}),model)[0];sens.append(dict(poengsett=model,scenario='Szoboszlai frisk fra R11: behold / B-fordel',R8=round(float(a[0]),2),R8_R13=round(float(a[:6].sum()),2),R8_R19=round(float(a.sum()),2),Thiago_i_XI='',Maguire_i_XI='',Thiago_minus_Maguire=round(float(bs.sum()-a.sum()),2)))
 arr[ix[SZ]]=szsaved;evalcache.clear()
for r in sens:
 r['B_minus_behold']=r['Thiago_minus_Maguire'] if r['scenario'].startswith('Szoboszlai') else ''
 if r['scenario'].startswith('Szoboszlai'):r['Thiago_minus_Maguire']=''
save('folsomhet_r2.csv',sens)
# Full-policy tests: conditional return, FT preservation, and a common compromise E path.
COMEBACK=True
return_runs=[]
for model in ['codex','repo_hybrid']:
 name=model+'_retur';a=MATRICES[model].copy()
 for g in range(11,20):a[ix[SZ],g-8]=forecast(SZ,g,healthy=True)[0]
 MATRICES[name]=a;later=max([p for p in plans if p['model']==model and p['wc']!=8],key=lambda p:p['total'])
 for wg in [8,later['wc']]:
  print('Comeback',model,wg,flush=True);z=schedule(name,wg);return_runs.append(z)
COMEBACK=False
save('retur_r2.csv',[dict(poengsett=p['model'],WC=p['wc'],BB=p['bb'],FH=p['fh'],R8_R19=round(p['total'],1),bank=p['rows'][-1]['bank']) for p in return_runs])
fttests=[]
for model in ['codex','repo_hybrid']:
 selected=[p for p in plans if p['model']==model];chosen=[next(p for p in selected if p['wc']==8),max([p for p in selected if p['wc']!=8],key=lambda p:p['total'])]
 for p in chosen:
  for rule in ['preserve','plus','reset']:
   z=simulate(model,p['wc'],p['bb'],p['fh'],chip_ft=rule);fttests.append(dict(poengsett=model,WC=p['wc'],FT_regel=rule,BB=p['bb'],FH=p['fh'],R8_R19=round(z['total'],1)))
save('FT_regler_r2.csv',fttests)
# Common path chosen on equal blend, then scored by both original models.
MATRICES['blend']=(XP+REPO)/2
print('Common E blend',flush=True);common=schedule('blend',8)
common_scores={m:round(pathscore(common,m),1) for m in ['codex','repo_hybrid']}
(O/'felles_E_r2.json').write_text(json.dumps(dict(plan=common,kryss=common_scores),ensure_ascii=False,indent=2))
(O/'retur_planer_r2.json').write_text(json.dumps(return_runs,ensure_ascii=False,indent=2))
# Also test Tavernier vs DH with actual policy and baseline late-WC dates.
buytests=[]
for model in ['codex','repo_hybrid']:
 chosen=max([p for p in plans if p['model']==model and p['wc']!=8],key=lambda p:p['total'])
 for buy in [TAV,DH]:
  z=simulate(model,chosen['wc'],chosen['bb'],chosen['fh'],r8buy=buy);buytests.append(dict(poengsett=model,WC=chosen['wc'],R8_kjop=E[buy]['web_name'],R8_R19=round(z['total'],1)))
save('byttevalg_policy_r2.csv',buytests)
# Exhaustive one-week pair of midfield choices above plus budgets/legality in every simulation.
print('Main runs finished',flush=True)
import runpy
runpy.run_path(str(O/'rapport_r2.py'),init_globals={'data':globals()},run_name='__main__')
