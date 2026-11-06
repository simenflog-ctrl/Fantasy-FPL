#!/usr/bin/env python3
"""R10 revision: immutable R1 scores, common BB12/FH13, paired injuries.
Run with Anaconda. Only *_r2 files and kontroll.md are written.
"""
import ast,csv,json,hashlib,sys,types,uuid,time
from pathlib import Path
import numpy as np
O=Path(__file__).resolve().parent
protected={str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in O.rglob('*') if p.is_file() and not p.stem.endswith('_r2') and p.name!='kontroll.md'}
source=O/'modell.py';tree=ast.parse(source.read_text())
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ('save','jwrite'):node.body=[ast.Pass()]
mod=types.ModuleType('gw10_r1_readonly');sys.modules[mod.__name__]=mod;ns=mod.__dict__;ns['__file__']=str(source)
exec(compile(ast.fix_missing_locations(tree),str(source)+' [readonly]','exec'),ns)
# Preserve the exact R1 seed algorithm; even transient solver files have _r2 stems.
BaseCBC=ns['pulp'].PULP_CBC_CMD
class RevisionCBC(BaseCBC):
    def create_tmp_files(self,name,*args):
        stem=str(O/(uuid.uuid4().hex+'_'+name+'_r2'))
        return (stem+'.'+ext for ext in args)
ns['pulp'].PULP_CBC_CMD=RevisionCBC
E=ns['E'];ids=ns['ids'];ix=ns['ix'];M=ns['M'];PP=ns['PP'];ORIG=ns['ORIG'];N=ns['N'];H=ns['H'];GWS=ns['GWS'];name=ns['name'];ordered=ns['ordered'];trajectory=ns['trajectory']
MODELS=['codex','repo_hybrid','blend'];BB=12;FH=13

