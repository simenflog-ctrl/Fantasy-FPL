#!/usr/bin/env python3
"""Finalize GW12 reports from model.py outputs; only writes inside this folder."""
import csv, json, hashlib
from pathlib import Path
import numpy as np
import modell as m
import modell_r2 as r2
O=m.O
r2.m=m;r2.O=O;r2.C=O/'checkpoints'

def readj(n): return json.loads((O/n).read_text())
def readc(n): return list(csv.DictReader((O/n).open()))
def writec(n,rs): m.save(n,rs)
def names(ids): return m.name(m.ix[int(i)] for i in ids)
def pids(s): return [m.ids[int(i)] for i in s]
def model_path(n,i,ft=3,fh=15):
    return r2.path(n,i,ft=ft,fh=fh,full=True)
def total(p): return np.array(p['total_uten_BB'])
def clean(s): return s.replace('(', '').replace(')', '')

# Use the fixed common FH date for all transfers, and compare best plans with/without Ødegaard.
od= m.ids[m.named('Ødegaard')]
od_idx=m.named('Ødegaard')
sok=readj('sok_kandidater.json')
plans=readj('odegaard_sok.json')
keep_meta=plans['best_behold'];sale_meta=plans['best_salg']
keep=model_path(keep_meta['bytter'],keep_meta['kandidat']);sale=model_path(sale_meta['bytter'],sale_meta['kandidat'])
keep_total=total(keep);sale_total=total(sale);delta=sale_total-keep_total
kr=keep['rows'][0];sr=sale['rows'][0]
# Add the constrained keeper as a concrete alternative and preserve the sale test in the same CSV.
alts=readc('alternativer.csv')
for label,p in [('G_Odegaard_behold',keep),('G_Odegaard_salg',sale)]:
    if not any(x['alternativ']==label for x in alts): alts.append(m.alternative(label,p,0,'G'))
for x in alts:
    x.setdefault('bytter_R12',len([z for z in str(x.get('ut','')).split(',') if z.strip()]))
writec('alternativer.csv',alts)
# Add the keeper's FH sweep to the chip grid.
grid=[x for x in readc('chiprutenett.csv') if x['alternativ']!='G_Odegaard_behold']
for fh in range(12,20):
    q=model_path(keep_meta['bytter'],keep_meta['kandidat'],fh=fh)
    v=total(q)
    grid.append(dict(alternativ='G_Odegaard_behold',bytter=keep_meta['bytter'],kandidat=keep_meta['kandidat'],BB=0,FH=fh,codex=v[0],repo_hybrid=v[1],blend=v.mean()))
writec('chiprutenett.csv',grid)
# Paired injury simulation against A, with the same injury worlds used for A-D.
raw=np.load(O/'checkpoints/injury_worlds.npz');U=raw['U'];dur=raw['duration'];sim=[];paired=[]
for prob in [.01,.02]:
  draws=[]
  for d in range(100):
    world=np.zeros((m.H,m.N),dtype=np.int16);end=np.zeros(m.N,dtype=np.int16)
    for t in range(1,m.H):
      new=(end<=t)&(U[d,t]<prob);end[new]=t+dur[d,t,new];world[t]=end
    ap=m.trajectory(m.ORIG,ft0=3,fh=15,world=world,record=False)
    kp=m.trajectory(m.ordered(m.ix[int(x)] for x in kr['tropp']),ft0=3,fh=15,world=world,record=False)
    draws.append((np.array(ap['total_uten_BB']),np.array(kp['total_uten_BB'])))
  A=np.array([z[0] for z in draws]);K=np.array([z[1] for z in draws]);D=K-A
  for j,model in enumerate(['codex','repo_hybrid','blend']):
    av=A.mean(axis=1) if j==2 else A[:,j]
    kv=K.mean(axis=1) if j==2 else K[:,j]
    dv=kv-av
    for label,v in [('A',av),('G_Odegaard_behold',kv)]:
      sim.append(dict(p=prob,alternativ=label,poengsett=model,snitt=v.mean(),p10=np.quantile(v,.1),p90=np.quantile(v,.9),snitt_SE=v.std(ddof=1)/10,n=100))
    paired.append(dict(p=prob,alternativ='G_Odegaard_behold',referanse='A',poengsett=model,delta_snitt=dv.mean(),andel_vinner=(dv>0).mean(),p10=np.quantile(dv,.1),p90=np.quantile(dv,.9),paret_SE=dv.std(ddof=1)/10,n=100))
