"""Generate round-two report exclusively from modell_r2 result objects."""
from pathlib import Path
import json,csv
G=data
O=G['O'];E=G['E'];ids=G['ids'];ix=G['ix'];plans=G['plans'];out=G['out'];cal=G['cal'];sens=G['sens'];scores=G['scores'];lineup=G['lineup'];orig=G['orig'];SZ=G['SZ'];TAV=G['TAV'];M=G['MATRICES'];common=G['common'];return_runs=G['return_runs'];fttests=G['fttests'];common_scores=G['common_scores'];teamnames=G['teamnames']
def pname(p):return E[p]['web_name']+' ('+teamnames[E[p]['team']]+', '+str(p)+')'
def ns(ps):return ', '.join(pname(p) for p in ps) or '–'
def top(model):return max([p for p in plans if p['model']==model and p['wc']!=8],key=lambda p:p['total'])
def ep(model):return next(p for p in plans if p['model']==model and p['wc']==8)
native={m:ep(m)['total']-top(m)['total'] for m in ['codex','repo_hybrid','repo_repeat']}
ret_diff={m:next(p['total'] for p in return_runs if p['model']==m+'_retur' and p['wc']==8)-next(p['total'] for p in return_runs if p['model']==m+'_retur' and p['wc']!=8) for m in ['codex','repo_hybrid']}
candidate_common=[]
for pp in [ep('codex'),ep('repo_hybrid'),common]:
 vv={m:G['pathscore'](pp,m) for m in ['codex','repo_hybrid']};dd={m:vv[m]-top(m)['total'] for m in vv};candidate_common.append((min(dd.values()),sum(dd.values()),pp,vv,dd))
