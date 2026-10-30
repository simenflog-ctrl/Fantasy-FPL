#!/usr/bin/env python3
"""Verify the finished R2 run and add explicit IDs/budget tables to its report.
No rerun of stochastic search, no changed projections; only *_r2 and kontroll.md writes.
Run after modell_r2.py using the existing Anaconda Python.
"""
import ast,csv,json,hashlib,re
from pathlib import Path
from collections import Counter
import numpy as np
O=Path(__file__).resolve().parent;D=O.parent/'data'
def load(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data):
    assert '_r2.' in name
    with (O/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
b=load(D/'bootstrap.json');E={e['id']:e for e in b['elements']};teams={t['id']:t['short_name'] for t in b['teams']}
validation=load(O/'validering_r2.json')
for filename,digest in validation['sha256'].items():assert sha(O/filename)==digest,filename
for filename,digest in load(O/'validering.json')['sha256'].items():assert sha(O.parent/filename)==digest,filename
plans=load(O/'planer_r2.json');gross=load(O/'grossplaner_r2.json');alternatives={r['alternativ']:r for r in rows(O/'alternativer_r2.csv')};gr={r['test']:r for r in rows(O/'gross_r2.csv')}
forecast_rows=rows(O/'spillerpoeng_r2.csv')+rows(O/'spillerpoeng_sen_r2.csv')
forecast={(int(r['id']),int(r['gw'])):r for r in forecast_rows}
assert len(forecast)==len(forecast_rows)==len(E)*11
assert len(rows(O/'spillerpoeng_r2.csv'))==len(E)*8
md={}
for r in rows(O/'minutter_antatt_r2.csv'):
    for g in range(int(r['gw_fra']),int(r['gw_til'])+1):md[int(r['id']),g]=r
for r in rows(O/'minutter_antatt.csv'):
    for g in range(int(r['gw_fra']),int(r['gw_til'])+1):
        p=int(r['id'])
        if g==9 and E[p]['web_name'] in ['Calafiori','B.Fernandes']:continue
        for key in ['p_start','forventede_min']:assert float(r[key])==float(md[p,g][key]),(p,g,key)
assert E[173]['web_name']=='Thomas' and teams[E[173]['team']]=='COV' and E[173]['element_type']==2
assert E[173]['status']=='d' and E[173]['chance_of_playing_next_round']==75
assert float(md[173,9]['p_start'])==.7015 and float(md[173,9]['forventede_min'])==59.28
# Recalculate EVERY exported player xP using the actual frozen R2 minutes.
# R1 output helpers disabled and its main guarded off, as in modell_r2.py.
tree=ast.parse((O/'modell.py').read_text())
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ('save','jwrite'):node.body=[ast.Pass()]
ns={'__file__':str(O/'modell.py'),'__name__':'readonly_consistency_check'}
exec(compile(ast.fix_missing_locations(tree),'<read-only forecast engine>','exec'),ns)
ns['md'].update(md);max_player_error=0.
for (p,g),r in forecast.items():
    codex=ns['forecast'](p,g)[0];raw=ns['repo_raw'].get((p,g));hybrid=codex
    if raw and float(raw['exp_minutes'])>0:hybrid=float(raw['xp'])*float(md[p,g]['forventede_min'])/float(raw['exp_minutes'])
    if p in ns['blocked']:codex=hybrid=0.
    for model,value in [('codex',codex),('repo_hybrid',hybrid)]:
        err=abs(value-float(r[model]));max_player_error=max(max_player_error,err);assert err<=.00000051,(p,g,model,err)
# Independent summation from rounded player CSV and the exact expectation weights.
max_plan_error=0.
for collection,summary in [(plans,alternatives),(gross,gr)]:
    for label,p in collection.items():
        computed=[]
        for r in p['rows']:
            squad=r['tropp'];counts=Counter(E[i]['element_type'] for i in squad)
            assert len(squad)==len(set(squad))==15 and counts=={1:2,2:5,3:5,4:3}
            assert max(Counter(E[i]['team'] for i in squad).values())<=3
            assert len(set(r['elleve']))==11 and set(r['elleve'])|set(r['benk'])==set(squad)
            assert r['kaptein'] in r['elleve'] and r['visekaptein'] in r['elleve']
            assert r['bank']>=0 and r['FT_etter']<=5
            points=[]
            for k,model in enumerate(['codex','repo_hybrid']):
                val=sum(float(forecast[i,r['gw']][model])*w for i,w in zip(squad,r['vekter']))-r['trekk']
                err=abs(val-r['poeng'][k]);max_plan_error=max(max_plan_error,err);assert err<.00001,(label,r['gw'],model,err)
                points.append(val)
            computed.append(points)
        computed=np.array(computed)
        for k,model in enumerate(['codex','repo_hybrid']):
            assert abs(computed[:,k].sum()-p['total'][k])<.0001
            if collection is plans:
                for suffix,n in [('R9',1),('R9_R12',4),('R9_R16',8),('R9_R19',11)]:assert abs(computed[:n,k].sum()-float(summary[label][model+'_'+suffix]))<.0051
            else:assert abs(computed[:,k].sum()-float(summary[label][model]))<.0001
# Same actual roster, XI, bench, captains and numerical path in both E and Gross-retain test.
for a,z in zip(plans['E']['rows'],gross['behold_BB19']['rows']):
    for key in ['tropp','elleve','benk','kaptein','visekaptein','poeng','vekter']:assert a[key]==z[key],key
assert 173 in plans['E']['rows'][0]['tropp']
assert max(alternatives,key=lambda lab:sum(float(alternatives[lab][m+'_R9_R19']) for m in ['codex','repo_hybrid']))=='E'
# Confirm the bridge-search correction selected the known stronger C plan at WC11.
assert plans['F_WC11']['rows'][0]['tropp']==plans['C']['rows'][0]['tropp']
assert np.allclose(plans['F_WC11']['total'],plans['C']['total'])
r2tree=ast.parse((O/'modell_r2.py').read_text());rolling=next(n for n in r2tree.body if isinstance(n,ast.FunctionDef) and n.name=='rolling')
rolling_source=ast.get_source_segment((O/'modell_r2.py').read_text(),rolling)
assert 'BB-9' not in rolling_source and 'bb-9' in rolling_source
for label,p in gross.items():
    if label.endswith('uten_BB'):assert not any(r['chip']=='BB' for r in p['rows']) and p['BB']==99
# Recompute every injury summary from its 200 paired raw trials.
sim=rows(O/'skadesim_r2.csv');trials=rows(O/'skadetrekk_r2.csv')
assert {float(r['p']) for r in sim}=={.01,.02,.03} and len(sim)==18
for r in sim:
    zz=[z for z in trials if z['p']==r['p'] and z['poengsett']==r['poengsett'] and z['mot']==r['mot']]
    assert len(zz)==int(r['trekk'])==200 and len({int(z['trekk']) for z in zz})==200
    aa=np.array([[float(z[k]) for k in ['E','F','delta']] for z in zz]);assert np.allclose(aa[:,0]-aa[:,1],aa[:,2])
    delta=aa[:,2];vals={'E_snitt':aa[:,0].mean(),'F_snitt':aa[:,1].mean(),'E_minus_F':delta.mean(),'E_vinner':(delta>0).mean(),'p10':np.quantile(delta,.1),'p90':np.quantile(delta,.9),'paret_SE':delta.std(ddof=1)/np.sqrt(200)}
    for key,val in vals.items():assert abs(val-float(r[key]))<1e-9,(r['p'],r['mot'],key)
# Budget and explicit ID artifacts.
chosen=plans[validation['anbefaling']];r=chosen['rows'][0];owned={int(z['id']):z for z in load(D/'salgspriser.json')}
names=lambda pp:', '.join(f"{E[p]['web_name']} ({p})" for p in pp)
roles={p:'XI' for p in r['elleve']}
for j,p in enumerate(r['benk']):roles[p]='Benk GK' if j==0 else 'Benk '+str(j)
roster=[]
for p in r['tropp']:
    sale=float(owned[p]['salgspris']) if p in owned else None;buy=E[p]['now_cost']/10 if p not in owned else None
    roster.append(dict(id=p,navn=E[p]['web_name'],lag=teams[E[p]['team']],pos=E[p]['element_type'],status=E[p]['status'],p_start_R9=float(md[p,9]['p_start']),forventede_min_R9=float(md[p,9]['forventede_min']),handling='behold' if p in owned else 'kjøp',salgspris=sale if sale is not None else '',kjopspris=buy if buy is not None else '',budsjettverdi=sale if sale is not None else buy,rolle_R9=roles[p],kaptein=p==r['kaptein'],visekaptein=p==r['visekaptein']))
outs=[dict(id=p,navn=E[p]['web_name'],salgspris=float(owned[p]['salgspris'])) for p in r['ut']]
sold=sum(z['salgspris'] for z in outs);bought=sum(E[p]['now_cost']/10 for p in r['inn']);effective=sum(z['budsjettverdi'] for z in roster)
assert abs(1.6+sold-bought-r['bank'])<1e-8 and abs(effective+r['bank']-99.4)<1e-8
save('anbefalt_tropp_r2.csv',roster);save('budsjett_ut_r2.csv',outs)
text=(O/'kontroll.md').read_text()
text=re.sub(r'^\*\*Ellever[^\n]*', '**Ellever (3–4–3):** '+names(r['elleve'])+'.',text,count=1,flags=re.M)
text=re.sub(r'^\*\*Kaptein:[^\n]*','**Kaptein:** '+names([r['kaptein']])+'. **Visekaptein:** '+names([r['visekaptein']])+'.',text,count=1,flags=re.M)
text=re.sub(r'^\*\*Benk:[^\n]*','**Benk:** '+names(r['benk'])+' (keeper først, deretter utespillere i prioritert rekkefølge).',text,count=1,flags=re.M)
lines=['## Konkret tropp og budsjett for anbefalingen','',
       '| ID | Spiller | Lag/status | Handling | Salgsverdi hvis eid | Ny kjøpspris | R9-rolle |','|---:|---|---|---|---:|---:|---|']
for z in roster:
    sale='–' if z['salgspris']=='' else f"{z['salgspris']:.1f}";buy='–' if z['kjopspris']=='' else f"{z['kjopspris']:.1f}"
    lines.append(f"| {z['id']} | {z['navn']} | {z['lag']}/{z['status']} | {z['handling']} | {sale} | {buy} | {z['rolle_R9']}{' (C)' if z['kaptein'] else ' (VC)' if z['visekaptein'] else ''} |")
lines+=['',f"Budsjett: £1,6m + verifiserte salg £{sold:.1f}m − kjøp £{bought:.1f}m = **£{r['bank']:.1f}m i bank**. Beholdt salgsverdi + nye kjøp er £{effective:.1f}m; sammen med banken er dette £99,4m. Tallene bruker de frosne prisene fra 29. oktober, ikke en ny prisinnhenting 30. oktober.", '',
        '| Ut-ID | Spiller ut | Verifisert salgspris |','|---:|---|---:|']
for z in outs:lines.append(f"| {z['id']} | {z['navn']} | {z['salgspris']:.1f} |")
lines+=['', '**Thomas er ID 173, COV, forsvarer, status d, 75 %, «'+E[173]['news']+'».** Han er ikke Thomas-Asante. R9-prognosen bruker p_start **0,7015**, **59,28 forventede minutter** og det reduserte p_play fra `p_play_r2.csv`. Det er også forutsetningen gjennom R19. Hele spillerfilen er nå gjenberegnet fra `minutter_antatt_r2.csv`; det er ingen frisk 90-minutters-Thomas skjult i poengtallene. E forblir best blant de testede hovedplanene på 50/50-gjennomsnittet av de to poengsettene med nettopp denne antakelsen. Dette er ikke en garanti for globalt optimum eller at Thomas faktisk starter.',
        'Fernandes (426) er solgt i denne WC9-planen. Ødegaard, Isak og Muharemović er med i de oppførte ID-ene. Dette er en ny WC-tropp fra R2, ikke R1-troppen. Salget er en samlet budsjett-/poengprioritering gjennom R19, ikke en påstand om at Fernandes er ute.', '',
        '## Sluttkontroll av avbrudd, ID-er og prognose','',
        'Kjøringen som fortsatte etter avbruddet fullførte alle tre skaderater og avsluttet med `DONE E`. 200 parede verdener ved hvert av 1 %, 2 % og 3 % gir 600 skadeverdener; begge poengsett er vurdert i de samme verdenene. Alle 18 sammendragsrader er uavhengig beregnet på nytt fra `skadetrekk_r2.csv`.',
        'Det raske søket er korrigert: broen til WC11 vurderer også de kjente tobytte-kandidatene og det påfølgende gratisbyttet i R10. F_WC11 velger nå samme R9-tropp som C (Calafiori/Thiago → Gabriel/Barry) og gir 676,8/731,3 nominelle poeng. Samtlige skaderater i rapporten bruker denne korrigerte politikken. Ingen fremtidige, ennå ukjente skader gis til planleggeren.',
        'Testen uten BB er også korrigert: faktisk BB-parameter sendes gjennom både WC-søket og byttepolitikken. Ingen del av den varianten planlegger for eller scorer BB19. At behold/selg-forskjellen likevel er den samme med og uten BB, er resultatet av den nye kjøringen. BB forklarer derfor ikke at Groß beholdes her. Codex foretrekker behold-pakken, mens repo-hybrid foretrekker salgspakken; dette er en reell modelluenighet.',
        f"Alle {len(E)*8} rader i `spillerpoeng_r2.csv`, samt R17–R19-filen, er kontrollert mot den faktiske minuttfilen og poengmotoren. Største avvik er {max_player_error:.8f} poeng, bare CSV-avrunding. Alle hoved- og Groß-planpoeng er deretter beregnet på nytt fra spiller-CSV-ene og de lagrede autobytte-/kapteinsvektene; største avvik per runde er {max_plan_error:.8f} poeng. Alle rapporterte horisonter stemmer innen avrunding.",
        'Tropp, ellever, benkrekkefølge, kaptein, visekaptein, vekter og poeng er identiske mellom E i `planer_r2.json` og «behold_BB19» i `grossplaner_r2.json`. De tilhørende CSV-radene er kontrollert mot disse eksakte planene. ID-listen over finnes også i `anbefalt_tropp_r2.csv`, med salgs-/kjøpspris og R9-rolle. Ingen R1-filer er endret.',
        'Robusthet: WC9 leder i begge modeller i skadeforløpene, men fordelen mot WC10 er liten i repo-hybrid; p10 ved 2 % og 3 % ligger svakt under null. Opprykksstressen reduserer repo-fordelen mot WC11 til omtrent 0,9 poeng. Anbefalingen er derfor WC9 etter forventning, med tydelig modellusikkerhet – ikke en sikker eller stor gevinst.','']
a=text.index('## Konkret tropp og budsjett for anbefalingen');z=text.index('## Kjøring og avgrensning',a)
text=text[:a]+'\n'.join(lines)+'\n'+text[z:]
post='Kjør deretter `python samarbeid/gw09/codex/sluttkontroll_r2.py` for ID-tabeller og uavhengig konsistenskontroll. Denne etterkontrollen endrer ingen prognoser eller simuleringstall.'
if post not in text:text+='\n'+post+'\n'
(O/'kontroll.md').write_text(text)
check=dict(status='OK',anbefaling=validation['anbefaling'],Thomas_id=173,Thomas_p_start=float(md[173,9]['p_start']),Thomas_forventede_min=float(md[173,9]['forventede_min']),spillerpoengrader_R9_R16=len(E)*8,alle_prognoser_gjenberegnet=len(forecast),max_spiller_avvik=max_player_error,max_lag_avvik_per_runde=max_plan_error,planer=len(plans),Gross_planer=len(gross),MC_nivaaer=[.01,.02,.03],MC_trekk_per_nivaa=200,MC_sammendrag_kontrollert=len(sim),E_identisk_Gross_behold_BB19=True,R1_hashkontroll=True,R2_opprinnelig_hashkontroll=True,skjulte_90_min_for_Thomas=False)
(O/'sluttkontroll_r2.json').write_text(json.dumps(check,ensure_ascii=False,indent=2))
validation.setdefault('rapport_for_idkontroll_sha256',validation['sha256']['kontroll.md']);validation['sha256']['kontroll.md']=sha(O/'kontroll.md')
for filename in ['sluttkontroll_r2.py','sluttkontroll_r2.json','anbefalt_tropp_r2.csv','budsjett_ut_r2.csv']:validation['sha256'][filename]=sha(O/filename)
validation['etterkontroll']='ID-er, alle spillerprognoser, alle hoved-/Gross-planpoeng og alle MC-sammendrag kontrollert fra filer.'
(O/'validering_r2.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2))
print(json.dumps(check,ensure_ascii=False,indent=2))
print('R9 XI:',names(r['elleve']));print('Bench:',names(r['benk']));print('Bank:',r['bank'])
