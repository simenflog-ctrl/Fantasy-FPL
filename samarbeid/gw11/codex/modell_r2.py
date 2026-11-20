#!/usr/bin/env python3
"""GW11 orchestration of GW10 candidate search and R2 common-date paired worlds.
No scoring/policy changes. Resumable jobs; each invocation stops after ~8 minutes.
Run: python samarbeid/gw11/codex/modell.py (repeat until status is complete).
--stage report refreshes reports; --stage check independently checks all outputs.
"""
import argparse, hashlib, json, time
from pathlib import Path
import numpy as np
LABEL={0:'A',1:'B',2:'C',3:'D3',4:'D4'}
MODELS=['codex','repo_hybrid','blend']

def run(core):
    global m,O,C,start,deadline
    m=core;O=m.O;C=O/'checkpoints';C.mkdir(exist_ok=True)
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',default='auto',choices=['auto','seeds','candidates','rank','grid','common','final','ft','sim','report','check'])
    parser.add_argument('--seconds',type=int,default=420)
    args=parser.parse_args();start=time.monotonic();deadline=start+min(420,args.seconds)
    assert args.seconds>0
    for f,h in read('prognose_sha256.json').items():assert digest(O/f)==h,('Frozen forecast changed',f)
    if args.stage=='report':report();return
    if args.stage=='check':check();report();return
    stages=[('seeds',seeds),('candidates',candidates),('rank',rank),('grid',grid),('common',common),('final',finalize),('ft',ft_sensitivity),('sim',simulate),('check',check)]
    for stage,fn in stages:
        if args.stage!='auto' and args.stage!=stage:continue
        marker=C/(stage+'.done')
        if marker.exists():continue
        print('STAGE',stage,flush=True)
        complete=fn()
        if complete:
            marker.write_text('OK\n')
            print('STAGE COMPLETE',stage,'elapsed',round(time.monotonic()-start,1),flush=True)
        if not complete or time.monotonic()>=deadline:
            m.jsave('status.json',dict(status='pågår',etappe=stage,etappe_ferdig=bool(complete),sekunder=round(time.monotonic()-start,1)))
            print('Checkpoint saved; repeat same command.',flush=True);return
    m.jsave('status.json',dict(status='fullført' if (C/'check.done').exists() else 'pågår'))
    if (O/'alternativer.csv').exists():report()

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((O/n).read_text())
def write(n,obj):m.jsave(n,obj)
def due():return time.monotonic()>=deadline
def squad(pids):return m.ordered(m.ix[int(p)] for p in pids)
def pids(s):return [m.ids[int(i)] for i in s]
def total(p,bb):return np.array(p['alle_BB'][bb-m.FIRST])
def labelnames(p):return m.name(m.ix[int(i)] for i in p)
def pair(v):return f'{v[0]:.2f} / {v[1]:.2f}'
def load_templates():
    if m.TEMPLATES:return
    m.TEMPLATES.extend(squad(read(f'checkpoints/template_{g}_{model}.json')) for g in range(12,20) for model in range(3))
def path(n,i,ft=3,fh=16,full=False):
    fn=f'checkpoints/path_{n}_{i}_ft{ft}_fh{fh}_full{int(full)}.json'
    if (O/fn).exists():return read(fn)
    load_templates();s=squad(read('sok_kandidater.json')[str(n)][i]);t=time.monotonic()
    p=m.trajectory(s,ft0=ft,fh=fh,full=full);write(fn,p)
    print('Path',n,i,'FT',ft,'FH',fh,'full',int(full),'seconds',round(time.monotonic()-t,2),flush=True)
    return p

def seeds():
    for n in range(1,5):
        for h,cols in enumerate([[11],list(range(11,15)),list(range(11,20))]):
            for model in range(3):
                fn=f'checkpoints/seed_{n}_{h}_{model}.json'
                if not (O/fn).exists():write(fn,pids(m.seed(cols,n,model)))
                if due():return False
    for g in range(12,20):
        for model in range(3):
            fn=f'checkpoints/template_{g}_{model}.json'
            if not (O/fn).exists():write(fn,pids(m.seed([g],model=model)))
            if due():return False
    return True