def save(n,rs):
    assert Path(n).stem.endswith('_r2') and rs
    with (O/n).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def jsave(n,obj):
    assert Path(n).stem.endswith('_r2');(O/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
def read(n):return json.loads((O/n).read_text())
def rows(n):return list(csv.DictReader((O/n).open()))
def point(p):return np.array(p['alle_BB'][BB-10])
def labelnames(rr):return name(ix[p] for p in rr)
def pct(v):return f'{100*v:.1f} %'
def pair(v):return f'{v[0]:.2f} / {v[1]:.2f}'

def main():
    start=time.time();draws=200
    # Check every frozen R1 forecast value, including all zero-minute players.
    err=0.
    for fn in ['spillerpoeng.csv','spillerpoeng_R18_R19.csv']:
        for r in rows(fn):
            for m,key in enumerate(MODELS[:2]):err=max(err,abs(float(r[key])-M[m,ix[int(r['id'])],int(r['gw'])-10]))
    assert err<1e-6,'R1 frozen player scores changed'
    original=read('planer.json');initial={k:ordered(ix[p] for p in original['hoved'][k]['rows'][0]['tropp']) for k in ['A','B','C']}
    def swap(out,inc):
        out_ids={next(i for i in ORIG if E[ids[i]]['web_name']==n) for n in out}
        in_ids={ns['named'](n) for n in inc}
        return ordered((set(ORIG)-out_ids)|in_ids)
    initial['Claude_Iwobi']=swap(['Dasilva','Ødegaard'],['Van Hecke','Iwobi'])
    initial['Claude_Evanilson']=swap(['Dasilva','Isak'],['Van Hecke','Evanilson'])
    for s in initial.values():ns['transact'](ORIG,s,ns['SALES'],4)
    for g in range(11,20):ns['TEMPLATES'].extend(ns['seed']([g],model=m) for m in [0,1,2])
    plans={k:trajectory(s,ft0=2,fh=FH,full=True) for k,s in initial.items()}
    nominal=[ns['alternative'](k,p,BB,k) for k,p in plans.items()]
    benchmarks=[]
    for k,s in initial.items():
        lite=trajectory(s,ft0=2,fh=FH)
        benchmarks.append(dict(alternativ=k,full_codex=point(plans[k])[0],lett_codex=point(lite)[0],full_repo=point(plans[k])[1],lett_repo=point(lite)[1],maks_avvik=float(np.abs(point(lite)-point(plans[k])).max())))
    save('simkontroll_r2.csv',benchmarks);save('alternativer_r2.csv',nominal);jsave('planer_r2.json',dict(BB=BB,FH=FH,planer=plans))
    # Check free FH timing from the full R1 grid: same policy for every cell.
    grid=rows('chiprutenett.csv');chip=[];extra_grid=[]
    for k in ['Claude_Iwobi','Claude_Evanilson']:
        for fh in range(11,20):
            q=trajectory(initial[k],ft0=2,fh=fh)
            for bb in GWS:
                if bb==fh:continue
                vals=q['alle_BB'][bb-10]
                extra_grid.append(dict(alternativ=k,BB=bb,FH=fh,codex=vals[0],repo_hybrid=vals[1],blend=np.mean(vals)))
    save('chiprutenett_r2.csv',extra_grid)
    for k,n in [('A',0),('B',1),('C',2),('Claude_Iwobi',None),('Claude_Evanilson',None)]:
        rr=[r for r in grid if int(r['bytter'])==n] if n is not None else [r for r in extra_grid if r['alternativ']==k]
        for model in MODELS:
            best=max(rr,key=lambda r:float(r[model]));now=max([r for r in rr if int(r['BB'])==10],key=lambda r:float(r[model]))
            chip.append(dict(alternativ=k,poengsett=model,beste_BB=int(best['BB']),beste_FH=int(best['FH']),beste_total=float(best[model]),BB10_beste_FH=int(now['FH']),BB10_total=float(now[model]),BB10_minus_best=float(now[model])-float(best[model])))
    assert all(r['BB10_minus_best']<0 for r in chip if r['alternativ'] in ['A','B','C'])
    save('chipkontroll_r2.csv',chip)
    report(plans,nominal,[],[],chip,'A',False,draws)
    print('R2 nominal complete',round(time.time()-start,1),[(k,point(p).round(3).tolist()) for k,p in plans.items()],flush=True)
    # Draw the first 100 worlds exactly as in R1 and append another independent 100.
    # Durations and onset draws are shared across ALL five plans and both models.
    rng=np.random.default_rng(7089878);U0=rng.random((100,H,N));D0=np.array([1,2,3,6],dtype=np.int16)[rng.integers(0,4,size=(100,H,N))]
    U1=rng.random((draws-100,H,N));D1=np.array([1,2,3,6],dtype=np.int16)[rng.integers(0,4,size=(draws-100,H,N))]
    U=np.concatenate([U0,U1]);duration=np.concatenate([D0,D1]);sim=[];comparisons=[];trials=[];choice='A'
    old={(float(r['p']),int(r['trekk']),r['alternativ']):np.array([float(r['codex']),float(r['repo_hybrid'])]) for r in rows('skadetrekk.csv') if int(r['BB'])==BB and r['alternativ'] in ['A','B','C']}
    replay_error=0.
    for prob in [.01,.02]:
        results={k:[] for k in initial}
        for draw in range(draws):
            world=np.zeros((H,N),dtype=np.int16);end=np.zeros(N,dtype=np.int16)
            for t in range(1,H):
                new=(end<=t)&(U[draw,t]<prob);end[new]=t+duration[draw,t,new];world[t]=end
            for k,s in initial.items():
                p=trajectory(s,ft0=2,fh=FH,world=world,record=False);v=point(p);results[k].append([v[0],v[1],v.mean()])
                trials.append(dict(p=prob,verden=draw,alternativ=k,BB=BB,FH=FH,codex=v[0],repo_hybrid=v[1],blend=v.mean()))
                if draw<100 and (prob,draw,k) in old:replay_error=max(replay_error,float(np.abs(v-old[prob,draw,k]).max()))
            if (draw+1)%20==0:print('MC',prob,draw+1,'/',draws,'elapsed',round(time.time()-start),flush=True)
        ref=np.array(results['A'])
        for k,v in results.items():
            a=np.array(v);delta=a-ref
            for m,model in enumerate(MODELS):
                sim.append(dict(p=prob,alternativ=k,poengsett=model,snitt=a[:,m].mean(),p10=np.quantile(a[:,m],.1),p90=np.quantile(a[:,m],.9),snitt_SE=a[:,m].std(ddof=1)/np.sqrt(draws),n=draws))
                comparisons.append(dict(p=prob,alternativ=k,referanse='A',poengsett=model,delta_snitt=delta[:,m].mean(),andel_vinner=(delta[:,m]>1e-9).mean(),p10=np.quantile(delta[:,m],.1),p90=np.quantile(delta[:,m],.9),paret_SE=delta[:,m].std(ddof=1)/np.sqrt(draws),n=draws))
        if prob==.02:choice=max(results,key=lambda k:np.array(results[k])[:,2].mean())
        save('skadetrekk_r2.csv',trials);save('skadesim_r2.csv',sim);save('parvise_r2.csv',comparisons)
        report(plans,nominal,sim,comparisons,chip,choice,False,draws)
    assert replay_error<1e-7,('R1 replay mismatch',replay_error)
    # Add both FT-count sensitivities to the final recommendation at identical chip dates.
    ft=[]
    for ft0 in [1,2,3]:
        for k,s in initial.items():ft.append(ns['alternative'](k,trajectory(s,ft0=ft0,fh=FH,full=True),BB,k))
    save('ft_sensitivitet_r2.csv',ft)
    # Independent reconstruction from frozen player CSV and archived weights.
    by={(int(r['id']),int(r['gw'])):np.array([float(r['codex']),float(r['repo_hybrid'])]) for fn in ['spillerpoeng.csv','spillerpoeng_R18_R19.csv'] for r in rows(fn)}
    scoreerr=0.
    for k,p in plans.items():
        total=np.zeros(2)
        for r in p['rows']:
            weights=r['bb_vekter'] if r['gw']==BB else r['vekter']
            pts=sum((by[pid,r['gw']]*w for pid,w in zip(r['tropp'],weights)),np.zeros(2))-r['trekk'];total+=pts
        scoreerr=max(scoreerr,float(np.abs(total-point(p)).max()))
    assert scoreerr<1e-4
    changed=[n for n,h in protected.items() if hashlib.sha256((O/n).read_bytes()).hexdigest()!=h]
    assert not changed,changed
    jsave('kontroll_r2.json',dict(status='OK',spillerpoeng_uendret=True,maks_spilleravvik=err,maks_planavvik_fra_CSV=scoreerr,maks_replay_avvik=replay_error,R1_filer_uendret=len(protected),verdener_per_rate=draws,BB=BB,FH=FH,valgt=choice))
    report(plans,nominal,sim,comparisons,chip,choice,True,draws)
    print('DONE R2',choice,'elapsed',round(time.time()-start,1),flush=True)


def report(plans,nominal,sim,comparisons,chip,choice,complete,draws):
    p=plans[choice];r=p['rows'][0]
    action='rull begge gratisbyttene' if choice=='A' else 'Dasilva → Van Hecke og Ødegaard → Iwobi' if choice=='Claude_Iwobi' else 'Dasilva → Van Hecke og Isak → Evanilson' if choice=='Claude_Evanilson' else labelnames(r['ut'])+' → '+labelnames(r['inn'])
    lines=['# Kontroll R10 – runde 2',f"**{'Endelig' if complete else 'Foreløpig'} anbefaling: {action}. Ikke Bench Boost nå.** Kaptein **{E[r['kaptein']]['web_name']}**, vise **{E[r['visekaptein']]['web_name']}**. Bank £{r['bank']:.1f}m. BB12/FH13 er planleggingsdatoer; særlig FH revurderes senere.",f"**Ellever:** {labelnames(r['elleve'])}. **Benk:** {labelnames(r['benk'])} (keeper først; deretter utespillerne i prioritert rekkefølge).",'Alle fem planer bruker **BB12/FH13**, FT=2, identiske frosne R1-spillerpoeng, samme adaptive fire-runders byttepolitikk og eksakte autobytter. C er dermed ikke gitt BB11 som i R1-hovedtabellen. Ingen nye minuttantakelser er innført. Valget følger høyest forventning med lik vekt på poengsettene ved 2 % nye fravær; 1 % er følsomhet.', '## Konkrete forslag, uten nye fravær', '| Plan | Ut → inn | Bank | R10 | R10–R13 | R10–R19 |', '|---|---|---:|---:|---:|---:|']
    for z in nominal:lines.append(f"| {z['alternativ']} | {z['ut'] or 'ingen'} → {z['inn'] or 'ingen'} | {z['bank_etter']:.1f} | {pair([z['codex_R10'],z['repo_hybrid_R10']])} | {pair([z['codex_R10_R13'],z['repo_hybrid_R10_R13']])} | {pair([z['codex_R10_R19'],z['repo_hybrid_R10_R19']])} |")
    lines+=['Tallpar = codex / repo_hybrid. Alle fem R10-handlinger er lovlige og uten poengtrekk ved 2 FT. Salgspriser brukes, ikke markedspriser. Iwobi-pakken: £0,4 + 4,0 + 6,7 − 5,0 − 5,4 = £0,7m; Evanilson-pakken: £0,4 + 4,0 + 9,1 − 5,0 − 6,4 = £2,1m. Eksakte kjøpspriser og full bankbane følger av planer_r2.json.', '## Parede skadesimuleringer', f'{draws} felles verdener per rate. Nye fravær fra R11, varighet 1/2/3/6 runder med lik sannsynlighet; fremtidige nye fravær er skjult for byttepolitikken. Fravær rammer også kjøpskandidater. Dette er stressantakelser, ikke medisinsk estimerte rater. De første 100 verdenene gjenskaper R1 nøyaktig.','| Rate | Sett | A snitt | B snitt | C snitt |','|---|---|---:|---:|---:|']
    for prob in [.01,.02]:
        for model in MODELS:
            vals=[next((z['snitt'] for z in sim if z['p']==prob and z['poengsett']==model and z['alternativ']==k),None) for k in ['A','B','C']]
            if all(v is not None for v in vals):lines.append(f"| {prob:.0%} | {model} | {vals[0]:.2f} | {vals[1]:.2f} | {vals[2]:.2f} |")
    lines+=['','| Rate | Sett | B − A | B vinner | Paret p10–p90 | MC-SE |','|---|---|---:|---:|---|---:|']
    for z in comparisons:
        if z['alternativ']=='B':lines.append(f"| {z['p']:.0%} | {z['poengsett']} | {z['delta_snitt']:+.2f} | {pct(z['andel_vinner'])} | {z['p10']:+.2f} til {z['p90']:+.2f} | {z['paret_SE']:.2f} |")
    lines+=['«Vinner» gjelder forventede poeng i skadeverdenen, ikke sannsynlighet for flest faktiske kamppoeng. p10–p90 over er for **paret B−A**. Intervall for selve totalsummene og C−A ligger i skadesim_r2.csv og parvise_r2.csv. Kampflaks og modellfeil er ikke med.','| Alternativ mot A | 1 %: Δ blend [p10, p90] | 2 %: Δ blend [p10, p90] |','|---|---:|---:|']
    for k in ['C','Claude_Iwobi','Claude_Evanilson']:
        values=[]
        for prob in [.01,.02]:
            z=next((z for z in comparisons if z['p']==prob and z['poengsett']=='blend' and z['alternativ']==k),None)
            values.append('pågår' if z is None else f"{z['delta_snitt']:+.2f} [{z['p10']:+.2f}, {z['p90']:+.2f}]")
        lines.append(f"| {k} | {values[0]} | {values[1]} |")
    central=[z for z in sim if z['p']==.02 and z['poengsett']=='blend']
    if central:
        central.sort(key=lambda z:-z['snitt'])
        lines.append(f"Ved 2 % fravær rangeres {central[0]['alternativ']} først, bare {central[0]['snitt']-central[1]['snitt']:.2f} poeng foran {central[1]['alternativ']}. Bytteanbefalingen er derfor svak; poengsettene og fraværsraten betyr mer enn denne marginen. Ingen ekstra skjønnsmessig sparebonus er lagt på A.")
        for key,description in [('Claude_Iwobi','Ødegaard/Dasilva → Iwobi/Van Hecke'),('Claude_Evanilson','Isak/Dasilva → Evanilson/Van Hecke')]:
            z=next(z for z in comparisons if z['p']==.02 and z['poengsett']=='blend' and z['alternativ']==key)
            lines.append(f"Claudes {description}: {z['delta_snitt']:+.2f} mot rull ved 2 % nye fravær. {'Dette gir ingen forventet forbedring i denne stresstesten.' if z['delta_snitt']<=0 else 'Den lille positive forventningen må ses mot intervallet i tabellen.'}")
    lines+=['## BB10 med fritt valgt FH',f'R1s chiprutenett er kontrollert for A/B/C og hvert poengsett; samme rutenett er beregnet for begge Claude-pakkene. Det sammenlignes **beste BB10/FH-kombinasjon** mot beste lovlige BB/FH-kombinasjon; ingen ulovlig dobbeltchip. For valgt handling {choice}:','| Sett | Beste BB / FH | Beste FH med BB10 | BB10 minus beste |','|---|---|---:|---:|']
    for z in chip:
        if z['alternativ']==choice:lines.append(f"| {z['poengsett']} | {z['beste_BB']} / {z['beste_FH']} | {z['BB10_beste_FH']} | {z['BB10_minus_best']:+.2f} |")
    lines+=['BB10 er bak i alle ni tester (A/B/C × codex/repo/blend), også når FH velges fritt. Se chipkontroll_r2.csv. Dette er nominelle prognoser; nye fravær er modellert i A–C-sammenligningen ovenfor.', '## Direkte svar til Claude', '1. **Van Hecke:** spiller-xP kan ikke summeres direkte til laggevinst. Dasilva er billig benkedekning, og gevinsten må betale for finansieringsbyttet og tapet av et spart FT i den fremtidige banen. De to pakkene er nå testet eksplisitt, med akkurat samme chipdatoer og autobytter som rull.', '2. **Isak → Evanilson:** rå repo-xP og minuttskalert hybrid er forskjellige modeller. Å bruke førstnevnte til å foreslå byttet og sistnevnte til å rangere resten er inkonsistent. Claudes tilbaketrekking er rimelig; den komplette pakken vurderes likevel i tabellen, inkludert £2,1m frigjort bank som senere byttepolitikk kan bruke.', '3. **«Alle 15 spiller nå» og BB:** grønne API-flagg er ikke 100 % spillegaranti. Den normale benken gir allerede autobyttedekning; BB-verdien er netto etter dette. Nåværende tilgjengelighet, torsdag/søndag-belastning og Groß-usikkerhet er i R1-prognosen. Senere BB slår BB10 også når FH-datoen er fri.', '4. **Haaland og kalibrering:** 5,39 Codex mot 7,56 observert poeng/runde og 7,44 hybrid er en reell nivåforskjell, men beviser ikke bonusundervurdering. Motstand, xG, minutter og priors er også forskjellige, og to evalueringsrunder gir ikke grunnlag for omkalibrering. Claudes «Haaland i begge poengsett» er for sterkt: Mbeumo har høyere R10 spiller-xP i ren Codex (5,53). Haaland vinner i blandingen og repo; Gabriel er vise i den felles lagplanen.', '5. **FH13:** en foreløpig modellprioritering, ikke en låst handling. Modelldisagreement om FH13/FH16 og fremtidige nyheter er gode grunner til å revurdere datoen senere, men ikke til å legge en vilkårlig informasjonsbonus oppå rull.', '## Kontroll og avgrensning']
    if complete:
        audit=read('kontroll_r2.json');lines.append(f"Fullført: {draws} verdener ved hver av 1 og 2 %, fem planer, samme fravær i begge poengsett. Største avvik mot R1s første 100 verdener: {audit['maks_replay_avvik']:.8f}; totalsummene er også rekonstruert fra frosne spiller-CSV-er og planvekter (avvik <0,0001). {audit['R1_filer_uendret']} eksisterende filer er uendret. Ingen spillerpoeng_r2.csv behøves: prognosen er identisk med R1.")
        ft=rows('ft_sensitivitet_r2.csv');lines.append('FT-følsomhet, uten nye fravær og med samme BB12/FH13:')
        for n in [1,2,3]:
            zz=[z for z in ft if int(z['FT'])==n];win=max(zz,key=lambda z:float(z['codex_R10_R19'])+float(z['repo_hybrid_R10_R19']))
            lines.append(f"- {n} FT: beste nominelle kandidat {win['alternativ']}, {float(win['codex_R10_R19']):.2f} / {float(win['repo_hybrid_R10_R19']):.2f}. Dette er ikke en ny skadesimulering for FT={n}.")
    else:lines.append('Foreløpig rapport. Kjøringen og kontrollen pågår; ingen R1-filer overskrives.')
    lines.append('Kjør `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH` og `python samarbeid/gw10/codex/modell_r2.py`. Avgrenset byttesøk, konstante priser og uavhengige normale spilleutfall som i R1. Hovedhorisont til R19, ikke et bevis for globalt maksimum gjennom R38. Ingen FPL-handlinger eller git-commit utført.')
    body='\n\n'.join(lines)+'\n'
    while '|\n\n|' in body:body=body.replace('|\n\n|','|\n|')
    (O/'kontroll.md').write_text(body)

if __name__=='__main__':main()