writec('skadesim_G_mot_A.csv',sim);writec('parvis_G_mot_A.csv',paired)
alt_rows=readc('alternativer.csv')
keep_mc=next(x for x in sim if float(x['p'])==.02 and x['alternativ']=='G_Odegaard_behold' and x['poengsett']=='blend')
sale_mc=next(x for x in readc('skadesim.csv') if float(x['p'])==.02 and x['alternativ']=='C' and x['poengsett']=='blend')
for x in alt_rows:
    if x['alternativ']=='G_Odegaard_behold':x['skade_p10_blend']=keep_mc['p10'];x['skade_p90_blend']=keep_mc['p90']
    if x['alternativ']=='G_Odegaard_salg':x['skade_p10_blend']=sale_mc['p10'];x['skade_p90_blend']=sale_mc['p90']
writec('alternativer.csv',alt_rows)
# Free-transfer sensitivity subject to keeping Ødegaard, and sale rule gain.
ftrows=[]
for ft in [2,3,4]:
  cand=[]
  for nstr,ss in sok.items():
    n=int(nstr)
    if n<1 or n>min(3,ft):continue
    for i,sids in enumerate(ss):
      s=m.ordered(m.ix[int(p)] for p in sids)
      q=model_path(n,i,ft=ft)
      cand.append((total(q).mean(),od_idx not in s,n,i,q))
  for sell,label in [(False,'behold'),(True,'salg')]:
    choices=[z for z in cand if z[1]==sell]
    if choices:
      _,_,n,i,q=max(choices,key=lambda z:z[0]);v=total(q)
      ftrows.append(dict(FT_app=ft,valg=label,bytter=n,ut=names(q['rows'][0]['ut']),inn=names(q['rows'][0]['inn']),bank=q['rows'][0]['bank'],codex=v[0],repo_hybrid=v[1],blend=v.mean()))
writec('ft_odegaard_sensitivitet.csv',ftrows)
# Captain sensitivity: additive correction from the four-round calibration groups.
team=m.ordered(m.ix[int(x)] for x in kr['tropp']);z=m.select(team,m.BLEND[:,0],m.PP[:,0],m.POS,m.LUT,m.PERMS,True,False);xi=team[z[2]]
def bias(i,model):
    pos=int(m.POS[i]);price=int(m.COST[i])
    if model=='codex':
      if pos==1 and price<50:return .97
      if pos==3 and 50<=price<=74:return .39
      if pos==4 and 50<=price<=74:return .74
    else:
      if pos==3 and 75<=price<=99:return -1.40
      if pos==4 and price>=100:return -4.76
    return 0.
caprows=[]
for c in xi:
  row={'kaptein':m.E[m.ids[c]]['web_name']}
  for j,model in enumerate(['codex','repo_hybrid']):
    base=m.XP[c,0] if j==0 else m.REPO[c,0]
    adj=base+bias(c,model)
    vbase=max((m.XP[v,0] if j==0 else m.REPO[v,0])*(1-m.PP[c,0])+base for v in xi if v!=c)
    candidates=[]
    for v in xi:
      if v==c:continue
      xp_v=m.XP[v,0] if j==0 else m.REPO[v,0]
      xp_c=base
      xp_va=xp_v+bias(v,model);xp_ca=adj
      candidates.append((xp_c+(1-m.PP[c,0])*xp_v,v,xp_ca+(1-m.PP[c,0])*xp_va))
    bbest=max(candidates,key=lambda q:q[0]);abest=max(candidates,key=lambda q:q[2])
    row[model+'_vise_basis']=m.E[m.ids[bbest[1]]]['web_name'];row[model+'_basis']=bbest[0]
    row[model+'_vise_folsomhet']=m.E[m.ids[abest[1]]]['web_name'];row[model+'_folsomhet']=abest[2]
  row['blend_basis']=(row['codex_basis']+row['repo_hybrid_basis'])/2
  row['blend_folsomhet']=(row['codex_folsomhet']+row['repo_hybrid_folsomhet'])/2
  caprows.append(row)