def candidates():
    cs={0:[m.ORIG]}
    for n in range(1,5):cs[n]=[squad(read(f'checkpoints/seed_{n}_{h}_{model}.json')) for h in range(3) for model in range(3)]
    eligible=m.UI[m.PURCHASE[m.UI,0]]
    pools=[eligible[m.POS[eligible]==k] for k in range(1,5)]
    singles=m.neighbors(m.ORIG,pools,m.SALES,999)
    horizons=[[0],list(range(4)),[t for t in range(m.H) if t!=16-m.FIRST]]
    for pred in [m.M[0],m.M[1],m.BLEND]:
        for cols in horizons:
            ap=m.approx(singles,pred,m.PP,cols,89);cs[1].extend(singles[np.argsort(-ap)[:5]])
    cs[1]=list(np.unique(np.array(cs[1]),axis=0));pairs=[]
    for one in cs[1]:pairs.extend(q for q in m.neighbors(one,pools,m.SALES,999) if len(set(q)-set(m.ORIG))==2)
    pairs=np.unique(np.array(pairs),axis=0)
    for pred in [m.M[0],m.M[1],m.BLEND]:
        for cols in horizons:
            ap=m.approx(pairs,pred,m.PP,cols,89);cs[2].extend(pairs[np.argsort(-ap)[:5]])
    cs={n:list(np.unique(np.array(ss),axis=0)) for n,ss in cs.items()}
    write('sok_kandidater.json',{str(n):[pids(s) for s in ss] for n,ss in cs.items()})
    print('Candidate counts',{n:len(ss) for n,ss in cs.items()},flush=True)
    return True

def rank():
    cs=read('sok_kandidater.json');rr=[];chosen={}
    for n0,ss in cs.items():
        n=int(n0);scores=[]
        for i,s in enumerate(ss):
            p=path(n,i);bb=m.choose_bb(p);score=float(total(p,bb).mean());scores.append(score)
            rr.append(dict(bytter=n,kandidat=i,ut=labelnames(p['rows'][0]['ut']),inn=labelnames(p['rows'][0]['inn']),BB=bb,FH=16,score=score))
            m.save('byttesok.csv',rr)
            if due():return False
        chosen[n0]=int(np.argmax(scores))
    write('forelopige_kandidater.json',chosen);return True

def grid():
    chosen=read('forelopige_kandidater.json');rr=[]
    for n0,i in chosen.items():
        for fh in range(12,20):
            p=path(int(n0),i,fh=fh)
            for bb in m.GWS:
                if bb==fh:continue
                v=total(p,bb);rr.append(dict(alternativ=LABEL[int(n0)],bytter=int(n0),kandidat=i,BB=bb,FH=fh,codex=v[0],repo_hybrid=v[1],blend=v.mean()))
            m.save('chiprutenett_sok.csv',rr)
            if due():return False
    best=max(rr,key=lambda r:r['blend'])
    write('felles_chips.json',dict(BB=best['BB'],FH=best['FH'],valgt_fra=best))
    return True

def common():
    chips=read('felles_chips.json');bb=chips['BB'];fh=chips['FH'];rr=[];chosen={}
    # Re-rank the SAME initial proposal universe at common dates, not own-best BB.
    for n0,ss in read('sok_kandidater.json').items():
        scores=[]
        for i,s in enumerate(ss):
            p=path(int(n0),i,fh=fh,full=True);v=total(p,bb);scores.append(v.mean())
            r=m.alternative(f'{LABEL[int(n0)]}_kandidat{i}',p,bb);r['kandidat']=i;rr.append(r)
            m.save('byttesok_felles.csv',rr)
            if due():return False
        chosen[n0]=int(np.argmax(scores))
    write('valgte_kandidater.json',chosen)
    plans={LABEL[int(n)]:path(int(n),i,fh=fh,full=True) for n,i in chosen.items()}
    write('planer.json',dict(hoved=plans,BB=bb,FH=fh))
    # Mandatory early output before the injury simulation.
    m.save('alternativer.csv',[m.alternative(k,p,bb) for k,p in plans.items()]);report()
    return True

def finalize():
    chosen=read('valgte_kandidater.json');rr=[]
    for n0,i in chosen.items():
        for fh in range(12,20):
            p=path(int(n0),i,fh=fh,full=True)
            for bb in m.GWS:
                if bb==fh:continue
                v=total(p,bb);rr.append(dict(alternativ=LABEL[int(n0)],bytter=int(n0),kandidat=i,BB=bb,FH=fh,codex=v[0],repo_hybrid=v[1],blend=v.mean()))
            m.save('chiprutenett.csv',rr)
            if due():return False
    extras();report();return True