_,_,common,common_scores,common_diff=max(candidate_common,key=lambda z:(z[0],z[1]))
(O/'felles_valgt_E_r2.json').write_text(json.dumps(dict(plan=common,kryss=common_scores,margin=common_diff),ensure_ascii=False,indent=2))
ft_diff={(m,rule):next(r['R8_R19'] for r in fttests if r['poengsett']==m and r['WC']==8 and r['FT_regel']==rule)-next(r['R8_R19'] for r in fttests if r['poengsett']==m and r['WC']!=8 and r['FT_regel']==rule) for m in ['codex','repo_hybrid'] for rule in ['preserve','plus','reset']}
# Decision: demand a common implementable E path beat delayed alternatives, plus tail and medical stress.
robust=all(v>0 for v in list(native.values())+list(ret_diff.values())+list(common_diff.values())+list(ft_diff.values()))
recommend_wc=robust
choice=common['rows'][0]['tropp'] if recommend_wc else sorted(orig-{SZ}|{TAV});model='blend' if recommend_wc else 'codex';v,xi,cap=lineup(frozenset(choice),8,model);bf=next(p for p in choice if E[p]['web_name']=='B.Fernandes');vice=bf if bf!=cap else max([p for p in xi if p!=cap],key=lambda p:M[model][ix[p],0]);bench=sorted(set(choice)-set(xi),key=lambda p:(E[p]['element_type']!=1,-M[model][ix[p],0]));bank=(G['enact'](orig,G['osell'],10,frozenset(choice)))[1]/10
headline='**Svak anbefaling R8: WC nå, med den felles testede troppen under.**' if recommend_wc else '**Anbefaling R8: Ikke WC nå. Szoboszlai → Tavernier, ett gratisbytte, bank £1,6m.**'
lines=['# Kontroll og revisjon – runde 1', '',headline,'',
'Jeg godtar at første rundes sammenligning var skjev. Alle hovedplanene her bruker samme fremtidige byttepolitikk, gyldig kjøpsunivers, reelle salgspriser og både BB og FH før R20. Tidligere filer er beholdt.', '',
'## Konklusjon om wildcard', '',
f"Under hvert poengsetts egen optimerte politikk slår WC R8 beste undersøkte senere wildcard med **{native['codex']:.1f} poeng** i forbedret Codex-modell og **{native['repo_hybrid']:.1f} poeng** i repo-hybrid. Beste sene runder er henholdsvis R{top('codex')['wc']} og R{top('repo_hybrid')['wc']}. Dette er en langt mer relevant test enn de gamle statiske troppene.", '',
'**WC nå består den snevre testen «høyere under begge hovedpoengsett med samme bytteregel».** Det betyr ikke automatisk at ett bestemt wildcardlag er robust: de to poengsettene velger forskjellige spillere. Derfor har jeg også testet samme kompromissplan, alternativ hale etter R13 og et betinget comeback fra R11.', '',
f"Den beste fellesplanen blant Codex-, repo- og 50/50-bane gir {common_scores['codex']:.1f} / {common_scores['repo_hybrid']:.1f} når de identiske troppene og chipdatoene vurderes med de to hovedpoengsettene (ellever/kaptein velges på nytt). Mot hver modells beste senere WC er marginene **{common_diff['codex']:+.1f} / {common_diff['repo_hybrid']:+.1f}**. Med repoets seksrunderssnitt gjentatt i R14–19 er fordelen ved WC nå **{native['repo_repeat']:+.1f}**. Ved frisk Szoboszlai fra R11 er tilsvarende marginer mot de respektive hovedløpenes beste sene datoer **{ret_diff['codex']:+.1f} / {ret_diff['repo_hybrid']:+.1f}**.", '',
('Disse testene peker alle mot WC nå. Det er modellrobust etter oppgavens kriterium innenfor dette undersøkte settet, men bare svakt: omtrent ett poeng for en felles konkret bane er mindre enn plausibel feil i én spillerrolle. Jeg endrer derfor anbefalingen fra hold til WC på forventning, uten å hevde at en liten rolleendring ikke kan snu den. Ingen av de testede hale-, FT- eller comebackantakelsene snur hovedsammenligningen; det er ingen garanti eller global optimalitetsattest.' if robust else 'WC nå er **ikke robust nok som en konkret handlingsplan på tvers av testene**. Minst én av disse kontrollene snur rangeringen. Derfor beholder jeg WC selv om begge hovedløp isolert velger WC nå. Hvilken kontroll som snur det, står tallfestet over. Gevinsten er liten nok til at denne modell-/haleavhengigheten er beslutningsrelevant.'), '',
'## 1. Svar på hver innvending fra Claude', '',
'**1 – undervurderte toppspillere: godtar metodekritikken, men avviser å kalibrere direkte til observert snitt.** Individuelle xG/xA-priorer fra de to siste tilgjengelige sesongene erstatter posisjonssnittet der historikk finnes. Seneste sesong har dobbelt vekt av den foregående; prioren veier 540 minutter, og øvrige spillere får 270 minutter posisjonsprior. Samme prior brukes for bonus/kort/straffehendelser når feltet finnes. Lagstyrke bruker nå xG/xGA, ikke mål. Noen eliteverdier øker, andre faller – det er ikke riktig å tvinge alle mot repoets tall eller siste sju runders poeng.', '',
'| Spiller | Før, per runde R8–13 | Ny, per runde R8–13 | Repo | Observert R1–7 | Ny xG90 / xA90 |',
'|---|---:|---:|---:|---:|---|']
for r in cal:lines.append(f"| {r['navn']} | {r['forrige_per_runde']:.1f} | {r['ny_per_runde']:.1f} | {r['repo_per_runde']:.1f} | {r['observert_per_runde']:.1f} | {r['ny_xG90']:.2f} / {r['ny_xA90']:.2f} |")
ha=next(p for p,e in E.items() if e['web_name']=='Haaland');br=next(p for p,e in E.items() if e['web_name']=='B.Fernandes');raw=G['repo_rows']
for p in [ha,br]:
 rr=[r for r in raw if int(r['element'])==p and 8<=int(r['gw'])<=13];rb=sum(float(r['xp_bonus']) for r in rr)/len(rr);mm=float(G['md'][p,8]['forventede_min']);nb=G['rates'][p]['bonus']*mm/90;lines+=['',f"{E[p]['web_name']}: repoet gir omtrent {rb:.1f} bonuspoeng per kamp i R8–13; den nye historikkbaserte bonusraten gir omtrent {nb:.1f} ved R8-minuttene. Det er en vesentlig del av modellgapet. Poengsnittet over sju kamper er ikke en fasit for neste kamp; sammenligningen over er en nivåkontroll, ikke en ut-av-utvalg-kalibrering."]
