"""Generate review with numbers taken directly from result CSVs."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
import pandas as pd
O=Path(__file__).resolve().parent

def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows])

def run():
    b=pd.read_csv(O/'baseline.csv'); c=pd.read_csv(O/'kalibrering.csv')
    diag=pd.read_csv(O/'diagnostikk.csv');audit=pd.read_csv(O/'datakontroll.csv')
    pc=pd.read_csv(O/'spillerkalibrering.csv')
    manifest=json.loads((O/'manifest.json').read_text())
    rows=[]
    for model in ['produksjon_offline','evaluate_pred','form_3gw']:
        for season in ['2023-24','2024-25','2025-26','alle']:
            r=b[(b.model==model)&(b.season==season)&(b.window=='GW2-38')].iloc[0]
            rows.append([model,season,int(r.n),f'{r.mae:.4f}',f'{r.rmse:.4f}',f'{r.spearman_played:.4f}',f'{r.top10:.3f}',f'{r.top20:.3f}',f'{r.top50:.3f}'])
    baseline=table(['Modell','Sesong','N','MAE','RMSE','Spearman, spilte','Topp10','Topp20','Topp50'],rows)
    rows=[]
    for model in ['produksjon_offline','evaluate_pred','form_3gw']:
        for season in ['2023-24','2024-25','2025-26','alle']:
            r=b[(b.model==model)&(b.season==season)&(b.window=='GW8-38')].iloc[0]
            rows.append([model,season,int(r.n),f'{r.mae:.4f}',f'{r.spearman_played:.4f}',f'{r.top10:.3f}',f'{r.top20:.3f}'])
    late=table(['Modell','Sesong','N','MAE','Spearman, spilte','Topp10','Topp20'],rows)
    q=c[(c.model=='produksjon_offline')&(c.season=='alle')&(c.window=='GW2-38')&(c.subset=='all')]
    rows=[]
    for (price,pos),g in q.groupby(['price_group','pos'],sort=False):
        total=g[g.metric=='total'].iloc[0];bonus=g[g.metric=='bonus'].iloc[0]
        rows.append([price,pos,int(total.n),f'{total.predicted:.3f} / {total.actual:.3f}',f'{total.bias:+.3f} ± {total.bias_se_gw:.3f}',f'{bonus.predicted:.3f} / {bonus.actual:.3f}',f'{bonus.bias:+.3f} ± {bonus.bias_se_gw:.3f}'])
    cal=table(['Pris','Pos','N','Total pred./faktisk','Total bias ± SE','Bonus pred./faktisk','Bonus bias ± SE'],rows)
    rows=[]
    for _,r in c[(c.model=='produksjon_offline')&(c.season!='alle')&(c.window=='GW2-38')&(c.subset=='all')&(c.price_group=='>=10')].iterrows():
        rows.append([r.season,r.pos,r.metric,int(r.n),f'{r.predicted:.3f}',f'{r.actual:.3f}',f'{r.bias:+.3f} ± {r.bias_se_gw:.3f}'])
    premium=table(['Sesong','Pos','Mål','N','Predikert','Faktisk','Bias ± SE'],rows)
    rows=[]
    for _,r in c[(c.model=='produksjon_offline')&(c.season=='alle')&(c.window=='GW2-38')&(c.subset=='played')&(c.price_group=='>=10')].iterrows():
        rows.append([r.pos,r.metric,int(r.n),f'{r.predicted:.3f}',f'{r.actual:.3f}',f'{r.bias:+.3f} ± {r.bias_se_gw:.3f}'])
    played_premium=table(['Pos','Mål','N','Predikert','Faktisk','Bias ± SE'],rows)
    f=q[(q.price_group=='>=10')&(q.pos=='FWD')&(q.metric=='total')].iloc[0]
    fb=q[(q.price_group=='>=10')&(q.pos=='FWD')&(q.metric=='bonus')].iloc[0]
    mb=q[(q.price_group=='>=10')&(q.pos=='MID')&(q.metric=='bonus')].iloc[0]
    rows=[]
    for (season,name),g in pc[pc.model=='produksjon_offline'].groupby(['season','name']):
        t=g[g.metric=='total'].iloc[0];v=g[g.metric=='bonus'].iloc[0]
        rows.append([season,name,int(t.n),f'{t.predicted:.2f} / {t.actual:.2f}',f'{v.predicted:.2f} / {v.actual:.2f}'])
    players=table(['Sesong','Spiller','N','Total pred./faktisk','Bonus pred./faktisk'],rows)
    rows=[]
    for _,r in audit.iterrows():
        rows.append([r.season,int(r.raw_rows),int(r.duplicate_rows),f'{r.bonus_per_fixture:.3f}',int(r.fixtures_bonus_above6)])
    data=table(['Sesong','Rårader','Identiske duplikater','Bonus/kamp','Kamper med >6 bonus'],rows)
    s=f'''# Uavhengig modellgjennomgang – Codex

**Hovedfunn:** Den historiske produksjonsrekonstruksjonen overvurderer premiumspisser ≥10 i totalpoeng med {f.bias:.3f} og bonus med {fb.bias:.3f} poeng per spiller–kamp samlet. Premiumspissenes total- og bonusbias er positiv i alle tre sesonger. Premium-MID har samlet bonusbias {mb.bias:+.3f}, men fortegnet varierer mellom sesonger. Dette støtter en målrettet bonustest, ikke et generelt påslag til toppspillere. Fravær uten historiske statusflagg gjør særlig totalbiasen usikker som mål på live-modellen.

Datert 22. oktober 2026. Gren: `modellforbedring`. Gjelder modellen som skal støtte lag 7089878 i 2026/27. Claudes nye forbedringsliste er ikke lest. Historiske GW08-kritikker og kontrollrapporter er lest som oppgitt i oppdraget.

## Hva som faktisk er kjørt

Alle tre testsesongene **2023/24, 2024/25 og 2025/26, GW2–38**, uten nett. Ingen sesonger eller testrunder er kuttet. Hver prognose bruker bare tidligere runder i samme sesong og eventuelt sesongen før. GK-/DC-regimeskifter betyr at historiske resultater ikke uten videre er kalibrering av alle 2026/27-regler.

To forskjellige baseliner er nødvendige:

- **`evaluate_pred`**: `P.walk_forward` med dagens standardparametre i `backtest.py`, personlig startprior, lagprior og forrige sesong ved liten datamengde. Dette er riggens modell, som **ikke er identisk med produksjon**.
- **`produksjon_offline`**: historisk rekonstruksjon som kaller `minutes.build`, `expected_points.per90_rates`, `dc_hit_rates`, `expected_points` og `team_strength.fit_current`. Den bruker personlige priorer, vektede minutter, vektet lagstyrke, fjorårets hjemmefordel, produksjonens redningsfunksjon og tilpasset bonustemperatur. Dette er den mest relevante målte baseline for dagens modell.
- **`form_3gw`**: riggens tre-runders poengsnitt, med samme fallback og nøyaktig samme rader som `evaluate_pred`. En enkel referanse, ikke et endringsforsøk.

**Begrensninger i produksjonsrekonstruksjonen:** historiske API-statusflagg, pressekonferanser og komplette deadline-snapshots finnes ikke her. Alle settes tilgjengelige; tilgjengelighetens kvalitet er derfor ikke målt. Testfilene brukes til kampoppsett og spiller-/klubb-/posisjonsmetadata, som en tilnærming til en historisk bootstrap. Testkampens minutter, starter, xG, BPS, bonus og poeng brukes aldri til tilpasning. Eldre års `cleaned_players.csv` finnes ikke: spillerpriorene rekonstrueres av forrige års kamprader med samme 450-minuttersgrense og mål-/assist-/BPS-rater som produksjonen. Navnekoblingen er eksakt historisk navn, mens live-koden normaliserer navn; identitetsendringer kan derfor gi manglende prior. Lagpriorer beregnes fra fjorårets mål med samme estimator og straff, opprykkslag får bunn-tre-prior. xG→mål kalibreres mot neste rundes kjente kampprogram, ikke produksjonens seks kommende runder. **Dette er ikke arkiverte live-prognoser eller en full test av kontoen 7089878.**

Wrapperen setter `P.BASE` til lokal cache; `B.HIST` styres dermed lokalt av riggen. Andre produksjonslesere erstattes med data i minnet. Nettforbindelser blokkeres eksplisitt. Eksisterende SciPy eksponerer Spearman som tuppel/`correlation`, så wrapperen leser første resultatfelt i stedet for riggens nyere `.statistic`-attributt; ingen pakker er oppdatert. Bonustemperatursøket er vektorisert med samme rutenett og tapsfunksjon; lik temperatur mot originalfunksjonen kontrolleres i GW2 i hver sesong. Observerte temperaturer: {diag.tau.min():.1f}–{diag.tau.max():.1f}.

**Datarydding uten å endre kildefiler:** ti identiske duplikater i 2025/26 fjernes i minnet. Fjorårets fixture-ID-er gis negativt fortegn før riggens tidlige sammenblanding med årets historikk: begge sesonger bruker ellers ID 1–380, og join på ID kan lage falske kamppar. GW8–38 påvirkes ikke av denne ID-rettingen. 2022/23 har to forskjellige Ben Davies; navnebaserte priorer kan blande disse. Det er en gjenværende identitetsbegrensning, ikke to identiske datarader.

## Målt baseline

Enhet: én **spiller–kamp**, også null minutter. MAE/RMSE bruker alle predikerte rader. Spearman bruker bare faktisk spilte, slik riggens docstring krever. Topp-k er faktisk poengsnitt for de k høyest predikerte radene per sesong/runde, deretter snitt over rundene. Dette er ikke en lovlig startellever, og en spiller med dobbeltrunde kan oppta to plasser. Pris, formasjon og kapteinsdobling inngår ikke. Forventningsmodeller vurderes også med RMSE: MAE belønner medianen og kan favorisere null for spillere som ofte ikke spiller.

{baseline}

For direkte sammenligning med riggens ordinære start i GW8:

{late}

Modellene dekker litt ulike spillerunivers: produksjonsfunksjonene kan gi priorbasert prognose til spillere riggen hopper over. Tallene over er derfor baseliner for hver modell, ikke en kausal effekt av ett tiltak. `parvis_diagnostikk.csv` sammenligner dem på felles nøkler og har runde-klustret SE for differanser i MAE/MSE. Ingen modellendring er implementert eller erklært bevist bedre i denne gjennomgangen.

## Kalibrering: pris og posisjon

`kalibrering.csv` inneholder alle prisgrupper × posisjoner, hver sesong og samlet, GW2–38 og GW8–38, bonus og totalpoeng. Hovedutvalget er **alle** predikerte spiller–kamper. `played` er en separat diagnose av de som faktisk spilte; slik etterhåndsseleksjon skal ikke brukes som bevis for ubetinget kalibrering.

Pris er siste observerte pris fra en **tidligere GW**; første observasjon uten kjent tidligere pris utelates fra prisgruppene. Dette er en offline tilnærming til deadline-pris, ikke sluttpris eller pris bestemt av testkampen. Intervallene er <6, [6,8), [8,10), ≥10 millioner.

Samlet produksjonsrekonstruksjon, GW2–38. **Bias = predikert minus faktisk**; positivt betyr overvurdering. SE klynger residualene per sesong/runde og vekter etter antall rader. Den tar felles rundestøy, men ikke all seriekorrelasjon/spilleravhengighet; den er ingen garanti for generalisering til et nytt år.

{cal}

Premium ≥10, fordelt per sesong:

{premium}

Tilleggsdiagnose blant faktisk spilte premiumspillere, samlet (etterhåndsseleksjon, ikke ubetinget kalibrering):

{played_premium}

Bonusovervurderingen for premiumspisser består i dette utvalget, mens totalbiasen blir mindre. Premium-MID har her omtrent nøytral/svakt negativ totalbias samtidig med positiv bonusbias. Vi kan derfor ikke konkludere med at alle premiumprofiler er overvurdert i totalpoeng.

Spillerdiagnose, alle prognoser GW2–38, ikke prisfiltrert:

{players}

Bonusbudsjettet i faktiske data:

{data}

**Tolkning:** Se fortegnene over før man hevder at «toppspillere generelt er undervurdert». Bonus og øvrige poeng kan ha motsatt skjevhet og delvis oppheve hverandre. Premiumgruppene inneholder svært få forskjellige spillere; mange rader er gjentatte observasjoner av samme profil, ikke uavhengige replikasjoner. Prisgruppe er heller ikke en ren ferdighetsgruppe: skader, rotasjon, prisfall og posisjon påvirker sammensetningen. Tre tidligere sesonger avgjør ikke om akkurat 8,4 eller 6,1 er riktig for Haaland i GW8 2026/27. GW08-sju-runderssnittet var en nivåkontroll innen samme sesong, ikke dokumentasjon ut av utvalg.

## Rangert forbedringsliste

Forventet gevinst nedenfor er **hypoteser**, med mindre raden uttrykkelig sier kode-/datafunn. Ingen forventede sesongpoeng er anslått som om de var målt. Kostnad er grovt arbeidsskønn, ikke en måling.

### Prediksjon og målekjede

| Prioritet | Tiltak og begrunnelse | Forventet gevinst / måling | Kostnad / risiko |
| --- | --- | --- | --- |
| P0 | Gjør produksjonsfunksjonene til felles prognosemotor også i `evaluate_pred` og `season_sim`; separate innlesere. Bevar identiteter og unike fixture-ID-er på tvers av år. | Målt kodeavvik: riggen mangler produksjonens personlige angrepsprior, tidsvekting, minuttmodell, temperaturtilpasning og redningsfunksjon. Gir troverdig måling; ingen påstått poenggevinst. Sjekk komponentparitet på frosne input. | 2–4 t. Middels fare for å endre baseline ved refaktorering. |
| P1 | Tilpass bonus på **predikert BPS/bonus fra tidligere walk-forward-fold**, ikke realisert BPS i treningskampen. Sammenlign enkel krympet historisk bonusrate, mildere temperatur og ev. hendelsesmodell. | Hypotese: bedre premiumkalibrering og kapteinsrangering. Mål parvis bonus-/total-MSE, kalibrering, Spearman og topp10/20. Ikke bare MAE eller samlet bonusbudsjett. | 2–4 t for enkel variant; hendelsesmodell større. Middels/høy risiko for ny støytilpasning. |
| P2 | Rett minuttmodellens innhopp-denominator: `p_sub_given_no_start` deler i dag på alle vektede kamper, og multipliseres så med `(1-p_raw)`; det demper innhopp to ganger. Tilpass også personlig P(60+ gitt start). | Kodefunn; gevinst ikke målt. Mål først innhopp/minutter/P60 med MSE/Brier og total-MSE i prissjikt; så benk/autobytter i sesongsimulering. Hypotese: bedre billige rotasjonsspillere. | 1–3 t. Middels risiko: økte forventninger kan forverre MAE selv ved bedre forventning. |
| P3 | Bruk fjorårets **xG/xA**, ikke mål/FPL-assists, som personlig angrepsprior der felt finnes. Sammenlign én/to sesonger og tidsavtagende prior; behold fallback. | Hypotese: mindre avslutningsstøy og mindre feil tidlig, særlig elite/ny rolle. Parvis total-MSE/topp-k i GW2–7 og GW8+, tre sesonger; ikke velg 540/270 på nytt etter samme allerede brukte testsett. | 2–4 t. Middels: navne-/klubb-/posisjonsbytter, assistdefinisjoner og aldring. |
| P4 | Normaliser historiske angrepsrater for motstand/hjemmebane før nye kamper skaleres. Produksjonens nevner `exp(mu+att)` er nøytral bane, mens observert rate allerede inkluderer hjemmebaner. | Hypotese: mindre program- og nivåskjevhet; effekten er ikke målt her. Ablasjon av nevner og motstandsjustering hver for seg; angreps-/total-MSE og topp-k per sesong. | 3–6 t. Middels/høy risiko for dobbeljustering og ustabile små utvalg. |
| P5 | Håndter bonusties og spilleusikkerhet eksplisitt. `exp(0)=1` gir også nullspillerne bonusvekt; fast seks poeng overser ties; `p3=p2` er en tilnærming. | Faktisk bonus/kamp >6 er målt over. Hypotese: bedre samlet bonusnivå og korrekt bonus ved fravær. Krev bonuskalibrering per fixture og spillergruppe; deretter total-MSE/topp-k. Ikke bare multipliser alle med et samlet budsjettforhold. | 2–6 t. Høy risiko hvis forbedret ligasum skjuler dårligere spillerfordeling. |
| P6 | Sesongstyrt poengkonfigurasjon, først GK-mål **10 i 2026/27** fra lokalt scoring-snapshot. `expected_points.py` og `backtest.py` har 6. Ta senere med små manglende hendelser som rødt kort/straffebom. | Regelretthet er ikke en tuninghypotese. GK-korreksjon er +4 × forventede GK-mål, svært liten forventet gevinst normalt. Rekonstruer lokale faktiske poeng og test riktig sesongregime; ikke krev signifikant MAE-gevinst for en kjent regel. | <1 t for GK; lengre for felles regelmotor. Lav risiko med sesongversjonering; høy ved å gi gamle sesonger nye regler. |

### Beslutninger

| Prioritet | Tiltak og begrunnelse | Forventet gevinst / måling | Kostnad / risiko |
| --- | --- | --- | --- |
| D0 | Reelle eier-/salgspriser, bank og FT inn i `solve`; bokfør nye kjøp separat og bruk korrekt faktisk chip-/FT-tilstand. Nå brukes nåpris ved salg, første FT=1, og FT etter WC begrenses til 1. | Kodefunn, og GW08-kontrollen dokumenterte en ufinansierbar plan. Gevinst: gjennomførbare planer; ingen målt sesonggevinst her. Først frosne tilstands-/budsjettsjekker, så parvis sesongsimulering med korrekt salgspris. | 2–4 t. Middels, særlig gjenkjøp, prisgevinst og chipregler. Lokal kilde må støtte faktisk FT-regel; ikke velg den som gir penest simulering. |
| D1 | Lengre rullerende horisont med terminalverdi for FT/chips/tropp; reell FH og sesongens chipvinduer. Nå optimizer=5 GW, xP vanligvis=6; GW08-hybrid skiftet modell etter GW13. | Hypotese: bedre rulling og chipvalg, færre kunstige siste-runde-bytter. Parvis helsesongsimulering med lik prognosemotor, starttilstand, framtidsinformasjon og chipdatoer ved isolering av WC-effekt. | 4–8 t+. Høy risiko for solverkostnad og dårligere langtidsprognoser. |
| D2 | Erstatt fast benkevekt 0,15 med forventet verdi av lovlige autobytter og vice; mål terskel for FT/hits med denne verdien. | Hypotese: bedre benk og færre dyre trekk. Bare sesongsimulering viser nettoverdi. Hold bonus/minutter faste under beslutningstesten. | 3–6 t. Middels; korrelert fravær og formasjon kompliserer. |
| D3 | Bredere kandidatsøk, symmetriske startpunkter og gjennomførbar solverstatus før en plan publiseres. Skill beste funn fra bevist optimum. | GW08 R3 viste søkefølsomhet. Hypotese: færre falske WC-fordeler. Samme-tid-budsjett parvis sesongsimulering; logg incumbent, gap og lovlighet. | 2–4 t. Middels solver-/kjøretidsrisiko. |

**Før beslutningsmåling:** `season_sim.py` bygger `pos_map`/`team_map` fra hele sesongfilen og prognosehorisonten fra framtidige spillerrader. Ved klubb-/posisjonsbytter kan dette bruke metadata som ikke var kjent på beslutningstidspunktet. Flytt disse oppslagene til tidspunktets roster; ikke bruk faktisk framtidig spillerregistrering som prognoseunivers. Sluttført kampprogram brukes også retrospektivt her; arkiver for når blanke/doble ble annonsert mangler. Slik informasjonslekkasje må skilles fra ren walk-forward-tilpasning av statistikk før sesongresultater tolkes som realistiske.

### Egen GW08 R2-modell: hva jeg ville beholdt og forkastet

`modell_r2.py` har nyttige byggesteiner: faktisk salgsverdi, samme fire-runders byttepolitikk på alle baner, personlig historisk xG/xA/bonusprior, xG-basert lagstyrke, empirisk DC-treff og et eksplisitt kjøpsfilter. **Ingen av disse R2-kombinasjonene er målt ut av utvalg her**, og hele skriptet er ikke kjørt: import ville starte søk og skrive i GW08-mappen, utenfor oppdragets skrivegrense.

Jeg ville ikke gjøre R2 til ny produksjonsmodell. Den bruker bl.a. utestede 7-kampers lagpriorer, 1,1/0,9-hjemmefaktorer, 540/270-minutters krymping og relativt faste roller til GW19. Historisk bonusrate ivaretar ikke konkret kampmotstand/ties; den er en nyttig enkel konkurrent, ingen fasit. Angrepshistorikken er ikke motstandskorrigert. `max(0,val)` klipper negative forventninger. Det deterministiske beam-søket garanterer ikke optimum; BB/FH søker få par, terminalverdier mangler, og ordinære autobytter/vice var ikke simulert. R3s tilbaketrekking av WC-anbefalingen er den relevante senere kontrollen; R2s gamle marginer er ikke bevis for WC nå eller bedre prediksjon.

## De tre første tiltakene etter sammenligning med Claude

1. **Korrekt tilstand og regler:** D0 + liten GK-retting P6, med frosne eksempler fra 7089878. Krev at bank/salg/FT/chips stemmer og at alle planer kan gjennomføres. Dette er korrekthet, og skal ikke vente på 3 SE i en poengtest. Produksjonsfiler endres først etter avtale.
2. **Én enkel bonushypotese:** P1, etter at felles målekjede P0 er etablert. Sammenlign dagens funksjon med krympet historisk bonusrate og én forhåndsvalgt mildere temperatur; tilpass bare på tidligere sesonger/runder. Ikke juster elitepoeng for å matche GW08-observasjonene.
3. **Avgrenset minuttkorreksjon:** P2, hold resten fast. Dette har en konkret kodebegrunnelse og kan måles på minutter/innhopp før kostbar sesongsimulering. Ingen samtidig endring av lagstyrke, priorvekt og bytteterskel.

## Krav før «forbedring»

- Frys kandidat, primærmål, utvalg og praktisk effektgrense før ny kjøring. Prediksjon: primært **parvis MSE** for forventningskvalitet; MAE som sekundærdiagnose. Topp10/20 og premiumkalibrering er vern mot en forbedring som bare gjelder nullspillere. Sammenlign nøyaktig samme `(sesong, spiller-ID, fixture)`; aggreger også dobbeltrunder til spiller/GW før en beslutningsnær topp-k-test.
- **Minst 3 kluster-/blokkbaserte standardfeil** samlet i riktig retning, og samme fortegn i alle tre sesonger på primærmålet. Bruk f.eks. fire-runders blokkbootstrap innen sesong og følsomhet for spillerklynger. Rapporter også sesongvise effekter. Den vanlige rad-SE i `evaluate_pred` behandler korrelerte rader som uavhengige; dens svært små standardfeil er ikke alene nok.
- Forslag til praktisk prediksjonsgrense, **normativt og ikke målt**: minst 0,5 % lavere MSE samlet. For en kandidat som hevdes å forbedre lagvalg: minst +0,10 faktisk poeng per valgt spiller/runde i forhåndsvalgt topp20 og helst ≥2 blokk-SE; ingen motsatt forverring >2 SE i topp10. Vis både absolutte endringer og SE. Ved uenighet mellom primær- og beslutningsmål: behold som uavklart og kjør målrettet sesongtest.
- Med flere temperaturer/priorvekter øker vinnerflaksen. Bruk de eldre årene til utvikling og siste år som låst kontroll; disse tre årene er **allerede brukt til tuning tidligere i repoet**, så dagens walk-forward er tidsmessig ut av utvalg per prognose, men ikke et helt urørt modellvalg-holdout. Nye kandidater trenger låst test eller framtidig prospektiv kontroll, og helst nestet walk-forward for hyperparametre.
- Beslutninger: `evaluate.py`/`season_sim.py`, tre sesonger og minst de tre felles frøene, samme tilgjengelige informasjon og korrekt regelregime. Forslag: ≥3 parede SE samlet, samme fortegn i alle sesonger og minst +5 netto sesongpoeng i gjennomsnitt. Flere frø reduserer bare følsomhet for optimizerstier; de skaper ikke flere uavhengige fotballsesonger. Ved sprik som i tidligere bytteterskeltest: ingen generell forbedring etablert.

## Reprodusering og leveranse

```sh
/Users/simenflogstad/opt/anaconda3/bin/python3 samarbeid/modell/codex/kjor_baseline.py
/Users/simenflogstad/opt/anaconda3/bin/python3 samarbeid/modell/codex/ekstra_analyse.py
/Users/simenflogstad/opt/anaconda3/bin/python3 samarbeid/modell/codex/skriv_rapport.py
```

Full baseline-/kalibreringskjøring tok {manifest['seconds']:.1f} sekunder i eksisterende Python. Ingen pakker installert, ingen nettbruk, ingen commit. Alle nye filer er i denne mappen. `baseline.csv` og `kalibrering.csv` er hovedresultatene; `prediksjoner.csv.gz` gjør hvert aggregat etterprøvbart. `diagnostikk.csv`, `datakontroll.csv`, `spillerkalibrering.csv`, `parvis_diagnostikk.csv`, `kjoring.log` og `manifest.json` dokumenterer supplerende målinger, miljø og kildefil-hasher. `src/`, `data/`, `config/` og `tests/` er ikke endret.
'''
    (O/'gjennomgang.md').write_text(s)

if __name__=='__main__':run()