def extras():
    doc=read('planer.json');bb=doc['BB'];fh=doc['FH'];plans=doc['hoved'];choice=recommendation();p=plans[choice]
    chosen=read('valgte_kandidater.json');n=next(n for n,k in LABEL.items() if k==choice);i=chosen[str(n)]
    alts=[m.alternative(k,p,bb) for k,p in plans.items()]
    sims=m.rows(O/'skadesim.csv') if (O/'skadesim.csv').exists() else []
    for r in alts:
        z=next((z for z in sims if float(z['p'])==.02 and z['poengsett']=='blend' and z['alternativ']==r['alternativ']),None)
        if z:r['skade_p10_blend']=float(z['p10']);r['skade_p90_blend']=float(z['p90'])
    # BB sweep keeps FH fixed. Collision is explicitly evaluated with another FH.
    for g in m.GWS:
        if g!=fh:alts.append(m.alternative(f'E_BB{g}',p,g,'E'))
        else:
            entries=[z for z in m.rows(O/'chiprutenett.csv') if z['alternativ']==choice and int(z['BB'])==g]
            best=max(entries,key=lambda z:float(z['blend']));q=path(n,i,fh=int(best['FH']),full=True)
            alts.append(m.alternative(f'E_BB{g}_FH{best["FH"]}',q,g,'E'))
    for f in range(12,20):
        q=path(n,i,fh=f,full=True);alts.append(m.alternative(f'F_FH{f}',q,m.choose_bb(q),'F'))
    r=p['rows'][0];s=squad(r['tropp']);z=m.select(s,m.BLEND[:,0],m.PP[:,0],m.POS,m.LUT,m.PERMS,True,bb==11);caps=[]
    for c in z[2]:
        v=max([j for j in z[2] if j!=c],key=lambda j:m.BLEND[s[j],0]);extra=m.M[:,s[c],0]+(1-m.PP[s[c],0])*m.M[:,s[v],0]
        caps.append((float(extra.mean()),c,v,extra))
    caps.sort(reverse=True);caprows=[]
    for _,c,v,extra in caps[:4]:
        row=m.alternative('G_'+m.E[m.ids[s[c]]]['web_name'],p,bb,'G')
        oldextra=m.M[:,s[z[4]],0]+(1-m.PP[s[z[4]],0])*m.M[:,s[z[5]],0];delta=extra-oldextra
        for model,shift in zip(MODELS[:2],delta):
            for suffix in ['R11','R11_R14','R11_R19']:row[model+'_'+suffix]+=float(shift)
        alts.append(row);caprows.append(dict(id=m.ids[s[c]],navn=m.E[m.ids[s[c]]]['web_name'],vice=m.E[m.ids[s[v]]]['web_name'],codex=m.XP[s[c],0],repo_hybrid=m.REPO[s[c],0],ekstrakopi_codex=extra[0],ekstrakopi_repo=extra[1]))
    m.save('kapteiner.csv',caprows);m.save('alternativer.csv',alts)
    benches=[]
    for k,q in plans.items():
        for r in q['rows']:benches.append(dict(alternativ=k,gw=r['gw'],FH=fh,benk=labelnames(r['benk']),codex_brutto=r['benk_brutto'][0],repo_brutto=r['benk_brutto'][1],codex_BB_netto=r['bb_gevinst'][0],repo_BB_netto=r['bb_gevinst'][1],BB_mulig=r['gw']!=fh))
    m.save('benk_per_runde.csv',benches)

def ft_sensitivity():
    chips=read('felles_chips.json');bb=chips['BB'];fh=chips['FH'];rr=[]
    # Same complete proposal universe at 2/3/4 FT, not just the 3-FT winners.
    for ft in [2,3,4]:
        for n0,ss in read('sok_kandidater.json').items():
            best=None;bestval=-np.inf
            for i,s in enumerate(ss):
                p=path(int(n0),i,ft=ft,fh=fh,full=True);v=total(p,bb).mean()
                if v>bestval:bestval=v;best=m.alternative(LABEL[int(n0)],p,bb);best['kandidat']=i
                if due():return False
            rr.append(best);m.save('ft_sensitivitet.csv',rr)
    report();return True

def recommendation():
    doc=read('planer.json');bb=doc['BB']
    if (C/'sim.done').exists() or (C/'sim_complete.json').exists():
        ss=[r for r in m.rows(O/'skadesim.csv') if float(r['p'])==.02 and r['poengsett']=='blend']
        if ss:return max(ss,key=lambda z:float(z['snitt']))['alternativ']
    return max(doc['hoved'],key=lambda k:total(doc['hoved'][k],bb).mean())