lines+=['',
'**2 – modellavhengig wildcardfordel: godtar og tester.** Hovedtabellen under gjentar hele planleggingen med begge poengsett; den låner ikke bare score til gamle wildcardtropper. Krysskolonnene viser også hvert ferdige forløp under den andre modellen, med ny beste lovlige ellever. Codex-planenes salg av Fernandes var modellfølsomt; de nye hoved-WC-troppene beholder ham ved R8. Eventuelle senere salg er synlige i loggen.', '',
'**3 – skjevt wildcardtidspunkt: godtar fullt ut, rettet.** B gjør Szoboszlai → Tavernier i R8. Alle varianter bruker deretter samme grådige fire-runders politikk med rulling og maks fem FT. WC-rundene er R8, R11, R13, R15 og R17. Ingen variant pålegges å holde dagens tropp urørt. Den gamle marginen 4,2 trekkes tilbake som beslutningsgrunnlag.', '',
'**4 – ugyldige/ubrukelige spillere: godtar, rettet.** Kjøp krever can_select, status uten u/n/i/s, ikke 0 %, og p_start minst 0,50. Dette gjelder alle 15 i nye WC/FH-tropper, også andrekeeperen. Dennis og begge Hughes er utelukket og kontrolleres med assertion. Eksisterende Steele/Kusi-Asare kan beholdes frem til de faktisk selges; dette er ikke nye kjøp. En skadeflagget spiller blir ikke frisk fordi han har historisk rate. Comebacktesten gjør ett eksplisitt, datert unntak for Szoboszlai fra R11.', '',
'**5 – Thiago/Maguire og vice: testes; Claude får støtte for elleveren.** Den forbedrede modellen og repoet velger Thiago fremfor Maguire i R8 etter B. Tabellen for følsomhet viser forskjellen mellom beste lovlige lag med Thiago uten Maguire og omvendt. Bruno velges som vice i den operative anbefalingen, fordi han har sikker rolle og høy forventning i repoet. Min modell alene kan foretrekke Mbeumo; siden vice bare teller ved fravær for Haaland er denne uenigheten liten og ikke grunnlag for et bytte.', '',
'**6 – rollevalidering av E: godtar som belegg for den gamle E-troppen, ikke som automatisk godkjenning av nye navn.** Den nye E-troppen er funnet på nytt og inneholder enkelte andre spillere; disse trenger Claudes nyhetskontroll. CSV-en med minutter gjør modellrollene etterprøvbare. Et historisk p_start over 0,50 er et minimumsfilter, ikke en pressekonferanse.', '',
'## 2. Hovedsammenligning R8–19', '',
'Alle tall inkluderer kaptein, faktiske BB-poeng i forventning, midlertidig FH-tropp og eventuelle trekk. Ingen prosentandel av benken legges til ordinære poeng. Søkets wildcardmål har en liten benkbonus for å støtte senere BB, men den rapporteres ikke som FPL-poeng. Poengforskjeller på få poeng er ikke statistisk signifikante funn.', '',
'| Poengsett | WC | BB / FH | R8 | R8–13 | R8–19 | E minus plan | Trekk | Kryss Codex / repo |',
'|---|---:|---|---:|---:|---:|---:|---:|---|']
for r in out:
 if r['poengsett'] not in ['codex','repo_hybrid']:continue
 diff=next(z['R8_R19'] for z in out if z['poengsett']==r['poengsett'] and z['WC']==8)-r['R8_R19'];lines.append(f"| {r['poengsett']} | {r['WC']} | {r['BB']} / {r['FH']} | {r['R8']:.1f} | {r['R8_R13']:.1f} | {r['R8_R19']:.1f} | {diff:+.1f} | {r['trekk']} | {r['kryss_codex']:.1f} / {r['kryss_repo']:.1f} |")
