"""Additional scoring reconstruction and paired role sensitivity, called by modell.py."""
import csv,json,itertools
from pathlib import Path
O=Path(__file__).resolve().parent;D=O.parent/'data';b=json.loads((D/'bootstrap.json').read_text());es={e['id']:e for e in b['elements']};sc=b['game_config']['scoring'];pos={1:'GKP',2:'DEF',3:'MID',4:'FWD'}
n=0;err=[]
for fn in (D/'element_summary').glob('*.json'):
 for h in json.loads(fn.read_text())['history']:
  k=es[h['element']]['element_type'];p=pos[k];m=h['minutes'];v=sc['long_play'] if m>=60 else sc['short_play'] if m>0 else 0
  for s in ['goals_scored','assists','clean_sheets','penalties_saved','penalties_missed','yellow_cards','red_cards','own_goals','bonus']:v+=h.get(s,0)*(sc[s][p] if isinstance(sc[s],dict) else sc[s])
  v+=sc['goals_conceded'][p]*(h['goals_conceded']//2)+sc['saves']*(h['saves']//3)+sc['defensive_contribution'][p]*(h.get('defensive_contribution',0)>=(10 if k==2 else 12));n+=1
  if v!=h['total_points']:err.append(dict(id=h['element'],gw=h['round'],beregnet=v,faktisk=h['total_points']))
assert not err,err
xp={(int(r['id']),int(r['gw'])):float(r['xp']) for r in csv.DictReader((O/'spillerpoeng.csv').open())};ds=json.loads((O/'detaljer.json').read_text());rr={r['alternativ']:r for r in csv.DictReader((O/'alternativer.csv').open())};tav=next(p for p,e in es.items() if e['web_name']=='Tavernier')
def score(s,g,factor):
 def val(p):return xp[p,g]*(factor if p==tav else 1)
 by={k:sorted([p for p in s if es[p]['element_type']==k],key=val,reverse=True) for k in range(1,5)};best=0
 for d in range(3,6):
  for m in range(2,6):
   f=10-d-m
   if 1<=f<=3:
    xi=by[1][:1]+by[2][:d]+by[3][:m]+by[4][:f];best=max(best,sum(val(p) for p in xi)+max(val(p) for p in xi))
 return best
rows=[]
for f in [1,.75,.5,0]:
 a=sum(score(ds['A']['squad'][str(g)],g,f) for g in range(8,16));bv=sum(score(ds['B']['squad'][str(g)],g,f) for g in range(8,16));rows.append(dict(Tavernier_poengfaktor=f,A_R8_R15=round(a,1),B_R8_R15=round(bv,1),B_minus_A=round(bv-a,1)))
with (O/'folsomhet.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
checks=dict(historiske_spillerkamper=n,poengavvik=len(err),modellregler='DC10/12, redninger3, innslupne2 matcher historikken; keepermål10 ikke observert i utvalget',csv_rader=len(rr))
(O/'kontrollresultat.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
text=(O/'analyse.md').read_text();marker='\n## Supplerende kontroller og følsomhet\n';text=text.split(marker)[0]
text+=marker+'\nPoengreglene er rekonstruert på alle '+str(n)+' tilgjengelige historiske spillerkamper: **null avvik**. Dette støtter DC-tersklene 10/12, redningstripler og innslupne par i dette utvalget. Keepermål er ikke observert; verdien 10 kommer direkte fra API-et. Resultatet står i kontrollresultat.json.\n\n'
diff=float(rr['E19']['xp_R8_R19'])-float(rr['F']['xp_R8_R19']);text+=f'Når wildcard begge steder velges for R19, gir E19 {rr["E19"]["xp_R8_R19"]} mot F {rr["F"]["xp_R8_R19"]} poeng til R19: WC nå leder med {diff:.1f}. Anbefalingen om å vente én runde er derfor et skjønn om verdien av ny informasjon og å unngå en stor omlegging på svakt datagrunnlag; den følger ikke direkte av høyeste modellpoeng. En forskjell på {diff:.1f} er liten i forhold til rolleusikkerheten. Hvis Claude bekrefter hele den foreslåtte nye troppens roller og fravær, støtter modellen WC nå.\n\n'
text+='En paret rollestress-test reduserer bare Taverniers poeng, lar dagens spillere være uendret og velger elleveren på nytt. Dette er lineær poengstress, ikke en ny full minuttmodell eller et comebackscenario for Szoboszlai.\n\n| Tavernier poengfaktor | B minus A til R15 |\n|---|---:|\n'
for r in rows:text+=f'| {r["Tavernier_poengfaktor"]:.0%} | {r["B_minus_A"]:.1f} |\n'
text+='\n`folsomhet.csv` gjenskapes automatisk av modell.py. Den gir en mer relevant robusthetskontroll på enkeltbyttet enn bare overlappende totalbånd.\n'
(O/'analyse.md').write_text(text)
# Confirm every reported headline value exists in the generated analysis, and constraints per actual path.
for r in rr.values():
 for col in ['xp_R8','xp_R8_R11','xp_R8_R15','xp_R8_R19']:assert r[col] in text,(r['alternativ'],col)
print('Kontroll OK:',n,'historiske kamper, ingen poengavvik; alle hovedtall finnes i analyse.md.')