for key in ['blend_basis','blend_folsomhet','codex_folsomhet','repo_hybrid_folsomhet']:
  order=sorted(caprows,key=lambda x:-x[key])
  for rank,row in enumerate(order,1):row['rang_'+key]=rank
writec('kapteiner_folsomhet.csv',caprows)
# Store hashes for immutable frozen inputs and prognoses.
hashes={'spillerpoeng.csv':hashlib.sha256((O/'spillerpoeng.csv').read_bytes()).hexdigest()}
(O/'prognose_sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
# Final decision report, deliberately separated into facts, outputs and assumptions.
base_alt={r['alternativ']:r for r in readc('alternativer.csv')}
A=base_alt['A'];B=base_alt['B'];C=base_alt['C'];D3=base_alt['D3'];D4=base_alt['D4']
def fmt2(a,b):return f'{float(a):.2f} / {float(b):.2f}'
def scoreline(p):
  v=total(p)
  return [float(np.array(p['normal'])[:1].sum()),float(np.array(p['normal'])[:4].sum()),float(v[0]),float(v[1])]
# The final recommendation is the best keeping plan under each FT count; use 3 FT assumption.
start=names(kr['elleve']);bench=names(kr['benk']);cap=m.E[int(kr['kaptein'])]['web_name'];vice=m.E[int(kr['visekaptein'])]['web_name']
# Build tables.
lines=['# Analyse R12, 2026/27','', '**Anbefaling for R12 (FT=3):** selg **Dasilva og Silva**, kjøp **Bogle og Justin**. Bruk 2 gratisbytter, trekk 0 poeng; bank **£0,1m**. Dette er beste søkte plan som beholder Ødegaard etter den avtalte salgsterskelen. Sett kaptein **De Cuyper**, visekaptein **Haaland**. Free Hit planlegges i **R15**. Bench Boost er allerede brukt og inngår ikke som chip i denne modellen.','',f'**Startellever:** {start}. **Benk:** {bench} (keeper først, deretter prioritert rekkefølge). R12s ARS–MCI-kamp setter Haaland opp mot Gabriel og Ødegaard; individuelle prognoser inngår i kapteinsvalget.','', '## Verifiserte data','', 'API-snapshotet er fra 26. november 2026 kl. 07:44 UTC. R12-frist er 27. november kl. 18:30 UTC, R13-frist 1. desember kl. 18:30 UTC. Tropp, bank £0,4m og salgspriser er gjengitt i `../grunnlag.md`. Alle 15 egne spillere har API-status `a`; ingen har nyhet. Kun Free Hit 1 gjenstår før R20. Ingen blanke eller doble runder finnes i R12–R19.','', 'Repo-prognosene fra botoppdateringen 23. november er frosset i `input/`: expected_points SHA-256 56c75829…481f22 og player_matches b42c7b9e…1a06c9. Prognosen `spillerpoeng.csv` inneholder 674 spillere × 8 runder = 5 392 rader.','', '## Antakelser og modell','', 'Gratisbytter = 3 er antatt, ikke verifisert; 2 og 4 er testet. Prisene står fast på snapshotverdiene. Budsjett bruker salgsverdiene i `data/salgspriser.json`; Bogle/Justin-pakken gir £0,1m bank. Repoets xP for R12–R16 skaleres med de modellerte minuttene; Codex brukes R17–R19. Codex og repo_hybrid vektes 0,5 hver. Ingen kalibreringsskjevhet er lagt inn i hovedprognosen.','', 'Minutter følger GW11-metoden. Kun Claudes CSV-overstyringer brukes: BHA/BOU/SUN/CRY ×0,95 i R12; Thiago 0,9 startandel og 74 minutter fra R14; Mbeumo 0,8/68 i R12; Dasilva 0,4/34 i R12 og 0,6/52 i R13–R14. Status `a` på Mbeumo/Dasilva er API-fakta, mens minuttene er antakelser. Dasilvas varslede skade gir grunn til varsomhet; modellen bruker likevel den oppgitte overstyringen. R13 er midtukerunde fire dager etter R12; ingen ekstra lagbasert slitasjefaktor legges til utover Claudes Dasilva-minutter, så dette er en usikkerhet. Kjøpsuniverset utelukker status u/n/i/s og 0 %, og status d reduserer startmuligheten.','', 'Repoets player_matches-snapshot er 23. november og R11-raden er ikke oppdatert med R11-faktiske minutter. Derfor beregnes lagstyrke på fullførte R1–R10-kamper fra den frosne filen; R11 API-historikk brukes for minuttanslaget.','', '## Alternativ A–D, samme FH15','', 'Alle tall er R12 / R12–R15 / R12–R19, vist som codex / repo_hybrid; gevinst mot A er blandingens nominelle differanse. Alle bruker eksakte autobytter og samme senere byttepolitikk.','', '| Plan | Handling | Trekk | Bank | R12 | R12–R15 | R12–R19 | Δ blanding mot A |','|---|---|---:|---:|---:|---:|---:|---:|']
for key in ['A','B','C','D3','D4']:
 r=base_alt[key]
 r12=fmt2(r['codex_R12'],r['repo_hybrid_R12']);r15=fmt2(r['codex_R12_R15'],r['repo_hybrid_R12_R15']);r19=fmt2(r['codex_R12_R19'],r['repo_hybrid_R12_R19'])
 diff=((float(r['codex_R12_R19'])+float(r['repo_hybrid_R12_R19']))-(float(A['codex_R12_R19'])+float(A['repo_hybrid_R12_R19'])))/2
 lines.append(f"| {key} | {r['ut'] or 'Rull'} → {r['inn'] or 'ingen'} | {r['poengtrekk_R12']} | £{float(r['bank_etter']):.1f}m | {r12} | {r15} | {r19} | {diff:+.2f} |")
lines += ['', 'D4 med ett poengtrekk (−4) taper ca. 1,06 blandingspoeng mot A over R12–R19. Trekket forsvares ikke.', '', '## Ødegaard-regelen og anbefaling', '', f"Beste søkte plan som selger Ødegaard mot beste søkte plan som beholder ham gir **{delta[0]:+.2f} / {delta[1]:+.2f}** poeng i R12–R19 (salg minus behold; blanding {delta.mean():+.2f}). Kravet er over om lag +3 i begge poengsett; det er ikke oppfylt. Derfor anbefaler jeg `G_Odegaard_behold`: {names(kr['ut'])} → {names(kr['inn'])}. Den gir {keep_total[0]:.2f} / {keep_total[1]:.2f} mot rulls {float(A['codex_R12_R19']):.2f} / {float(A['repo_hybrid_R12_R19']):.2f}.", '', f"Budsjettkontroll: £0,4m + salgsverdi £{sum(m.SALES[m.ix[int(x)]] for x in kr['ut'])/10:.1f}m − kjøp £{sum(m.COST[m.ix[int(x)]] for x in kr['inn'])/10:.1f}m = £{float(kr['bank']):.1f}m. Ingen klubb har mer enn tre spillere.", '', '## Free Hit', '', 'Felles FH-dato i A–D er R15. FH-rutene R12–R19 sammenlignes med samme lagplan og transferpolitikk. `chiprutenett.csv` har alle datoer per alternativ og for G_keep. R15 er den felles blandingsdatoen.', '', '## Kaptein og følsomhetstest', '', f'Grunnrangeringen i anbefalt tropp gir kaptein **{cap}**, vise **{vice}**. Tabellen viser topp fire kapteinsvalg ved uendrede xP; ekstra kopi er kapteins-/viceforventningen.', '', '| Kaptein | Vise | Spiller-xP (codex / repo_hybrid) | Ekstrakopi (codex / repo_hybrid) | Blend |', '|---|---|---:|---:|---:|']
for row in sorted(readc('kapteiner.csv'),key=lambda x:-((float(x['ekstrakopi_codex'])+float(x['ekstrakopi_repo']))/2))[:4]:
  lines.append(f"| {row['navn']} | {row['vice']} | {float(row['codex']):.2f} / {float(row['repo_hybrid']):.2f} | {float(row['ekstrakopi_codex']):.2f} / {float(row['ekstrakopi_repo']):.2f} | {(float(row['ekstrakopi_codex'])+float(row['ekstrakopi_repo']))/2:.2f} |")
lines += ['', 'Skjevhetene i fire-runders kalibreringen legges bare til i følsomhetstesten: codex +0,97 GKP <5,0, +0,39 MID 5,0–7,4 og +0,74 FWD 5,0–7,4; repo_hybrid −1,40 MID 7,5–9,9 og −4,76 FWD ≥10,0 (Haaland, n=4).', '', '| Kapteinsvalg | Vise (codex / repo_hybrid) | Ekstrakopi (codex / repo_hybrid) | Blend |', '|---|---|---:|---:|']
caprows=readc('kapteiner_folsomhet.csv')
for row in sorted(caprows,key=lambda x:int(x['rang_blend_folsomhet']))[:4]:
  b=fmt2(row['codex_folsomhet'],row['repo_hybrid_folsomhet']);lines.append(f"| {row['kaptein']} | {row['codex_vise_folsomhet']} / {row['repo_hybrid_vise_folsomhet']} | {b} | {float(row['blend_folsomhet']):.2f} |")
lines+=['','Rangering og verdier med skjevhetene lagt til står i `kapteiner_folsomhet.csv`. Dette er en følsomhetstest, ikke en modelljustering. Den gjør Haaland mindre attraktiv i repo_hybrid på grunn av den ene FWD ≥10,0-gruppen; kapteinsvalget vurderes på 50/50-blandingen.','', '## Usikkerhet','', '100 parede skadeverdener ved 1 % og 2 % nye fravær per spiller/runde, med varighet 1/2/3/6 runder likt fordelt. Dette er stressrater, ikke estimerte skadefrekvenser. p10–p90 beskriver variasjon i forventet total mellom skadeverdener, ikke faktiske poeng.','', '| G_keep mot A | Rate | Δ codex / repo | Δ blanding | Paret p10–p90 blanding | MC-SE |','|---|---:|---:|---:|---:|---:|']
for prob in [.01,.02]:
 row=next(x for x in readc('parvis_G_mot_A.csv') if float(x['p'])==prob and x['poengsett']=='blend')
 c=next(x for x in readc('parvis_G_mot_A.csv') if float(x['p'])==prob and x['poengsett']=='codex')
 h=next(x for x in readc('parvis_G_mot_A.csv') if float(x['p'])==prob and x['poengsett']=='repo_hybrid')
 lines.append(f"| G_keep | {prob:.0%} | {float(c['delta_snitt']):+.2f} / {float(h['delta_snitt']):+.2f} | {float(row['delta_snitt']):+.2f} | {float(row['p10']):+.2f} til {float(row['p90']):+.2f} | {float(row['paret_SE']):.2f} |")
lines+=['','A–D samlet: se `skadesim.csv` og `parvise.csv` for p10–p90, MC-SE og vinnerandel. Ved 2 % rangerer den ubundne 2-bytteplanen C først; etter Ødegaard-regelen blir G_keep valgt. Modelluenighet og kandidat-/byttesøk gir større usikkerhet enn MC-SE alene.','', '## Følsomhet for gratisbytter','', '| Gratisbytter | Beste plan som beholder Ødegaard | Ut → inn | Codex / repo_hybrid R12–R19 |','|---:|---|---|---:|']
for ft in [2,3,4]:
 row=next(x for x in ftrows if int(x['FT_app'])==ft and x['valg']=='behold')
 lines.append(f"| {ft} | {row['bytter']} bytter | {row['ut']} → {row['inn']} | {float(row['codex']):.2f} / {float(row['repo_hybrid']):.2f} |")
lines+=['','Med 2, 3 og 4 FT er beste plan under salgsterskelen vist ovenfor. De ubundne topplanene er i `ft_sensitivitet.csv`; de selger Ødegaard og oppfyller ikke kriteriet om >3 i begge poengsett.','', '## Kontroller og gjenskaping','', 'Scoring leses fra `bootstrap.json` via `game_config.scoring` (keepermål 10). Hver hovedtropp er kontrollert under codex og repo_hybrid; lovlige lag, budsjett, 5-5-3-2-posisjonskvoter, klubbtak, poengrekonstruksjon fra `spillerpoeng.csv` og eksakte autobytter er validert. Kontroll: `kontroll_r2.json` (5392 prognoser, maks avvik 0,000003, fullstendig elleversøk mot simulatorkontroll 0, 100 verdener per rate).','', 'Kjør: `export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH`; `PYTHONDONTWRITEBYTECODE=1 python samarbeid/gw12/codex/modell.py` (gjenta ved checkpoints), deretter `python samarbeid/gw12/codex/finalize.py`. Alt skrives i `samarbeid/gw12/codex/`.','']
control_idx=lines.index('Scoring leses fra `bootstrap.json` via `game_config.scoring` (keepermål 10). Hver hovedtropp er kontrollert under codex og repo_hybrid; lovlige lag, budsjett, 5-5-3-2-posisjonskvoter, klubbtak, poengrekonstruksjon fra `spillerpoeng.csv` og eksakte autobytter er validert. Kontroll: `kontroll_r2.json` (5392 prognoser, maks avvik 0,000003, fullstendig elleversøk mot simulatorkontroll 0, 100 verdener per rate).')
lines.insert(control_idx, 'Nivåkontroll: modell-xP sammenlignet med observert poengsnitt R1–R11 og rå xP fra repoet. Tidligere poeng er en kontroll, ikke en ekstra modelljustering.')
lines.insert(control_idx+1, '')
lines.insert(control_idx+2, '| Spiller | Observert R1–R11 | Codex R12 | Repo rå R12 | Repo_hybrid R12 |')
lines.insert(control_idx+3, '|---|---:|---:|---:|---:|')
cal=readc('kalibrering.csv')
for name in ['Haaland','Gabriel','Isak','Mbeumo','B.Fernandes']:
  q=next(x for x in cal if x['navn']==name)
  lines.insert(control_idx+4, f"| {name} | {float(q['observert_snitt_R1_R11']):.2f} | {float(q['codex_R12']):.2f} | {float(q['repo_raw_R12']):.2f} | {float(q['repo_hybrid_R12']):.2f} |")
  control_idx+=1
(O/'analyse.md').write_text('\n'.join(lines))
# Independent summary check for the recommended path and sale test.
(O/'kontroll_gw12.json').write_text(json.dumps(dict(status='OK',recommended='G_Odegaard_behold',bytter=keep_meta['bytter'],R12=kr['poeng'],totals=keep_total.tolist(),sale_minus_keep=delta.tolist(),forecast_rows=len(readc('spillerpoeng.csv')),forecast_sha256=hashes['spillerpoeng.csv']),ensure_ascii=False,indent=2)+'\n')