lines+=['',
'Poengsett (a) er ny Codex-modell R8–19. (b) bruker repoets faktiske spiller-xP i R8–13 og **Codex R14–19**. Der repoet mangler spiller/runde brukes Codex; dekningen lagres i kontrollresultat_r2.json. Uaktuelle/skadde spillere settes til null i begge. Dermed er (b) et hybridscenario, ikke tolv runder uavhengige repo-prognoser. Den tredje testen gjentar hver spillers repo-snitt fra R8–13 gjennom R14–19 i stedet; detaljene står i wildcard_tidspunkt_r2.csv.', '',
'### Samme politikk og penger', '',
'Fra R9 evalueres alle lovlige enkeltbytter i en posisjonspool på inntil 16 beste etter neste fire runder, sju billigste og beholdte kandidater. Vinduet stoppes før neste planlagte WC; en planlagt FH-runde utelates, og benkepoeng legges til hvis BB ligger i vinduet. Gratisbytte tas ved over ett forventet poeng gevinst over disse rundene. Ved fem FT eller i R19 brukes terskel null, fordi videre lagringsverdi er liten innen horisonten. Lagrede FT kan brukes flere samme runde; ett nytt opptjenes etter ordinære runder, maks fem. Ett betalt ekstrabytte er bare tillatt ved over fem bruttopoeng i de neste fire rundene, altså mer enn fire som krevd. Alle gjennomførte gevinster og terskelutløsere logges. Dette er en felles grådig politikk, ikke et perfekt adaptivt sesongoptimum.', '',
'WC/FH har samme kjøpsfilter og søk: deterministisk beam med bredde tre, billig gyldig tropp, reparert eksisterende tropp og eventuelt gyldig eksisterende tropp som startpunkter. WC velges for gjenstående runder til R19; FH for én runde. To lovende BB/FH-datopar velges fra et første forløp og spilles deretter gjennom på nytt med reell gjenoppretting av troppen etter FH. FH gir ingen permanent byttegevinst eller lånt ekstra bank. BB og FH kolliderer aldri med WC eller hverandre. Chipdatoene er beste funn blant disse søkte parene, ikke globalt optimale datoer.', '',
'FT ved WC/FH er ikke spesifisert i lokale API-felter. Hovedantakelsen er bevaring av antallet ved chipbruk, uten nytt FT i selve chiprunden; E starter dermed med to videreførte. Jeg oppgir ikke dette som verifisert 2026/27-regel. To alternative bokføringer – bevaring pluss ett, og reset til ett – er testet på samme valgte chipdatoer. FT_regler_r2.csv viser alle resultatene. Denne usikkerheten skjules ikke som en hardkodet regel.', '',
'Budsjettet starter med £1,0m bank. Ved hvert faktisk salg brukes spillerens eide salgspris; beholdte opprinnelige spillere beholder denne, nye kjøpes/selges til frossen nåpris. Ved gjenkjøp av en tidligere solgt spiller brukes nåpris, ikke gammel salgspris. Alle WC/FH-tropper og alle ukentlige bytter kontrolleres for posisjoner, maks tre per klubb og ikke-negativ bank. Ingen prisendringer er simulert.', '',
'| Plan | Bank etter R8 | Bank etter R19 | FT til R20 |',
'|---|---:|---:|---:|']
for r in out:
 if r['poengsett'] in ['codex','repo_hybrid']:lines.append(f"| {r['poengsett']} WC{r['WC']} | {r['bank_R8']:.1f} | {r['bank_R19']:.1f} | {r['FT_R20']} |")