def simulate():
    load_templates();doc=read('planer.json');bb=doc['BB'];fh=doc['FH'];chosen=read('valgte_kandidater.json');cs=read('sok_kandidater.json')
    rngfile=C/'injury_worlds.npz';draws=100
    if not rngfile.exists():
        rng=np.random.default_rng(7089878);U=rng.random((draws,m.H,m.N));dur=np.array([1,2,3,6],dtype=np.int16)[rng.integers(0,4,size=(draws,m.H,m.N))]
        np.savez_compressed(rngfile,U=U,duration=dur)
    raw=np.load(rngfile);U=raw['U'];dur=raw['duration']
    for prob in [.01,.02]:
        for draw in range(draws):
            world=np.zeros((m.H,m.N),dtype=np.int16);end=np.zeros(m.N,dtype=np.int16)
            # Current R11 news is fixed. New injuries start in R12, as in GW10 method.
            for t in range(1,m.H):
                new=(end<=t)&(U[draw,t]<prob);end[new]=t+dur[draw,t,new];world[t]=end
            for n0,i in chosen.items():
                label=LABEL[int(n0)];fn=f'checkpoints/sim_{int(prob*100)}_{draw}_{label}.json'
                if not (O/fn).exists():
                    p=m.trajectory(squad(cs[n0][i]),ft0=3,fh=fh,world=world,record=False);v=total(p,bb)
                    write(fn,dict(p=prob,verden=draw,alternativ=label,BB=bb,FH=fh,codex=v[0],repo_hybrid=v[1],blend=v.mean(),alle_BB=p['alle_BB']))
                if due():summarize_sim();report();return False
            if (draw+1)%5==0:print('MC',prob,draw+1,'/100','elapsed',round(time.monotonic()-start),flush=True)
            if (draw+1)%10==0:summarize_sim();report()
    write('checkpoints/sim_complete.json',dict(verdener=100,rater=[.01,.02]));summarize_sim();extras();report();return True

def summarize_sim():
    trials=[];ss=[];paired=[];chips=[]
    for prob in [.01,.02]:
        common=[d for d in range(100) if all((C/f'sim_{int(prob*100)}_{d}_{k}.json').exists() for k in LABEL.values())]
        if not common:continue
        rr={k:[read(f'checkpoints/sim_{int(prob*100)}_{d}_{k}.json') for d in common] for k in LABEL.values()}
        ref=np.array([[r[z] for z in MODELS] for r in rr['A']])
        for k,rs in rr.items():
            trials.extend({key:value for key,value in r.items() if key!='alle_BB'} for r in rs);a=np.array([[r[z] for z in MODELS] for r in rs]);delta=a-ref
            full=np.array([r['alle_BB'] for r in rs])
            for bb in m.GWS:
                if bb==int(rs[0]['FH']):continue
                v=full[:,bb-m.FIRST,:];d=full[:,0,:]-v
                for j,model in enumerate(MODELS):
                    vv=v[:,j] if j<2 else v.mean(axis=1);dd=d[:,j] if j<2 else d.mean(axis=1)
                    chips.append(dict(p=prob,alternativ=k,BB=bb,FH=int(rs[0]['FH']),poengsett=model,snitt=vv.mean(),BB11_minus=dd.mean(),delta_p10=np.quantile(dd,.1),delta_p90=np.quantile(dd,.9),paret_SE=dd.std(ddof=1)/np.sqrt(len(dd)) if len(dd)>1 else 0,n=len(dd)))
            for j,model in enumerate(MODELS):
                ss.append(dict(p=prob,alternativ=k,poengsett=model,snitt=a[:,j].mean(),p10=np.quantile(a[:,j],.1),p90=np.quantile(a[:,j],.9),snitt_SE=a[:,j].std(ddof=1)/np.sqrt(len(a)) if len(a)>1 else 0,n=len(a)))
                paired.append(dict(p=prob,alternativ=k,referanse='A',poengsett=model,delta_snitt=delta[:,j].mean(),andel_vinner=(delta[:,j]>1e-9).mean(),p10=np.quantile(delta[:,j],.1),p90=np.quantile(delta[:,j],.9),paret_SE=delta[:,j].std(ddof=1)/np.sqrt(len(a)) if len(a)>1 else 0,n=len(a)))
    if trials:m.save('skadetrekk.csv',trials);m.save('skadesim.csv',ss);m.save('parvise.csv',paired);m.save('skadesim_chips.csv',chips)

