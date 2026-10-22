#!/usr/bin/env python3
"""Offline model. Run with a Python containing numpy/scipy; no downloads.
Uses numpy, available in the existing Anaconda Python. All writes confined to this directory. Minute CSV is preserved as an override input.
"""
import csv,json,math,sys,itertools
from pathlib import Path
import numpy as np
import random
O=Path(__file__).resolve().parent; D=O.parent/'data'
def read(n):return json.loads((D/n).read_text())
def writecsv(n,rows):
 with (O/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
b=read('bootstrap.json'); es={e['id']:e for e in b['elements']}; ids=list(es); idx={p:i for i,p in enumerate(ids)}; N=len(ids)
sales=read('salgspriser.json'); original={r['id'] for r in sales}; sell={r['id']:round(r['salgspris']*10) for r in sales}; teams={t['id']:t['short_name'] for t in b['teams']}; sc=b['game_config']['scoring']; pos={1:'GKP',2:'DEF',3:'MID',4:'FWD'}; fixtures=read('fixtures.json')
hist={int(p.stem):json.loads(p.read_text())['history'] for p in (D/'element_summary').glob('*.json')}
# Estimate role from seven observed rounds, recent individual history where available.
mp=O/'minutter_antatt.csv'
if not mp.exists():
 rows=[]
 for p,e in es.items():
  h=hist.get(p,[]); weights=[.5**((7-r['round'])/4) for r in h]
  ps=(sum(w*r['starts'] for w,r in zip(weights,h))+.35)/(sum(weights)+.7) if h else (e['starts']+.35)/7.7
  mg=e['minutes']/max(e['starts'],1); mg=min(90,max(60,mg)); sub=max(0,e['minutes']-e['starts']*mg)/7
  avail=0 if e['status'] in ['i','u','s','n'] else (e.get('chance_of_playing_next_round') if e.get('chance_of_playing_next_round') is not None else (50 if e['status']=='d' else 100))/100
  ps*=avail; minute=min(90,ps*mg+sub*avail)
  rows.append(dict(id=p,navn=e['web_name'],lag=teams[e['team']],gw_fra=8,gw_til=19,p_start=round(ps,3),forventede_min=round(minute,1),kilde='Antakelse: starter/minutter R1–7, 0.7 kamp prior; API-status holdes til R19'))
 writecsv('minutter_antatt.csv',rows)
mr=list(csv.DictReader(mp.open()))
def minutes(p,g):
 matches=[r for r in mr if int(r['id'])==p and int(r['gw_fra'])<=g<=int(r['gw_til'])]
 assert matches, (p,g)
 r=matches[-1];return float(r['p_start']),float(r['forventede_min'])
# Team goal model: scored/conceded smoothed by seven league-average games.
done=[f for f in fixtures if f['finished'] and f['event']<=7]; mean=sum(f['team_h_score']+f['team_a_score'] for f in done)/(2*len(done)); tm={t:[0,0,0] for t in teams}
for f in done:
 for t,g,a in [(f['team_h'],f['team_h_score'],f['team_a_score']),(f['team_a'],f['team_a_score'],f['team_h_score'])]:
  tm[t][0]+=g;tm[t][1]+=a;tm[t][2]+=1
strength={t:((v[0]+7*mean)/(v[2]+7)/mean,(v[1]+7*mean)/(v[2]+7)/mean) for t,v in tm.items()}
pri={}
for k in range(1,5):
 ee=[e for e in es.values() if e['element_type']==k and e['minutes']>0]; mins=sum(e['minutes'] for e in ee)
 pri[k]={s:sum(float(e.get(s,0)) for e in ee)/mins*90 for s in ['expected_goals','expected_assists','bonus','yellow_cards','red_cards','own_goals','penalties_saved','penalties_missed','saves']}
xp=np.zeros((N,12)); attack=np.zeros_like(xp); rows=[]
for i,p in enumerate(ids):
 e=es[p];k=e['element_type'];psname=pos[k];m=e['minutes']; rates={s:(float(e.get(s,0))*90+270*v)/(m+270) for s,v in pri[k].items()}
 # DC threshold validation is performed below on available individual histories.
 h=hist.get(p,[]); eligible=[r for r in h if r['minutes']>=60]; threshold=10 if k==2 else 12
 dc=(sum(r.get('defensive_contribution',0)>=threshold for r in eligible)+1)/(len(eligible)+3) if eligible else min(.8,float(e.get('defensive_contribution',0))/max(m/90,1)/threshold*.35)
 for g in range(8,20):
  ps,mi=minutes(p,g);p60=min(ps,mi/65)*.95; pp=min(1,ps+max(0,mi-ps*min(90,m/max(e['starts'],1)))/20)
  total=att=0
  for f in fixtures:
   if f['event']!=g or e['team'] not in [f['team_h'],f['team_a']]:continue
   home=e['team']==f['team_h'];opp=f['team_a'] if home else f['team_h'];lam=mean*strength[opp][0]*strength[e['team']][1]*(.9 if home else 1.1);scale=strength[opp][1]*(1.1 if home else .9)
   a=(rates['expected_goals']*sc['goals_scored'][psname]+rates['expected_assists']*sc['assists'])*mi/90*scale
   conceded=sum((z//2)*math.exp(-lam)*lam**z/math.factorial(z) for z in range(20))
   save= rates['saves']*mi/max(ps,1e-6)/90 if ps else 0
   savepts=ps*sum((z//3)*math.exp(-save)*save**z/math.factorial(z) for z in range(35)) if k==1 else 0
   other=sum(rates[s]*sc[s] for s in ['bonus','yellow_cards','red_cards','own_goals','penalties_saved','penalties_missed'])*mi/90
   total+=sc['short_play']*pp+(sc['long_play']-sc['short_play'])*p60+a+sc['clean_sheets'][psname]*math.exp(-lam)*p60+sc['goals_conceded'][psname]*conceded*mi/90+savepts+dc*sc['defensive_contribution'][psname]*p60+other;att+=a
  xp[i,g-8]=max(0,total);attack[i,g-8]=att;rows.append(dict(id=p,navn=e['web_name'],gw=g,xp=round(total,3),angrep=round(att,3)))
writecsv('spillerpoeng.csv',rows)
# Deterministic feasible beam/local search. No certificate of global optimality.
cache={}; statuses=[]
def solve(gws,base=original,budget=993,nchange=None,bb=False):
 key=(tuple(gws),tuple(sorted(base)),budget,nchange,bb)
 if key in cache:return cache[key]
 columns=[g-8 for g in gws]; costs={p:(sell[p] if p in original and p in base else es[p]['now_cost']) for p in ids}
 pools={k:sorted([p for p in ids if es[p]['element_type']==k and es[p].get('can_select',True)],key=lambda p:sum(xp[idx[p],j] for j in columns),reverse=True)[:18] for k in range(1,5)}
 for k in pools:
  pools[k]=list(set(pools[k])|set(sorted([p for p in ids if es[p]['element_type']==k and es[p].get('can_select',True)],key=lambda p:costs[p])[:5])|{p for p in base if es[p]['element_type']==k})
 memo={}
 def value(s):
  key=tuple(sorted(s))
  if key in memo:return memo[key]
  # Same legal XI objective as reported; optional BB scores all 15.
  v=sum((sum(xp[idx[p],g-8] for p in s)+xp[idx[lineup(s,g)[2]],g-8]) if bb else lineup(s,g)[0] for g in gws)
  memo[key]=v;return v
 def neighbors(s,only_original=False):
  cost=sum(costs[p] for p in s);clubs={t:sum(es[p]['team']==t for p in s) for t in teams}
  for out in sorted(s):
   if only_original and out not in base:continue
   for inc in sorted(pools[es[out]['element_type']]):
    if inc in s or (only_original and inc in base):continue
    if cost-costs[out]+costs[inc]>budget:continue
    if clubs[es[inc]['team']]-(es[out]['team']==es[inc]['team'])>=3:continue
    yield frozenset(s-{out}|{inc})
 if nchange is not None:
  beam=[frozenset(base)]
  for depth in range(nchange):
   if nchange==1:
    pools={k:[p for p in ids if es[p]['element_type']==k and es[p].get('can_select',True)] for k in range(1,5)}
   cand=set(z for s in beam for z in neighbors(s,True))
   if not cand:raise RuntimeError('No feasible plan')
   beam=sorted(cand,key=lambda s:(value(s),tuple(sorted(s))),reverse=True)[:24]
  best=max(beam,key=value)
 else:
  seeds=[frozenset(base)]
  # Cheap legal squad allows funds to be reallocated across positions.
  cheap=set()
  for k,n in [(1,2),(2,5),(3,5),(4,3)]:
   for p in sorted([p for p in ids if es[p]['element_type']==k],key=lambda p:(costs[p],p)):
    if sum(es[z]['team']==es[p]['team'] for z in cheap)<3:
     cheap.add(p)
     if sum(es[z]['element_type']==k for z in cheap)==n:break
  seeds.append(frozenset(cheap)); best=seeds[0]
  for seed in seeds:
   current=seed
   for _ in range(35):
    cand=max(neighbors(current),key=value,default=current)
    if value(cand)<=value(current)+1e-8:break
    current=cand
   if value(current)>value(best):best=current
 statuses.append(dict(gws=gws,nchange=nchange,status='heuristisk, ikke globalt optimalitetsbevis',objective=round(value(best),3),evaluated=len(memo)))
 cache[key]=set(best);return set(best)

def lineup(sq,g,arr=xp):
 by={k:sorted([p for p in sq if es[p]['element_type']==k],key=lambda p:arr[idx[p],g-8],reverse=True) for k in range(1,5)};best=None
 for d in range(3,6):
  for m in range(2,6):
   f=10-d-m
   if not 1<=f<=3:continue
   xi=by[1][:1]+by[2][:d]+by[3][:m]+by[4][:f];cap=max(xi,key=lambda p:arr[idx[p],g-8]);val=sum(arr[idx[p],g-8] for p in xi)+arr[idx[cap],g-8]
   if best is None or val>best[0]:best=(val,xi,cap)
 return best

def names(s):return ', '.join(es[p]['web_name'] for p in sorted(s)) or '–'
def bank(sq):return (993-sum(sell[p] if p in original else es[p]['now_cost'] for p in sq))/10
plans=[]
for label,n in [('A',0),('B',1),('C',2),('D3',3),('D4',4),('D5',5),('E',None)]:
 sq=original if n==0 else solve(list(range(8,16)),nchange=n)
 plans.append(dict(label=label,path={g:sq for g in range(8,20)},hit=4*max(0,(n or 0)-2),wc=8 if n is None else None))
plans.append(dict(label='E19',path={g:solve(list(range(8,20))) for g in range(8,20)},hit=0,wc=8))
# Later wildcard: bridge = optimized 1-FT plan, no further transfers before WC.
bridge=plans[1]['path'][8];future=[]
for g in range(9,20):
 sq=solve(list(range(g,20)));path={r:bridge if r<g else sq for r in range(8,20)};v=sum(lineup(path[r],r)[0] for r in range(8,20));future.append((v,g,path))
_,wg,path=max(future,key=lambda x:x[0]);plans.append(dict(label='F',path=path,hit=0,wc=wg))
# Chips on B bridge. Free Hit restores bridge the next round; no permanent transfers.
fh={g:solve([g]) for g in range(8,20)}
bb_gain={g:sum(xp[idx[p],g-8] for p in bridge)-sum(xp[idx[p],g-8] for p in lineup(bridge,g)[1]) for g in range(8,20)}
fh_gain={g:lineup(fh[g],g)[0]-lineup(bridge,g)[0] for g in range(8,20)}
bg=max(bb_gain,key=bb_gain.get);fg=max(fh_gain,key=fh_gain.get)
plans.extend([dict(label='G_BB',path={g:bridge for g in range(8,20)},hit=0,wc=None,bb=bg),dict(label='G_FH',path={g:fh[g] if g==fg else bridge for g in range(8,20)},hit=0,wc=None,fh=fg)])
results=[];details={}
for plan in plans:
 path=plan['path'];sq=path[8]; vals={};low={};high={}
 for g in range(8,20):
  for arr,out in [(xp,vals),(np.maximum(0,.9*xp-.25*attack),low),(1.05*xp+.25*attack,high)]:
   v,xi,cap=lineup(path[g],g,arr)
   if plan.get('bb')==g:v=sum(arr[idx[p],g-8] for p in path[g])+arr[idx[cap],g-8]
   out[g]=v
 # Common potential chips envelope conditional on each permanent path, no WC/chip collisions.
 gains={g:sum(xp[idx[p],g-8] for p in path[g])-sum(xp[idx[p],g-8] for p in lineup(path[g],g)[1]) for g in range(8,20)}
 # Existing FH candidates must also fit actual ownership after a wildcard.
 fgs={g:max(0,lineup(fh[g],g)[0]-lineup(path[g],g)[0]) if sum(sell[p] if p in original and p in path[g] else es[p]['now_cost'] for p in fh[g])<=993 else 0 for g in range(8,20)}
 pairs=[(gains[a]+fgs[z],a,z) for a in range(8,20) for z in range(8,20) if a!=z and a!=plan['wc'] and z!=plan['wc'] and not(z==8 and path[8]!=original)]
 gain,bbg,fhg=max(pairs)
 v,xi,cap=lineup(sq,8);vice=max((p for p in xi if p!=cap),key=lambda p:xp[idx[p],0]);bench=sorted(sq-set(xi),key=lambda p:(es[p]['element_type']!=1,-xp[idx[p],0]))
 row=dict(alternativ=plan['label'],inn=names(sq-original),ut=names(original-sq),poengtrekk=plan['hit'],bank=round(bank(sq),1),xp_R8=round(vals[8]-plan['hit'],1),xp_R8_R11=round(sum(vals[g] for g in range(8,12))-plan['hit'],1),xp_R8_R15=round(sum(vals[g] for g in range(8,16))-plan['hit'],1),usikkerhet_R8_R15=f"{sum(low[g] for g in range(8,16))-plan['hit']:.0f}–{sum(high[g] for g in range(8,16))-plan['hit']:.0f}",xp_R8_R19=round(sum(vals.values())-plan['hit'],1),WC=plan['wc'] or '',BB=plan.get('bb',''),FH=plan.get('fh',''),potensial_BB_FH=round(gain,1),BB_potensiell=bbg,FH_potensiell=fhg)
 results.append(row);details[plan['label']]=dict(xi=names(xi),kaptein=es[cap]['web_name'],visekaptein=es[vice]['web_name'],benk=names(bench),benk_rekkefolge=[es[p]['web_name'] for p in bench],wc_runde=plan['wc'],wc_inn=names(path[plan['wc']]-bridge) if plan['wc'] and plan['wc']>8 else '',wc_ut=names(bridge-path[plan['wc']]) if plan['wc'] and plan['wc']>8 else '',squad={g:sorted(s) for g,s in path.items()},ukepoeng={g:round(v,2) for g,v in vals.items()},salg=round(sum(sell[p] for p in original-sq)/10,1),kjop=round(sum(es[p]['now_cost'] for p in sq-original)/10,1))
 # Exact legality/budget assertions.
 for g,s in path.items():
  assert len(s)==15 and bank(s)>=-1e-8
  assert all(sum(es[p]['team']==t for p in s)<=3 for t in teams)
  assert [sum(es[p]['element_type']==k for p in s) for k in range(1,5)]==[2,5,5,3]
writecsv('alternativer.csv',results);writecsv('wildcard_tidspunkt.csv',[dict(gw=g,xp_R8_R19=round(v,1),bank=bank(path[g]),inn=names(path[g]-bridge),ut=names(bridge-path[g])) for v,g,path in future]);writecsv('chip_tidspunkt.csv',[dict(gw=g,BB_merpoeng=round(bb_gain[g],1),FH_merpoeng=round(fh_gain[g],1),FH_tropp=names(fh[g])) for g in range(8,20)])
(O/'detaljer.json').write_text(json.dumps(details,ensure_ascii=False,indent=2));(O/'solver.json').write_text(json.dumps(statuses,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2));print('Later WC:',wg,'BB:',bg,'FH:',fg)
# Report is generated from precisely the same result objects, avoiding stale copied numbers.
rmap={r['alternativ']:r for r in results}
rank=sorted(results,key=lambda r:r['xp_R8_R15'],reverse=True)
lines=['# Beregning og anbefaling R8', '',
'**Foreløpig anbefaling: ett gratisbytte, Szoboszlai → '+rmap['B']['inn']+'. Behold wildcard til ny vurdering i R9.** Dette er alternativ B nå og F som betinget videre plan. Bekreft innspillerens rolle med Claude før fristen. Modellen har ikke nok informasjon til å bevise et sesongoptimum eller et optimalt wildcardlag.', '',
'## Verifiserte inngangsdata', '',
'Fryst API-uttrekk i `../data/`, 22. oktober 2026. Lag 7089878, to gratisbytter, bank £1,0m. Salgsverdi £98,3m; disponibel likvidasjonsverdi £99,3m. Szoboszlai har skadeflagg og 0 %. MUN og BHA har tre hver. Ingen blanke/doble runder i den frosne terminlisten til R19. WC1, BB1 og FH1 utløper R19 ifølge grunnlag.md. API-scoring gir keepermål 10. Ingen nettdata eller repoets avledede poeng brukes som modellinput.', '',
'## Modell og søk', '',
'Alle alternativer bruker samme spillerpoeng og beste lovlige formasjon hver runde, med dobbel kaptein. 15 spillere: 2/5/5/3, maks tre fra hver klubb; én keeper, minst tre forsvarere, to midtbanespillere og én spiss i elleveren. Budsjettet kontrolleres i heltall (tideler av million). Beholdte egne spillere verdsettes til salgspris, innkjøp til nåpris. Ingen prisendringer antas. Wildcard betyr ikke at beholdte spillere må kjøpes tilbake.', '',
'Lagstyrke bygger på mål for/mot i ferdigspilte R1–7, krympet med sju ligagjennomsnittskamper. Hjemme-/bortefaktor er antatt 1,1/0,9. Ingen motstanderjustert regresjon. Individuelle xG/xA per 90 krympes med 270 minutter mot minuttvektet posisjonssnitt fra samme sesong. Mål og assists skaleres med motstanderens forsvar. Poisson brukes til nullen, innslupne par og redningstripler. Bonus, kort, selvmål og straffehendelser bruker krympede historiske rater. Bonus er ikke modellert som konkurranse om seks poeng, en svakhet.', '',
'Poengvektene leses fra `game_config.scoring`, inklusive keepermål 10. Tersklene 60 minutter, to innslupne, tre redninger og DC 10/12 er regelantakelser fra grunnlaget; API-scoring oppgir bare poengvektene. DC for egne spillere bruker treff i 60+-kamper med tre pseudoobservasjoner (ett treff). For andre brukes aggregert DC per 90 delt på terskelen × 0,35, avgrenset ved 0,8. Dette er en grov og viktig antakelse, ikke en verifisert sannsynlighetsmodell.', '',
'`minutter_antatt.csv` er både leveranse og input. Første kjøring oppretter den; senere kjøringer bevarer overstyringer. Alle 668 spillere har intervall R8–19. Egne spillere får nyere starter vektet med halveringstid fire runder; andre får (starter + 0,35)/7,7. Forventet spilletid bygger på årets minutter og starter. Skade-/suspensjonsstatus holdes gjennom hele perioden, inklusive null for Szoboszlai. Det er et konservativt scenario, ikke en prognose om skadevarighet. P(60+) settes til 0,95 × min(p_start, forventede_min/65); innhoppssannsynlighet er en enkel restberegning. Rader som overlapper: siste rad gjelder. Claude kan endre p_start og forventede_min per intervall uten å endre kode.', '',
'B undersøker alle tilgjengelige enkeltbytter. C og D bruker deterministisk beam-søk med 24 beholdte tilstander og en kandidatpool per posisjon. Wildcard/FH bruker lokal forbedring fra eksisterende og billig lovlig tropp. Disse er **beste funn, ikke bevist optimale**. Særlig tverrposisjonelle finansieringsbytter kan overses. `solver.json` viser evaluerte tilstander og status. Ingen heltallsløser er tilgjengelig i installert miljø.', '',
'For A–E beholdes troppen etter R8 og startlaget optimeres ukentlig. F gjør B i R8 og wildcard i oppgitt runde; ellers holdes troppen. E velges for R8–15, E19 for R8–19 som horisontkontroll. Ingen videre gratisbytter brukes i disse sammenligningene. Resultatene viser derfor ikke beste adaptive flerukersplan, og lang horisont overvurderer gevinsten av mange bytter nå sammenlignet med gratis reparasjoner senere. G_BB og G_FH bygger på B og bruker hver sin chip; FH-troppen forsvinner etter chiprunden.', '',
'## Modellresultater og rangering', '',
'Poeng inkluderer kaptein og oppgitte trekk. Spredning er stresscenario for forventningen, **ikke** et sannsynlighetsintervall for faktiske poeng: lav = 0,90 × spillerpoeng − 0,25 × angrepspoeng; høy = 1,05 × spillerpoeng + 0,25 × angrepspoeng. Elleveren velges på nytt i scenarioene. Faktisk kampvariasjon og lagkorrelasjon kommer i tillegg. Overlapp kan ikke brukes som en statistisk test på forskjellen.', '',
'| Rang | Alternativ | R8 | R8–11 | R8–15 | Stress R8–15 | R8–19 |',
'|---|---|---:|---:|---:|---|---:|']
for n,r in enumerate(rank,1):lines.append(f"| {n} | {r['alternativ']} | {r['xp_R8']:.1f} | {r['xp_R8_R11']:.1f} | {r['xp_R8_R15']:.1f} | {r['usikkerhet_R8_R15']} | {r['xp_R8_R19']:.1f} |")
lines+=['', 'Rangeringen er rå modellpoeng under de oppgitte faste planene. Den er ikke en handlingsrangering med likt chipforbruk. E/E19/F bruker WC, G bruker BB/FH, mens A–D beholder disse ressursene.', '',
 f"B slår A med {rmap['B']['xp_R8_R15']-rmap['A']['xp_R8_R15']:.1f} poeng til R15 i scenarioet der Szoboszlai fortsatt er ute. C gir ytterligere {rmap['C']['xp_R8_R15']-rmap['B']['xp_R8_R15']:.1f}, men koster den andre gratisbytten og selger en spillende Thiago. D3/D4/D5 viser at trekk kan tjenes inn dersom troppen ellers holdes urørt; dette er ikke grunnlag for å ta trekk nå, fordi gratisbytter senere ikke er optimert. Anbefalingen om å selge den skadde spilleren er mer robust enn navnene på innspillerne, chipdatoene eller salg av friske spillere.", '',
'## Startlag R8 for anbefalt B', '',
'**Elleve:** '+details['B']['xi']+'.', '',
'**Kaptein:** '+details['B']['kaptein']+'. **Visekaptein:** '+details['B']['visekaptein']+'.', '',
'**Benk i rekkefølge:** '+', '.join(details['B']['benk_rekkefolge'])+' (reservekeeper først; deretter tre utespillere). Modellen regner ikke automatiske innbytter eller kapteinsfallback; forventningene inkluderer redusert spilletid, men benkedekning er ikke lagt oppå startelleveren. Bench Boost teller alle 15 fullt etter spillerens forventning.', '',
'## Budsjettkontroll og konkrete bytter', '',
'Likviditetskontroll for R8: £1,0 + salgsinntekter − kjøp = bank. Ingen salgsgevinst fra beholdte spillere brukes som ekstra penger.', '',
'| Alternativ | Ut | Inn | Salg | Kjøp | Bank | Trekk |',
'|---|---|---|---:|---:|---:|---:|']
for r in results:
 d=details[r['alternativ']];lines.append(f"| {r['alternativ']} | {r['ut']} | {r['inn']} | {d['salg']:.1f} | {d['kjop']:.1f} | {r['bank']:.1f} | {r['poengtrekk']} |")
lines+=['',f"F: WC i R{wg}. Ut fra B-troppen: {details['F']['wc_ut']}. Inn: {details['F']['wc_inn']}. Bank etter WC: £{bank(path[wg]):.1f}m (se wildcard_tidspunkt.csv for autoritativ kontroll).", '',
'Alle tropper gjennomgår assertions for klubbgrense, posisjoner og salgsverdibudsjett. `detaljer.json` inneholder ID-er og ukepoeng for hele planene. `chip_tidspunkt.csv` viser også de midlertidige FH-troppene. Priser kan endres før fristen; modellen må da kjøres med oppdaterte godkjente data.', '',
'## Chips og fleksibilitet til R19', '',
f"På B-troppen gir BB mest i R{bg}: {bb_gain[bg]:.1f} merpoeng; FH mest i R{fg}: {fh_gain[fg]:.1f}. Dette er betinget av at B-troppen beholdes, og ingen fremtidige blanke/doble runder. Lite BB-utbytte skyldes blant annet reservekeeper og en spiss uten registrerte minutter.", '',
'For hver permanent plan viser alternativer.csv også beste funne kombinasjon av BB og FH før R20, på ulike runder og uten kollisjon med wildcard. Dette er en **oppnåelig ekstra chipverdi blant undersøkte tropper**, ikke noe som skal legges på G-radene som allerede bruker chipen. FH-kandidatene søkes med opprinnelig eierskap, men budsjettet kontrolleres på nytt for faktisk eierskap hver runde. Ugyldige kandidater får null FH-merverdi (bruk ordinær tropp); derfor kan bedre gyldige FH-tropper være oversett. FH i R8 er utelukket når planen har permanente R8-bytter. Samlet chipoptimering kan gi andre tropper og datoer.', '',
'| Permanent plan | BB+FH anslag | BB-runde | FH-runde |',
'|---|---:|---:|---:|']
for key in ['A','B','C','E','E19','F']:
 r=rmap[key];lines.append(f"| {key} | {r['potensial_BB_FH']:.1f} | {r['BB_potensiell']} | {r['FH_potensiell']} |")
lines+=['',
'F er den konkrete senere wildcardplanen med høyest R8–19-sum i det søkte settet. Alle datoer R9–19 finnes i wildcard_tidspunkt.csv. Forskjeller på få poeng mellom tidlige wildcarddatoer er for små til å overstyre nye lagnyheter. Behold muligheten til å vente; ikke bind deg til en ubetinget WC-dato. BB etter WC bør planlegges når begge keepere og benken faktisk spiller; en ny søking for BB kan kreve en annen wildcardtropp. Modellen har ikke optimert dette samlet.', '',
'Gratisbytter: A gir tre i R9; B gir to; C og D gir én, forutsatt ett nytt gratisbytte per runde og maks fem. Til R15 er alle statiske planer ved taket, og det illustrerer hvorfor det er urimelig å behandle dem som sesongoptimum. En ekstra FT har ingen fast poengverdi: den er verdiløs uten et ønsket bytte, men kan spare et trekk på fire poeng når behovet kommer. Bruk 0–4 poeng som beslutningsscenario for én ekstra FT, ikke som estimert forventning eller absolutt tak. A vs B må også veies mot at B fjerner en kjent nullspiller. FT-bevaring ved WC/FH er ikke uttrykkelig dokumentert i de frosne regelfeltene; repoets automatiske reset til én kan ikke bekreftes fra dette datagrunnlaget. Ingen poeng er kreditert på grunnlag av den regelen.', '',
'WC1/FH1/BB1 har ingen ubrukt terminalverdi etter R19: de utløper. Men troppen og bank/lagrede bytter påvirker R20 og videre. Nytt chipsett i andre halvdel gjør det heller ikke riktig å spare første sett forbi fristen. R19 er derfor en nyttig planleggingsgrense, ikke sesongslutt. Det mangler en adaptiv sesongsimulering, prisprognose og verdi av fremtidig informasjon; ikke tolk R8–15-summen som målet for resten av sesongen.', '',
'## Kontroll av repoets plan.json', '',
'Enig i å undersøke wildcard: flere benkespillere har svak spilletid, Szoboszlai er ute, og forbedringspotensialet er synlig også her. Uenig i at det foreliggende resultatet er tilstrekkelig grunnlag for å aktivere chipen:', '',
'- `src/optimize.py` bruker samme nåpris ved kjøp og salg. De ti R8-salgene i plan.json gir £58,8m etter salgsprisene; innkjøpene koster £60,7m i frosne bootstrap. Med £1,0m bank mangler **£0,9m**. Selv salg til nåpris (£59,1m) gir et underskudd på £0,6m mot disse dataene. Planen ser derfor også ut til å bruke andre pris-/bankinnganger enn det fryste grunnlaget.',
'- Start-FT er hardkodet til én, mens faktisk utgangspunkt er to. WC-reset til én er også hardkodet; dette er ikke verifisert i de tilgjengelige API-reglene.',
'- `HORIZON = 5` gir R8–12. Spillerpoengfilen omfatter R8–13, ikke R8–15 eller R19. Slutt-BB kan derfor få kunstig stor verdi uten å prise etterfølgende troppsbehov.',
'- Maks tre spillere per klubb og lovlige formasjoner er korrekt inkludert i optimizeren. Wildcard og BB hindres fra samme runde. FH er ikke modellert.',
'- Målfunksjonen inkluderer 15 % av all benk, ekstra fire poeng straff per hit og byttefriksjon. `objective=362.55` er derfor ikke rene forventede FPL-poeng og kan ikke sammenlignes direkte med tabellen her.',
'- `expected_points.py` har keepermål hardkodet til 6. Minuttmodellen håndterer skadeflagg og innhopp, men bruker samme minutter over horisonten, generisk P(60+|start) og forsøker å hente fjorårsdata over nett. Dette kan ikke reproduseres fra bare det frosne datagrunnlaget. Det er ikke belegg for at dens tall er kontrollert.', '',
'## Viktigste begrensninger og neste kontroll', '',
'Bare 15 element-summary-filer finnes, så nylig form, starter, DC-treff og pris-/rollehistorikk kan ikke kontrolleres tilsvarende for innspillere. Det mangler skadekomback, forventede rotasjoner, startoppstillinger og dokumentert fremtidig terminendring. API summer er data; hjemmefaktorer, ratekrymping, minuttmodell og skadevarighet er antakelser; tabellpoengene er modellresultater.', '',
'Navn som Tzolakis, De Cuyper og Tavernier må rollevalideres av Claude. Aggregert DC og kort historikk kan overvurdere dem. Ved store spilletidsoverstyringer skal alle alternativene kjøres på nytt. Skadefrisk Szoboszlai fra for eksempel R10 og reduserte minutter for innkandidatene er de viktigste neste scenarioene. Stressbåndene over erstatter ikke disse spesifikke scenariotestene.', '',
'## Reproduksjon og kontroll', '',
'Kjør fra repoets rot:', '',
'```sh', '/Users/simenflogstad/opt/anaconda3/bin/python3 samarbeid/gw08/codex/modell.py', '```', '',
'Bruk eksisterende Python med numpy (systemets python3 har ikke numpy). Ingen pakker installeres og ingen nettforespørsler utføres. Skriptet skriver bare i codex/, bevarer minutter_antatt.csv og gjenskaper CSV, JSON, denne analysen og modellpoeng. Søk har fast rekkefølge og ingen tilfeldig trekning. Summer i analysen genereres direkte fra samme resultatobjekter som alternativer.csv; lovlighet og budsjett kontrolleres under kjøring. A–G er representert, med D3/D4/D5 og G_BB/G_FH som egne rader.', '',
'**Oppdraget er ikke løst som et bevist globalt flerperiode-/sesongoptimum.** Leveransen er en kjørbar, etterprøvbar grunnmodell med konkrete lovlige alternativer og tydelige forbehold om søk og fremtidige handlinger.']
# F bank: avoid a loop-variable shadowing affecting report.
for i,line in enumerate(lines):
 if line.startswith('F: WC i '):
  fs=set(details['F']['squad'][wg]);lines[i]=line[:line.index('Bank etter WC:')]+f'Bank etter WC: £{bank(fs):.1f}m.'
(O/'analyse.md').write_text('\n'.join(lines)+'\n')

import runpy
runpy.run_path(str(O/'kontroller.py'),run_name='__main__')