lines+=['',
'WC1, FH1 og BB1 er brukt før utløp i alle hovedalternativer. Terminalverdien av ubrukte chips er derfor ikke skjult i sammenligningen. FT, bank og tropp har fortsatt verdi fra R20. Modellen stopper R19 og kan følgelig favorisere små sene bytter uten å prise R20+. Den verdsetter ikke ny informasjon, fremtidige skader eller endret cup-/ligaprogram. Det er en felles begrensning, ikke en dokumentert poengverdi for å vente.', '',
'## 3. Følsomhet for R8', '',
'Her holdes troppen etter R8-byttet fast for å isolere spiller-/ellevervalget. Det er **ikke** hovedsammenligningen, som bruker fremtidige bytter. Separate full-policy-tester står under.', '',
'| Poengsett | Scenario | R8 | R8–13 | R8–19 | Thiago minus Maguire R8 | B minus behold til R19 |',
'|---|---|---:|---:|---:|---:|---:|']
for r in sens:lines.append(f"| {r['poengsett']} | {r['scenario']} | {r['R8']:.1f} | {r['R8_R13']:.1f} | {r['R8_R19']:.1f} | {r['Thiago_minus_Maguire']} | {r['B_minus_behold']} |")
lines+=['',
'Taverniers belastningsscenario tolker 70 minutter som **gitt start**: p_start 0,75, forventede minutter 52,5 og p_60 0,7125. Å sette p_play 0,75 sammen med ubetingede 70 minutter ville være umulig, siden maksimum da er 67,5. For repo-xP skaleres Tavernier med forholdet mellom ny og opprinnelig Codex-prognose i stedet for å late som repoets rateledd er kjent. Dette er et rolletapscenario, ikke en skadeprognose.', '',
'Szoboszlai fra R11 er et bevisst optimistisk motstykke til null hele perioden. Det står i konflikt med Claudes sentrale vurdering om ute minst til og med R11, og er derfor en stresstest, ikke nytt skadebelegg. Frisk rate og spilletid estimeres fra egne historiske starter; ingen faktisk returdato antas. I full-policy-testene blir han kjøpbar først fra R11. Senere WC-dato holdes lik den beste fra hovedløpet, mens samme bytteregel og chipsøking kjøres på nytt.', '',
'| Full politikk, frisk R11 | WC | R8–19 | BB / FH |',
'|---|---:|---:|---|']
for p in return_runs:lines.append(f"| {p['model']} | {p['wc']} | {p['total']:.1f} | {p['bb']} / {p['fh']} |")
lines+=['',
'| Full politikk, samme chipdatoer | WC | R8-kjøp | R8–19 |',
'|---|---:|---|---:|']
for r in G['buytests']:lines.append(f"| {r['poengsett']} | {r['WC']} | {r['R8_kjop']} | {r['R8_R19']:.1f} |")
lines+=['',
'## 4. Konkret kritikk av Claudes forslag', '',
'- **Godt nok:** Szoboszlai ut nå; bruk salgspris; unngå et uberegnet trekk; Thiago foran Maguire i R8; Tavernier og Dewsbury-Hall vurderes som rolleavhengig valg. Thiagos lave poeng er ikke i seg selv salgsgrunn når xG og minutter er sterke. Forslaget oppgir også egne databegrensninger tydelig.',
'- **Manglet:** tallfestet WC-dato, BB/FH-plan, reelle fremtidige bytter og verdi av å bygge en spillende andrekeeper/benk før BB. Dette er nå regnet under én felles politikk. Vindusforslaget R12–15 var en hypotese, ikke et dokumentert optimum.',
'- **For sterkt formulert:** «byttet er positivt i alle scenarioer» er ikke en universell robusthetsgaranti når Taverniers minutter kan svikte og Szoboszlai kan komme tilbake. Det må avgrenses til de faktisk testede scenarioene. Belastningstesten over kan favorisere DH.',
'- **Feil generell påstand:** Fernandes ×0,7 trekker ikke alle planer like mye ned. Det gjelder bare dersom samme spiller beholdes, starter og har samme kapteinsrolle. Når WC kan selge ham, velge en annen kaptein eller finansiere andre posisjoner, kan rangeringen endres. Claudes egen krysskontroll viser nettopp dette.',
'- **Ikke et tallfestet FT-estimat:** «ett bytte er verdt 3–4 poeng i én runde» er et mulig behovsscenario, ikke forventet verdi av å rulle. Her prises rulling gjennom faktiske senere handlinger. En skade før neste runde er ikke modellert og kan gi ytterligere informasjonsverdi.',
'- **FH til en eventuell blank:** rimelig beredskap, men lokale data har ingen blank. Å vente på en hendelse utenfor datagrunnlaget er ikke i seg selv en beregnet fordel. Alle planene bruker FH før den utløper også uten blank.', '',
'## 5. Anbefalt handling og kontrollerbar tropp R8', '',headline, '',
'**Startellever:** '+ns(xi)+'.', '',
'**Kaptein:** '+pname(cap)+'. **Visekaptein:** '+pname(vice)+'.', '',
'**Benk:** '+ns(bench)+'. Reservekeeper står først; utespillerne deretter i innbytterekkefølge. **Bank:** £'+f'{bank:.1f}m.', '']
if recommend_wc:
 lines+=['WC ut: '+ns(sorted(orig-set(choice)))+'.', '', 'WC inn: '+ns(sorted(set(choice)-orig))+'.', '',f"Budsjett: £1,0m + salg £{sum(G['osell'][p] for p in orig-set(choice))/10:.1f}m − kjøp £{sum(G['cost'][p] for p in set(choice)-orig)/10:.1f}m = bank £{bank:.1f}m.", '',f"Planlagt BB R{common['bb']}, FH R{common['fh']}; disse datoene er betinget av kjente roller og uendret program, og bør revurderes ukentlig."]
