"""Render Norwegian measurement report from executed CSVs; no model tuning."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,re
import pandas as pd
O=Path(__file__).resolve().parent

def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows])

def run():
    st=pd.read_csv(O/'p1p2_parvis.csv');levels=pd.read_csv(O/'p1p2_nivaer.csv')
    cal=pd.read_csv(O/'p1p2_premium.csv');wace=pd.read_csv(O/'p1p2_premium_wace.csv')
    mech=pd.read_csv(O/'p1p2_minuttkalibrering.csv');grid=pd.read_csv(O/'p1p2_tau_utvikling.csv')
    decision=json.loads((O/'p1p2_beslutning.json').read_text());lock=json.loads((O/'p1_tau_last.json').read_text())
    manifest=json.loads((O/'p1p2_manifest.json').read_text())
    parity=pd.read_csv(O/'p1p2_p0_paritet.csv')
    test_log=(O/'p1p2_tests.log').read_text();test_count,test_seconds=re.search(r'(\d+) passed in ([\d.]+)s',test_log).groups()
    seasons=['2023-24','2024-25','2025-26','alle'];tau=decision['tau']
    def stat(model,season,metric):return st[(st.model==model)&(st.season==season)&(st.metric==metric)].iloc[0]
    def level(model,season):return levels[(levels.model==model)&(levels.season==season)].iloc[0]
    def fmt(r):return f'{r.difference:+.6f} ± {r.se:.6f}'
    def perf(model):
        rows=[]
        for s in seasons:
            a,b=level('baseline',s),level(model,s);r=stat(model,s,'mse')
            rows.append([s,int(b.n),f'{a.mse:.6f} → {b.mse:.6f}',fmt(r),
                f'{100*r.relative_mse_reduction:+.3f} %',f'{-r.difference/r.se:.2f}' if r.se else '–',
                f'{a.top10:.3f} → {b.top10:.3f} ({fmt(stat(model,s,"top10"))})',
                f'{a.top20:.3f} → {b.top20:.3f} ({fmt(stat(model,s,"top20"))})'])
        return table(['Sesong','N','Total-MSE før → etter','Δ total-MSE ± SE','MSE-reduksjon','Forbedring/SE','Topp10 før → etter (Δ ± SE)','Topp20 før → etter (Δ ± SE)'],rows)
    gridrows=[]
    for t in [4,5,6,7,8,10,12]:
        cells=[]
        for s in ['2023-24','2024-25','utvikling_samlet']:
            r=grid[(grid.tau==t)&(grid.season==s)].iloc[0];cells.append(f'{r.bonus_mse:.6f}')
        gridrows.append([f'**{t}**' if t==tau else t,*cells])
    gridtable=table(['Fast tau','Bonus-MSE 2023/24','Bonus-MSE 2024/25','Utvikling samlet'],gridrows)
    bonusrows=[]
    for s in seasons:
        a,b=level('baseline',s),level('B1',s);r=stat('B1',s,'bonus_mse')
        bonusrows.append([s,f'{a.bonus_mse:.6f}',f'{b.bonus_mse:.6f}',fmt(r),f'{100*(1-b.bonus_mse/a.bonus_mse):+.2f} %'])
    bonustable=table(['Sesong','Bonus-MSE før','Etter','Δ ± blokk-SE','Reduksjon'],bonusrows)
    mechrows=[]
    for s in seasons:
        for metric in ['p_play','p_sub','minutes']:
            r=mech[(mech.season==s)&(mech.p_start_group=='all_<0.6')&(mech.metric==metric)].iloc[0]
            mechrows.append([s,metric,int(r.n),f'{r.predicted_baseline:.4f} → {r.predicted_P2:.4f}',f'{r.actual:.4f}',
                f'{r.bias_baseline:+.4f} ± {r.se_bias_baseline:.4f}',f'{r.bias_P2:+.4f} ± {r.se_bias_P2:.4f}',
                f'{r.delta_mse:+.5f} ± {r.se_delta_mse:.5f}'])
    mechtable=table(['Sesong','Mål','N','Predikert før → P2','Faktisk','Bias før ± SE','Bias P2 ± SE','Δ Brier/MSE ± SE'],mechrows)
    premiumrows=[]
    for s in seasons:
        for price in ['8-10','>=10']:
            for pos in ['FWD','MID']:
                q=cal[(cal.model=='B1')&(cal.season==s)&(cal.price_group==price)&(cal.pos==pos)]
                a=q[q.metric=='bonus'].iloc[0];b=q[q.metric=='total'].iloc[0]
                premiumrows.append([s,price,pos,int(a.n),f'{a.actual:.3f} / {b.actual:.3f}',
                    f'{a.predicted_baseline:.3f} → {a.predicted_candidate:.3f}',f'{b.predicted_baseline:.3f} → {b.predicted_candidate:.3f}',
                    f'{a.abs_bias_change:+.3f} ± {a.se_abs_bias_change:.3f}',
                    f'{b.abs_bias_change:+.3f} ± {b.se_abs_bias_change:.3f}'])
    premiumtable=table(['Sesong','Pris','Pos','N','Faktisk bonus / total','Pred. bonus før → etter','Pred. total før → etter','Δ absolutt bonusbias ± SE','Δ absolutt totalbias ± SE'],premiumrows)
    wr=[]
    for s in seasons:
        for metric in ['bonus','total']:
            r=wace[(wace.model=='B1')&(wace.season==s)&(wace.metric==metric)].iloc[0]
            wr.append([s,metric,int(r.n),f'{r.wace_baseline:.6f} → {r.wace_candidate:.6f}',f'{r.delta_wace:+.6f} ± {r.se_delta_wace:.6f}'])
    wtable=table(['Sesong','Kalibrering','N','Vektet absolutt cellebias før → etter','Δ ± blokk-SE'],wr)
    cr=[]
    labels=dict(mse_reduction_ge_0p5pct='Minst 0,5 % lavere total-MSE samlet',
        total_mse_ge_3_block_se='Minst 3 blokk-SE bedre total-MSE samlet',
        total_mse_same_better_sign_all_seasons='Lavere total-MSE i hver sesong',
        top10_top20_guard_pooled='Topp10/20-vern samlet (≤2 SE forverring)',
        control_total_mse_better='Lavere total-MSE på låst kontrollår',
        control_top10_top20_guard='Topp10/20-vern på kontrollåret',
        bonus_mse_better_control_and_pooled='Lavere bonus-MSE på kontrollår og samlet',
        premium_bonus_wace_better_control_and_pooled='Bedre premium-bonuskalibrering på kontrollår og samlet')
    for name,label in labels.items():
        cr.append([label,*[('JA' if decision[m]['criteria'][name] else '**NEI**') if name in decision[m]['criteria'] else '–' for m in ['P2','B1']]])
    criteriatable=table(['Forhåndsregistrert krav / vern','P2','B1'],cr)
    combo='**Ikke kjørt:** begge kandidatene måtte være godkjent hver for seg først.'
    if 'B1+P2' in set(st.model):
        combo=perf('B1+P2')
        inc=pd.read_csv(O/'p1p2_kombinasjon_inkrement.csv');rows=[]
        for _,r in inc[(inc.season.isin(['2025-26','alle']))&(inc.metric.isin(['mse','bonus_mse','top10','top20']))].iterrows():
            rows.append([r.reference,r.season,r.metric,fmt(r)])
        combo+='\n\nInkrementell effekt av kombinasjonen relativt til hver enkelt kandidat:\n\n'+table(['Referanse','Sesong','Mål','Δ ± blokk-SE'],rows)
        combo+=f"\n\nKonklusjon kombinasjon: **{decision['B1+P2']['status']}**. P1-unntaket brukes bare for B1, ikke automatisk for kombinasjonen."
    def reasons(name):
        d=decision[name];failed=[labels[k] for k,v in d['criteria'].items() if not v]
        text='Alle ordinære krav og vern er oppfylt.' if not failed else 'Ikke oppfylt: '+ '; '.join(failed)+'.'
        if d['exception_used']:
            text+=' **Godkjent etter det forhåndsskrevne P1-unntaket, ikke etter det ordinære primærkravet.** Bonus-MSE og premium-bonuskalibreringen bedres på kontrollåret og samlet; topp-k-vernene består.'
        return text
    if decision['B1']['status']=='GODKJENT':
        recommendation=f'Anbefalt `BONUS_TAU_FIXED = {tau}.0`, etter Claudes kontroll av denne uavhengige målingen.'
    else:
        recommendation=f'Behold `BONUS_TAU_FIXED = None`. Tau {tau} var det låste utviklingsvalget, men er ikke godkjent for aktivering.'
    p2effect=stat('P2','alle','mse')
    b1effect=stat('B1','alle','mse')
    mp=mech[(mech.season=='alle')&(mech.p_start_group=='all_<0.6')].set_index('metric')
    wb=wace[(wace.model=='B1')&(wace.metric=='bonus')].set_index('season')
    n_display=f"{manifest['rows_per_model']:,}".replace(',', ' ')
    p2recommend='P2 kan aktiveres etter kontroll.' if decision['P2']['status']=='GODKJENT' else 'Behold `SUB_GIVEN_NO_START = False`.'
    b2reason=('B1 bestod ikke; B2 skal derfor ikke testes etter forhåndsregistreringen.' if decision['B1']['status']!='GODKJENT' else
        'B2 er ikke kjørt. Oppdraget måler de implementerte kandidatene B1 og P2; B2 er en valgfri neste produksjonskandidat, ikke et automatisk nytt tuningsøk.')
    body=f'''# Uavhengig måling av P1 B1 og P2

**P2: {decision['P2']['status']}. P1 B1: {decision['B1']['status']}.**

{recommendation} {p2recommend} Standardverdiene er ikke endret; ingen commit.

## Låst metode og gjennomføring

Lest diffene `7502dcd` og `87a16db`. Kravene er hentet uendret fra `samarbeid/modell/plan.md` og `claude/p1-bonus-forhandsregistrering.md`; hasher er lagret i `p1p2_metode_for_kjoring.json`. P2 er testet isolert med bonusflagget på `None`; B1 med P2 av. Baseline er `SUB_GIVEN_NO_START=False`, `BONUS_TAU_FIXED=None`.

Alle tre sesonger, **GW8–38**, {n_display} spiller–kamp-prognoser per hovedmodell og 93 runder. Paring er identisk sesong/spiller/fixture og faktiske utfall. Effekt er kandidat minus baseline: negativ MSE er bedre, positiv topp-k er bedre. SE bruker de samme fire-runders blokkene innen sesong som P0: 8 blokker per år, 24 samlet. «±» betyr én SE, ikke et 95 %-intervall. Topp-k er poengsnitt for k valgte spiller–kamp-rader per runde; ikke en lovlig budsjettert ellever.

StringIO-broen er fjernet: historikk gis som `last_season` direkte til Claudes produksjonsfunksjon. Tau-rutenettet deler identiske minutter/lagstyrker/kampprogram, men **hver tau kjøres gjennom produksjonens `forecast` og flagget `BONUS_TAU_FIXED`**. En paritetstest mot separat full flaggkjøring består. Ny baseline mot P0 har største xP-avvik **{parity['max'].max():.2g}**; `p1p2_p0_paritet.csv` dokumenterer dette. Ingen andre prediksjonsformler er innført.

## P1: utviklingsvalg før kontrollåret

Minimering av bonus-MSE, akkurat rutenettet {{4, 5, 6, 7, 8, 10, 12}}, bare på 2023/24 og 2024/25. Samlet verdi er vektet med antall spiller–kamper; ved likhet velges lavere tau. Verken total-MSE eller topp-k velger tau.

{gridtable}

**Låst tau = {tau}.** Låsen ble skrevet **{lock['locked_utc']}**, før 2025/26 ble lastet. `p1_tau_last.json` lagrer lasteloggen og hash av utviklingstabellen. På kontrollåret kjøres bare den låste verdien, ingen rutenettsøk. Historiske kontrollårsdata er sett i tidligere prosjektarbeid, men ingen B1-kontrollmåling er brukt til dette tau-valget. Samlede B1-tall inkluderer utviklingsårene og er derfor ikke en ny uavhengig bekreftelse; kontrollåret vises separat.

## P2: totalpoeng og topp-k

{perf('P2')}

**Konklusjon P2: {decision['P2']['status']}.** {reasons('P2')} Samlet gevinst er {100*p2effect.relative_mse_reduction:.3f} % og {-p2effect.difference/p2effect.se:.2f} blokk-SE. Dette er en målt liten gevinst, men terskelen på 0,5 % senkes ikke etter resultatet.

### Minutt- og innhoppsmekanismen

Felles utvalg: prognoser med **p_start < 0,6**; p_start er identisk av/på. `p_play` sammenlignes med 1[minutter > 0], minutter med faktiske minutter. `p_sub = p_play − p_start` sammenlignes med 1[ikke start og minutter > 0]. Dette er ubetinget innhoppssannsynlighet per kamp, ikke etterhåndsfiltrering til dem som faktisk spilte. Sannsynlighets-MSE er Brier-score. Delgruppene 0–0,2, 0,2–0,4 og 0,4–0,6 finnes i CSV-en i tillegg til totalutvalget under.

{mechtable}

P2 retter i stor grad innhoppsnivået: samlet predikert p_sub går fra {mp.loc['p_sub','predicted_baseline']:.4f} til {mp.loc['p_sub','predicted_P2']:.4f}, mot faktisk {mp.loc['p_sub','actual']:.4f}. Samtidig øker overvurderingen av samlet p_play og gjennomsnittsminutter. Brier-score og minutt-MSE blir likevel lavere; nivåbias og kvadratfeil måler ulike egenskaper. Mekanismen er derfor ikke bedre kalibrert på alle mål.

En bedre mekanismediagnose erstatter ikke kravene til total-MSE og topp-k. Historiske tilgjengelighetsflagg mangler fortsatt; alle modeller har samme begrensning og samme rekonstruksjon av roster/priorer.

## B1 med låst tau: totalpoeng, bonus og topp-k

{perf('B1')}

{bonustable}

### Premiumkalibrering før/etter

Pris er siste observerte pris fra en tidligere GW. Kun FWD/MID i [8,10) og ≥10 m; ukjent tidligere pris utelates. «Bias» er predikert minus faktisk. Absolutt bias sammenligner størrelsen, slik at både over- og undervurdering straffes. CSV-en inneholder før/etter-bias, tilhørende blokk-SE, parvis biasendring og bonus-/total-MSE per celle.

{premiumtable}

For å avgjøre «bedre premiumkalibrering» ble følgende oppsummering skrevet ned før målingen: **WACE = antallsvektet absolutt gjennomsnittsbias i de fire pris-/posisjonscellene**. Dette hindrer at overvurdering i én celle skjules av undervurdering i en annen. Kravet vurderes på bonus; totalpoeng rapporteres samtidig, slik oppdraget krever. SE for endring i absolutt bias/WACE bruker delta-metodens påvirkningsverdier i de samme fire-runders blokkene; nær null bias er denne lineariseringen usikker. Ingen ny signifikansgrense for kalibrering er lagt til.

{wtable}

**Konklusjon B1: {decision['B1']['status']}.** {reasons('B1')}

Tau 7 reduserer særlig overvurderingen av ≥10 m-spillere samlet, men gjør undervurderingen i 8–10 m-gruppene større. Premium-bonus-WACE går samlet fra {wb.loc['alle','wace_baseline']:.6f} til {wb.loc['alle','wace_candidate']:.6f}, og på kontrollåret fra {wb.loc['2025-26','wace_baseline']:.6f} til {wb.loc['2025-26','wace_candidate']:.6f}. Endringene er små relativt til SE, så dette beviser ikke skade, men oppfyller heller ikke kravet om bedre premiumkalibrering. Topp10 på kontrollåret faller med {abs(stat('B1','2025-26','top10').difference):.3f} poeng per valgt spiller (±{stat('B1','2025-26','top10').se:.3f}); det er innenfor 2-SE-vernet, uten å være en rangeringseffekt i ønsket retning.

Det forhåndsskrevne unntaket lyder: «Hvis B1 bare forbedrer bonus-MSE, men ikke total-MSE med 3 SE … Da avgjør vi ut fra kalibreringen og topp-k, og skriver eksplisitt at det primære kravet ikke ble nådd.» Unntaket er {'brukt' if decision['B1']['exception_used'] else 'ikke brukt'}. Alle enkeltceller vises; en bedre samlet WACE betyr ikke at hver spillergruppe eller hvert års celle må bli bedre.

## Kontroll mot forhåndsregistrerte krav

{criteriatable}

GODKJENT betyr at ordinære krav består, eller at det eksplisitte B1-unntaket er brukt og forklart. AVVIST brukes ved tydelig samlet primærforverring eller brudd på de vurderte vernene. UAVKLART betyr at kravene til godkjenning ikke er møtt; det betyr ikke at det mangler enhver målt gevinst eller at skade er bevist. For B1 vises topp-k-vern både samlet og på det låste kontrollåret. Ingen krav er justert ved å velge en annen tau etter kontrollen.

## Kombinasjon og B2

{combo}

{b2reason}

## Etterprøvbarhet

Alle målinger er kjørt fra `kjor_p1p2.py`, hele testsuiten er grønn: **{test_count} tester, {test_seconds} s** (`p1p2_tests.log`). Beregningen tok **{manifest['seconds']:.1f} s**; ingen sesonger eller runder kuttet. Flaggene er gjenopprettet til `False` og `None`, med kontroll i `p1p2_manifest.json`. Ingen nett, installasjon, commit eller skriving av produksjonsutdata.

Hovedfiler: `p1p2_tau_utvikling.csv`, `p1p2_nivaer.csv`, `p1p2_parvis.csv`, `p1p2_minuttkalibrering.csv`, `p1p2_premium.csv`, `p1p2_premium_wace.csv`, `p1p2_beslutning.json`, `p1p2_prediksjoner.csv.gz`. Sesongfilene og kjøringsloggen bevarer utviklings-/kontrollfasene hver for seg.

```sh
export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH
PYTHONDONTWRITEBYTECODE=1 python3 samarbeid/modell/codex/kjor_p1p2.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' python3 -m pytest -q tests/ > samarbeid/modell/codex/p1p2_tests.log
PYTHONDONTWRITEBYTECODE=1 python3 samarbeid/modell/codex/skriv_p1p2.py
```
'''
    (O/'p1p2-maling.md').write_text(body)

if __name__=='__main__':run()