def report():
    if not (O/'planer.json').exists():return
    doc=read('planer.json');bb=doc['BB'];fh=doc['FH'];plans=doc['hoved'];choice=recommendation();p=plans[choice];r=p['rows'][0]
    complete=(C/'check.done').exists();nominal=max(plans,key=lambda k:total(plans[k],bb).mean());delta=total(p,bb)-total(plans['A'],bb)
    r=dict(r)
    if bb==11:
        s=squad(r['tropp']);z=m.select(s,m.BLEND[:,0],m.PP[:,0],m.POS,m.LUT,m.PERMS,True,True)
        r.update(elleve=pids(s[z[2]]),benk=pids(s[z[3]]),kaptein=m.ids[s[z[4]]],visekaptein=m.ids[s[z[5]]])
    first_points=np.array(p['normal'][0])+(np.array(p['boost'][0]) if bb==11 else 0)
    action='rull gratisbyttene' if not r['ut'] else labelnames(r['ut'])+' → '+labelnames(r['inn'])
    txt=['# Analyse R11, 2026/27',f"Status: {'fullført og kontrollert' if complete else 'foreløpig; se status.json for gjenstående etapper'}. Tallpar er codex / repo_hybrid. Prognosen bygger på frosne data 19. november, ikke senere nyheter.",f"**Anbefaling: {action}.** {'Bench Boost i R11.' if bb==11 else 'Ingen chip i R11.'} Kaptein **{m.E[r['kaptein']]['web_name']}**, visekaptein **{m.E[r['visekaptein']]['web_name']}**. Trekk {r['trekk']} poeng, bank **£{r['bank']:.1f}m**. Felles planleggingsdatoer: **BB{bb}/FH{fh}**.",f"**Ellever:** {labelnames(r['elleve'])}. **Benk:** {labelnames(r['benk'])} (keeper først; de tre utespillerne i prioritert rekkefølge).",f"Nominelt beste alternativ: {nominal}. Anbefalt alternativ {choice} har nominelt {pair(delta)} poeng mot rull, blanding {delta.mean():+.2f}, gjennom R19. Når alle skadeverdener er ferdige følger handlingsvalget høyest 50/50-forventning ved 2 % nye fravær, som i R10s kontrollrunde; 1 % er følsomhet.",'## Verifiserte data og antakelser','API-snapshot 19. november 16:30 UTC: bank £0,4m, salgsverdi £99,5m, alle 15 i egen tropp har status a og tom nyhet. Ingen blanke/doble runder i horisonten. WC1 brukt R9 og TC1 R3; BB1/FH1 utløper R19. Frist lørdag 21. november 11:00 UTC / 12:00 norsk tid. Ingen FPL-handlinger er utført.','FT=3 er antatt, ikke verifisert; 2 og 4 testes. Priser holdes konstante. FH bevarer FT uten +1, som i forrige modell; regelen er fortsatt en antakelse. Andre runder gir +1, maks 5. Nåværende salgspriser brukes ved første salg; senere bytter følger samme prisbokføring som R10.','Minutter: vektede starter R1–R10, historiske minutter per start/innhopp og samme prior. Bare Claudes frosne overstyringer brukes: BHA/BOU/SUN/CRY ×0,95 i R12; Thiago 0,90/74 fra R14; Ødegaard 0,95/82 R11–R12. Ingen europafaktor i R11 og ingen gammel Groß-reduksjon. Alle faktiske antakelser står i minutter_antatt.csv. Jeg har ikke grunnlag for å overstyre disse; de er antakelser, ikke spillgarantier.','Kjøp utelukker status u/n/i/s og 0 %, med den eksplisitt oppgitte Thiago-returen som eneste datofestede unntak fra R14. Thiago kan ikke kjøpes R11–R13. Status d skaleres med API-prosent; øvrige ukjente returdatoer modelleres ikke.','Scoring leses fra bootstrap game_config.scoring, inkludert 10 poeng per keepermål. Repo-hybrid er repoets xP skalert med samme minutter i R11–R16 og Codex i R17–R19. Lik vekt 0,5/0,5. Ingen kalibreringsendring på grunnlag av de tre evalueringsrundene. Begge repo-filer har de oppgitte SHA-256-summene.','## A–D med samme chipdatoer',f'Alle hovedplaner har FT=3, BB{bb}/FH{fh}, samme fire-runders byttepolitikk og eksakte autobytter. Tallene inkluderer alle senere modelltrekk; A betyr rull i R11 og adaptive bytter senere. D4 er fire bytter og −4 nå, og anbefales bare dersom netto forventning er best.','| Plan | Ut → inn | Trekk nå | Bank | R11 | R11–R14 | R11–R19 | Δ blend mot A |','|---|---|---:|---:|---:|---:|---:|---:|']
    for k in sorted(plans,key=lambda k:-total(plans[k],bb).mean()):
        q=plans[k];a=m.alternative(k,q,bb)
        txt.append(f"| {k} | {a['ut'] or 'ingen'} → {a['inn'] or 'ingen'} | {a['poengtrekk_R11']} | {a['bank_etter']:.1f} | {pair([a['codex_R11'],a['repo_hybrid_R11']])} | {pair([a['codex_R11_R14'],a['repo_hybrid_R11_R14']])} | {pair(total(q,bb))} | {total(q,bb).mean()-total(plans['A'],bb).mean():+.2f} |")
    outs=[m.ix[i] for i in r['ut']];ins=[m.ix[i] for i in r['inn']]
    txt+=['## Budsjett og konkret tropp',f"£0,4 + salg £{m.SALES[outs].sum()/10:.1f} − kjøp £{m.COST[ins].sum()/10:.1f} = **£{r['bank']:.1f}m**. Troppen har 2 keepere, 5 forsvarere, 5 midtbanespillere og 3 spisser, maks 3 per klubb.",'| Handling | Spiller | Pris £m |','|---|---|---:|']
    for i in outs:txt.append(f'| Selg | {m.name([i])} | {m.SALES[i]/10:.1f} |')
    for i in ins:txt.append(f'| Kjøp | {m.name([i])} | {m.COST[i]/10:.1f} |')
    txt.append(f"Samme konkrete tropp, ellever, benk, kaptein og vise i begge poengsett gir R11 {pair(first_points)} med valgt chip og autobytter. Ingen modellspesifikk lagseleksjon skjuler forskjellen.")
    txt+=['## Usikkerhet og parede skadesimuleringer','100 felles verdener ved hver av 1 % og 2 % nye fravær per spiller/runde. Nye fravær begynner R12; kjent R11-informasjon holdes fast. Varighet 1/2/3/6 runder med lik sannsynlighet. Samme fravær rammer både eide spillere og kjøpskandidater, i alle planer og begge poengsett. Fremtidige fravær er skjult for den adaptive byttepolitikken. Chipdatoene er forhåndsvalgt og felles.','Dette er stressnivåer, ikke estimerte skaderater. p10–p90 er variasjon i forventede poeng mellom skadeverdener, ikke et prediksjonsintervall for faktiske FPL-poeng. Kampflaks, modellfeil, klubbsjokk og rolleendringer kommer i tillegg.','| Plan mot A | Rate | Δ codex / repo | Δ blend | Paret p10–p90 blend | MC-SE | n |','|---|---:|---:|---:|---|---:|---:|']
    if (O/'parvise.csv').exists():
        pp=m.rows(O/'parvise.csv')
        for prob in [.01,.02]:
            for k in ['B','C','D3','D4']:
                zz=[next((z for z in pp if float(z['p'])==prob and z['alternativ']==k and z['poengsett']==model),None) for model in MODELS]
                if not all(zz):continue
                a,b,c=zz;txt.append(f"| {k} | {prob:.0%} | {float(a['delta_snitt']):+.2f} / {float(b['delta_snitt']):+.2f} | {float(c['delta_snitt']):+.2f} | {float(c['p10']):+.2f} til {float(c['p90']):+.2f} | {float(c['paret_SE']):.2f} | {c['n']} |")
        for prob in [.01,.02]:
            ss=[z for z in m.rows(O/'skadesim.csv') if float(z['p'])==prob and z['poengsett']=='blend']
            if ss:
                ss.sort(key=lambda z:-float(z['snitt']));txt.append(f"Ved {prob:.0%} rangeres {ss[0]['alternativ']} først med {float(ss[0]['snitt']):.2f} forventede poeng, {float(ss[0]['snitt'])-float(ss[1]['snitt']):.2f} foran {ss[1]['alternativ']} ({ss[0]['n']} verdener).")
        txt.append('Totalsummenes p10–p90 finnes i skadesim.csv og alternativer.csv; parede forskjeller og vinnerandeler i parvise.csv. Små forskjeller må vurderes mot både modelluenighet og simuleringens standardfeil.')
    else:txt.append('Skadesimuleringen er ikke ferdig; ingen robusthetskonklusjon trekkes ennå.')
    if (O/'chiprutenett.csv').exists():
        grid=m.rows(O/'chiprutenett.csv');rr=[z for z in grid if z['alternativ']==choice]
        txt+=['## E–F: Bench Boost og Free Hit','| BB | FH i sammenligning | Benk brutto | Netto BB | Total R11–R19 |','|---:|---:|---:|---:|---:|']
        for g in m.GWS:
            same=[z for z in rr if int(z['BB'])==g and int(z['FH'])==fh]
            if not same:same=[z for z in rr if int(z['BB'])==g]
            if not same:continue
            z=max(same,key=lambda z:float(z['blend']));f=int(z['FH']);n=next(n for n,k in LABEL.items() if k==choice);i=read('valgte_kandidater.json')[str(n)]
            fn=f'checkpoints/path_{n}_{i}_ft3_fh{f}_full1.json'
            if not (O/fn).exists():continue
            q=read(fn);row=q['rows'][g-m.FIRST];txt.append(f"| {g} | {f} | {pair(row['benk_brutto'])} | {pair(row['bb_gevinst'])} | {pair([float(z['codex']),float(z['repo_hybrid'])])} |")
        txt+=['BB-gevinsten er netto etter normal autobyttedekning, ikke summen av fire benkespillere. Byttepolitikken er uavhengig av BB-dato og bygger ikke målrettet opp benken. Ved kollisjon med FH flyttes FH eksplisitt i tabellen; hovedalternativene sammenlignes fortsatt med felles datoer.','| FH | Beste lovlige BB | Total R11–R19 |','|---:|---:|---:|']
        for f in range(12,20):
            zs=[z for z in rr if int(z['FH'])==f]
            if zs:
                z=max(zs,key=lambda z:float(z['blend']));txt.append(f"| {f} | {z['BB']} | {pair([float(z['codex']),float(z['repo_hybrid'])])} |")
        for model in MODELS:
            if rr:
                z=max(rr,key=lambda z:float(z[model]));txt.append(f"{model}: beste datoer for denne handlingen BB{z['BB']}/FH{z['FH']} ({float(z[model]):.2f}).")
        txt.append('Datoene velges nominelt fra chiprutenettet før skadesimuleringen. Ved modelluenighet eller små marginer er dette planleggingsdatoer som bør revurderes med neste ukes data.')
    if (O/'skadesim_chips.csv').exists():
        txt+=['BB-følsomhet ved 2 % nye fravær, samme handling og samme FH som hovedplanen:', '| BB | Forventet blend | BB11 minus denne | Paret p10–p90 |', '|---:|---:|---:|---:|']
        for z in m.rows(O/'skadesim_chips.csv'):
            if float(z['p'])==.02 and z['alternativ']==choice and z['poengsett']=='blend':txt.append(f"| {z['BB']} | {float(z['snitt']):.2f} | {float(z['BB11_minus']):+.2f} | {float(z['delta_p10']):+.2f} til {float(z['delta_p90']):+.2f} |")
    if (O/'kapteiner.csv').exists():
        txt+=['## G: kaptein og visekaptein R11','| Kaptein | Vise | Spiller-xP | Ekstrakopi med vise |','|---|---|---:|---:|']
        for z in m.rows(O/'kapteiner.csv'):txt.append(f"| {z['navn']} | {z['vice']} | {pair([float(z['codex']),float(z['repo_hybrid'])])} | {pair([float(z['ekstrakopi_codex']),float(z['ekstrakopi_repo'])])} |")
    txt+=['## Gratisbytter: 2, 3 eller 4','Felles BB/FH beholdes. Hele samme R11-kandidatunivers testes ved hvert FT-antall; tabellen viser beste kandidat. FT får verdi gjennom senere faktiske modellbytter, uten en skjønnsmessig sparebonus.']
    if (O/'ft_sensitivitet.csv').exists():
        txt+=['| FT | Beste plan | Ut → inn | Trekk | R11–R19 |','|---:|---|---|---:|---:|'];rr=m.rows(O/'ft_sensitivitet.csv')
        for ft in [2,3,4]:
            zz=[z for z in rr if int(z['FT'])==ft]
            if len(zz)==5:
                z=max(zz,key=lambda z:float(z['codex_R11_R19'])+float(z['repo_hybrid_R11_R19']));txt.append(f"| {ft} | {z['alternativ']} | {z['ut'] or 'ingen'} → {z['inn'] or 'ingen'} | {z['poengtrekk_R11']} | {pair([float(z['codex_R11_R19']),float(z['repo_hybrid_R11_R19'])])} |")
        txt.append('FT-følsomheten er nominell; skadesimuleringen gjelder 3 FT. Samme tobyttepakke C vinner ved 2, 3 og 4 FT. At 4 FT gir lavere modelltotal enn 3 FT skyldes at den uendrede, heuristiske byttepolitikken velger en annen senere bane; et ekstra gratisbytte har ikke negativ iboende verdi. Dette begrenser presisjonen i langtidsrangeringen. Kontroller tallet i FPL før en plan med tre bytter låses.')
    else:txt.append('FT-følsomhet gjenstår.')
    txt+=['## Nivåkontroll av toppspillere','| Spiller | Observert snitt R1–R10 | Codex R11 | Repo rå R11 | Repo-hybrid R11 | Snitt R11–R16 codex / repo |','|---|---:|---:|---:|---:|---:|']
    for z in m.rows(O/'kalibrering.csv'):txt.append(f"| {z['navn']} | {float(z['observert_snitt_R1_R10']):.2f} | {float(z['codex_R11']):.2f} | {float(z['repo_raw_R11']):.2f} | {float(z['repo_hybrid_R11']):.2f} | {pair([float(z['codex_R11_R16_snitt']),float(z['repo_R11_R16_snitt'])])} |")
    txt+=['Observert snitt er poeng per runde, ikke per opptreden. Modellen bruker xG/xA, historiske priors, motstand og minutter; tidligere poengsnitt er en kontroll, ikke et kalibreringsmål. Bonusmetoden er uendret. Modellenes nivåforskjell er reell modellusikkerhet.','## Metode, avgrensning og gjenskaping','Poengberegning, minuttprior, eksakt integrasjon av uavhengige spilleutfall, lovlige autobytter, kaptein/vice og byttepolitikk er videreført fra R10. Hovedtabellene søker alle lovlige ellevere/benkerekkefølger. Skadeverdener bruker forrige ukes begrensede elleverkandidater med eksakt forventning for hver kandidat.','Først foreslås 1–4 bytter fra heltallsoptimering over én, fire og ni runder, begge poengsett og blandingen; alle lovlige enkeltbytter brukes også til forslag og finansieringspar. Forslagene rangeres på rullerende eierbaner, først FH16, deretter felles chipdatoer. «Beste» betyr beste i dette avgrensede søket, ikke et bevist globalt optimum.','Senere byttesøk: 12 beste + 4 billigste per posisjon, enkeltbytter/finansieringspar, tre forslag vurderes eksakt. Gratisbytte krever >1 poeng over fire runder, med terskel 0 ved 5 FT/R19; betalt bytte krever >5 brutto. FH bruker samme heltallsforslag og lokale forbedring som R10.','Horisonten slutter R19. Det gjør at denne modellen ikke direkte verdsetter tropp og lagrede bytter ved inngangen til R20 eller maksimerer hele R11–R38. En terminalverdi og målrettet oppbygging før BB kunne vært undersøkt senere; ingen slike modellendringer er gjort her.','Kjør med Anaconda: `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH`, så `PYTHONDONTWRITEBYTECODE=1 python samarbeid/gw11/codex/modell.py`. Gjenta til status.json sier fullført. Hver kommando har tidsbudsjett 420 sekunder og lagrer etter hvert delarbeid. `--stage report` oppdaterer rapporten; `--stage check` gjentar kontrollene. Slett checkpoints bare hvis hele beregningen skal kjøres fra bunnen med de samme fryste inputene.','spillerpoeng.csv inneholder alle 672 spillere × 9 runder = 6048 rader. Prognosefilenes SHA-256 kontrolleres mot filene fra 19. november. Alle skrivinger skjer i codex/. Ingen nettverk, installasjon, git eller FPL-handlinger.']
    if (O/'kontroll_r2.json').exists():txt.append('Kontroll: '+json.dumps(read('kontroll_r2.json'),ensure_ascii=False))
    if (O/'kontroll.md').exists():txt.append('Runde 2: se [kontroll.md](kontroll.md) for kritikken av Claude og [bb_skade.csv](bb_skade.csv) for den parede BB11/18/19-testen av A og B med FH12 og FH15.')
    body='\n\n'.join(txt)+'\n'
    while '|\n\n|' in body:body=body.replace('|\n\n|','|\n|')
    (O/'analyse.md').write_text(body)