else:
 lines +=[f"Ved fortsatt hold peker de to hovedpoengsettene mot WC R{top('codex')['wc']} / R{top('repo_hybrid')['wc']}. Dette er konkrete arbeidsdatoer, men ingen fremtidig chip er låst nå. Bank £1,6m og to FT til R9 gir mulighet til å reagere på nye lagnyheter."]
lines+=['',
'### Nye wildcardtropper, til Claudes rollekontroll', '',
'| Modellvalg R8 | Tropp | Bank |',
'|---|---|---:|']
for p in [ep('codex'),ep('repo_hybrid'),G['common']]:lines.append(f"| {p['model']} | {ns(p['rows'][0]['tropp'])} | {p['rows'][0]['bank']:.1f} |")
lines+=['',
'Fellesplanen står i felles_valgt_E_r2.json. Blant de tre ferdige banene fra Codex, repo-hybrid og 50/50-blanding velges banen med høyest laveste margin mot de to hovedmodellenes beste sene WC. Det er et lite maximin-søk, ikke en bevist robust optimal tropp. Blend-banen bevares separat i felles_E_r2.json. Kryssvurdering velger ellever på nytt, men endrer ikke de fremtidige byttene; dette er én implementerbar troppsbane under to vurderinger, ikke en uavhengig tredje prognose.', '',
'## 6. Etterprøvbarhet og gjenværende svakheter', '',
'Verifiserte data: 222 element-summary-filer; bootstrap-spillere/status/priser; lokal historikk for R1–7; tidligere sesongers xG/xA/minutter der feltene finnes; spillereglenes poengvekter; frosne kamper til R19. player_matches summeres og kontrolleres mot bootstrap for **alle 668 spilleres minutter og xG**, uten avvik. Lag-xGA tas fra motstanderens summerte xG i kampen; man summerer aldri individuelle overlappende xGA. Det lokale historikkgrunnlaget er dermed tilstrekkelig for xG-lagstyrke.', '',
'Antakelser: sju kamper krymping i lagstyrke; hjemme/borte 1,1/0,9; 540/270 min prior; historisk p_start og minutter uten nye pressekonferanser; fire-runders byttevindu; ett poeng terskel for FT-bruk; benkbonus 0,35 × største forventede benkepoeng i WC-søket; FT-regel ved chip; ingen prisendringer; ingen nye blanke/doble. Empirisk DC-treff fra de 222 historikkene erstatter den gamle grove DC-haleformelen. Data om tidligere bonus er observert i et annet sesongregime og kan også ha strukturell skjevhet.', '',
'Modellresultater er tabellene, ikke verifiserte fotballfakta. Lavere feil mot observert snitt i sju runder er ingen dokumentasjon på bedre fremtidsprognose. Modellen er ikke backtestet med de nye priorene. Den korrigerer heller ikke historiske spiller-xG for motstand før den projiserer nye kamper. Det er usikkerhet både i nivå og relative spillerverdier.', '',
'Automatiske innbytter og kapteinsfallback er ikke simulert. Dette undervurderer en fungerende benk i ordinære runder og kan påvirke marginer på få poeng; alle WC/FH-benker har likevel minst 50 % startsjanse. Poengintervaller fra runde 1 var stressbånd, ikke konfidensintervaller. Her bruker jeg **spredningen mellom poengsett, fellesplan, hale- og comebackscenario** som beslutningsusikkerhet; ingen statistisk sikkerhetsprosent er beregnet. Lokale søk kan overse finansieringskombinasjoner. Ingen av disse resultatene er et bevist globalt optimum.', '',
'Kjør fra repoets rot:', '',
'```sh', '/Users/simenflogstad/opt/anaconda3/bin/python3 samarbeid/gw08/codex/modell_r2.py', '```', '',
'Ingen installasjon eller nett. modell_r2.py leser gamle spillerpoeng bare for før-kolonnen, bevarer minutter_antatt_r2.csv som overstyringsinput, genererer alle *_r2-resultatene og bruker rapport_r2.py til denne teksten. Alle poengtall her kommer fra resultatobjektene i den samme kjøringen. Fullstendige ukentlige kjøp/salg, salgspriser, bank, FT og chips ligger i planer_r2.json; JSON-logs inneholder begrunnelsen i fire-rundersgevinst per bytte. Forrige runde er ikke overskrevet.']
lines+=['', '### Samme E-bane vurdert med begge poengsett', '', '| Bane valgt med | Codex-poeng / margin mot senere WC | Repo-poeng / margin mot senere WC |', '|---|---|---|']
for _,_,pp,vv,dd in candidate_common:lines.append(f"| {pp['model']} | {vv['codex']:.1f} / {dd['codex']:+.1f} | {vv['repo_hybrid']:.1f} / {dd['repo_hybrid']:+.1f} |")
lines+=['', '### FT-regel ved chip: E minus beste sene dato fra hovedløpet', '', '| Poengsett | Bevaring | Bevaring + ett | Reset til ett |', '|---|---:|---:|---:|']
for m in ['codex','repo_hybrid']:lines.append(f"| {m} | {ft_diff[m,'preserve']:+.1f} | {ft_diff[m,'plus']:+.1f} | {ft_diff[m,'reset']:+.1f} |")
text='\n'.join(lines)+'\n';(O/'kontroll.md').write_text(text)
checks=dict(history_files=len(G['history']),player_matches_rows=len(G['pm']),bootstrap_minutes_xg_match=True,purchase_universe=len(G['universe']),repo_cells_R8_R13=len(G['coverage']),native_E_margin={k:round(v,2) for k,v in native.items()},common_E_margin={k:round(v,2) for k,v in common_diff.items()},return_E_margin={k:round(v,2) for k,v in ret_diff.items()},FT_E_margin={str(k):round(v,2) for k,v in ft_diff.items()},recommend_WC=recommend_wc,all_paths_have_WC_BB_FH=True)
for p in plans+return_runs+[common]:
 assert {r['chip'] for r in p['rows']} >= {'WC','BB','FH'}
 assert all(r['bank']>=0 for r in p['rows'])
 for r in p['rows']:
  assert G['legal'](frozenset(r['tropp'])) and G['legal'](frozenset(r['permanent']))
for r in out:
 if r['poengsett'] in ['codex','repo_hybrid']:assert f"{r['R8_R19']:.1f}" in text
(O/'kontrollresultat_r2.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print('REPORT OK',json.dumps(checks,ensure_ascii=False),flush=True)