def check():
    doc=read('planer.json');plans=doc['hoved'];bb=doc['BB'];fh=doc['FH'];m.validate(plans)
    for f,h in read('prognose_sha256.json').items():assert digest(O/f)==h,f
    for f,h in read('input_sha256.json').items():assert digest(O.parent/f)==h,f
    assert len(m.rows(O/'chiprutenett.csv'))==5*8*8
    alts=m.rows(O/'alternativer.csv');assert {r['gruppe'] for r in alts}>=set('ABCDEFG')
    for r in alts:
        if r['alternativ'] in plans:assert (int(r['BB']),int(r['FH']),int(r['FT']))==(bb,fh,3)
    by={(int(r['id']),int(r['gw'])):np.array([float(r['codex']),float(r['repo_hybrid'])]) for r in m.rows(O/'spillerpoeng.csv')}
    err=0.;liteerr=0.
    for k,p in plans.items():
        score=np.zeros(2)
        for r in p['rows']:
            weights=r['bb_vekter'] if r['gw']==bb else r['vekter'];pts=sum((by[pid,r['gw']]*w for pid,w in zip(r['tropp'],weights)),np.zeros(2))-r['trekk'];score+=pts
            for pid in r['inn']:assert m.PURCHASE[m.ix[pid],r['gw']-m.FIRST]
        err=max(err,float(np.abs(score-total(p,bb)).max()))
        s=squad(p['rows'][0]['tropp']);load_templates();q=m.trajectory(s,ft0=3,fh=fh)
        liteerr=max(liteerr,float(np.abs(total(q,bb)-total(p,bb)).max()))
    assert err<1e-4
    sim=m.rows(O/'skadesim.csv');assert len(sim)==30 and all(int(r['n'])==100 for r in sim)
    pairs=m.rows(O/'parvise.csv');assert len(pairs)==30
    trials=m.rows(O/'skadetrekk.csv');assert len(trials)==1000
    assert len({(r['p'],r['verden'],r['alternativ']) for r in trials})==1000
    assert len(m.rows(O/'ft_sensitivitet.csv'))==15
    write('kontroll_r2.json',dict(status='OK',spillerpoeng_uendret=True,spillere=m.N,rader=m.N*m.H,maks_planavvik_fra_CSV=err,maks_full_mot_sim_elleversok=liteerr,verdener_per_rate=100,rater=[.01,.02],planer=5,BB=bb,FH=fh,valgt=recommendation()))
    print('ALL CHECKS OK',read('kontroll_r2.json'),flush=True);return True

if __name__=='__main__':
    import modell
    run(modell)
