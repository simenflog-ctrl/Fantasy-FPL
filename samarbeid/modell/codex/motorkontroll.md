# Uavhengig kontroll av ukemotoren

klar til bruk fra R12

Arbeidsstatus 23. november 2026: **Punkt 3 fullført.** d428750, F3/F7-reproduksjoner, GW10/GW11/R12 gyldige oppsett og tall for gyldige planer er kontrollert. Codex-standardtest: 64 bestått, 2 hoppet over på 72,35 s. Claudes langsomtestlogg: 66 bestått (`samarbeid/modell/claude/pytest-langsom-d428750.log`).

### Prioritert kontroll før R12

1. **F3/F7 er rettet i d428750 og reproduksjonene avviser ugyldige input.** Gyldige GW10-, GW11- og R12-oppsett er kontrollert; ingen rettinger gjenstår før R12.
2. **Søket og `fh_start`:** ingen motorretting kreves før R12 dersom Claude og Codex bruker samme gyldige `fh_start` i begge analyser. Dette holder rangeringen sammenlignbar og ga samme planpoeng i R11. Søk over flere FH-datoer kan vurderes senere; det er et søkedekningsvalg, ikke en regnefeil for fast plan.

Arbeidskopi: `ukemotor-fletting`, fra c0f7ebe. Motorrettelsen som forelå ved første kontroll var e5cde2e. Kontrollør: Codex. Bare `samarbeid/modell/codex/` endres. GW10 er fasit for flyttingen, ikke prognosenes treffsikkerhet. Ingen nettverk brukes.


## Dom per oppdragspunkt (historisk, etter commit 4ed2cbc)

1. **OK — tester.** Standardtest nå: **60 bestått, 2 hoppet over, 74,38 s**. Langsomtesten kjørt av Claude: **62 bestått, 2 hoppet over, 250,92 s**. Eldre resultater står i loggene under. 
2. **OK — GW10-dekket regnelogikk.** Kildekontroll fullført; bevisste generaliseringer og avvik utenfor fasiten er listet nedenfor. Dette er ikke en påstand om at all ny funksjonalitet er feilfri (se punkt 3 og den historiske F12-reproduksjonen).
3. **FEIL — nye funksjoner/regler.** F1/F2/F6/F9/F11/F12 er rettet. F3 og F7 har hver et gjenværende kanttilfelle; se tabellen etter commit.
4. **OK — WC, TC og FH i inneværende runde stoppes ved de kontrollerte analyseinngangene.** CLI gir forklaring; Motor gir TypeError for ukjente WC/TC-parametre og AssertionError med tekst for FH nå. Den interne wildcard-hjelpegrenen er fortsatt ikke en støttet analyse (se steg 4).
5. **USIKKER — bruk fra R12.** Den vanlige CLI-kjøringen avviser feiloppsett og de åtte rettingene er kontrollert. Direkte Motor godtar fortsatt et chipargument som den kaster bort; delvis overlappende overstyringsintervall har uavklart klipperegel. Krever disse avklaringene før ubetinget godkjenning.

## Historisk kontroll — kjørt 19. november, før e5cde2e

Kilder: `motorkontroll-data/eksempler.log` og `kanttilfeller.log`. Disse historiske loggene bevares. Tabellen gjengir observerte resultater, ikke konklusjoner om dagens kode.

| Funn | Historisk reproduksjon | Hva e5cde2e/test_oppsett.py oppgir å rette |
|---|---|---|
| F1 | BB/FH samtidig og uten tilgjengelige chips godtatt; BB5 brukt som BB9 ved negativ indeks; full kjøring ga OK; `fh_start=7` godtatt med tom FH-liste. | `alternativ`/`faste_planer` og CLI sjekker tilgjengelighet/kollisjon; siste variant må sjekkes. |
| F2 | FT=6, −1, 1,9 godtatt i Motor (1,9 ble 1); FT-følsomhet −1 ga fire minuspoeng ved rull; vekt=2 godtatt. | CLI sjekker gratisbytter 0–5; andre innganger må sjekkes. |
| F3 | Oppgitt manglende overstyringsfil ignorert; omvendt intervall 8–7 med `faktor='feil tall'` ignorert. | Manglende fil stoppes; intervall må sjekkes. |
| F4 | WC/TC i `chips` og i `felles_chip` ignorert med status OK. | WC/TC i `chips` stoppes; `felles_chip` må sjekkes. |
| F5 | Spillerpoeng overskrevet uten SHA256SUMS til tross for README-løfte. | README avklarer at prognoseskriptet fryser; motoren overskriver. |
| F6 | Bestilt skadesim med to trekk og tom BB-liste hoppet over uten melding, status OK. | Ingen oppgitt rettelse. |
| F7 | Horisont R19–20 og R38–39 godtatt, også BB i siste runde. | CLI avgrenser chipvindu/sesong; direkte Motor må sjekkes. |
| F8 | G-rader beholdt gammel modellspredning, f.eks. 49,0886 i stedet for 48,2788 (arvet fra GW10). | G-spredning regnes etter kapteinsendringen; fasitjustering i test. |
| F9 | `p_start=0, forventede_min=30` ga P(spiller)=0, codex=0,766248, repo=1,875 (id 13). | Ingen oppgitt rettelse. |
| F10 | `--frys` kopierte player_matches før eksisterende expected_points utløste stopp; blandet par ble liggende. | Repo-kilden er rettet, ikke nødvendigvis delvis kopiering. |
| F11 | Eget alternativ `Claude_test` i fellestabellen, men bare standardplanens bytteantall 0 i chiprutenettet. | Ingen oppgitt rettelse; vurder mot kontrakten. |

Andre tidligere resultater: dobbel/blank i begge poengsett, autobytter og BB (største avvik 7,32e−13); overstyringsrekkefølge, retur, flagg, kilde og id; salgspris/gjenkjøp/budsjett/2–5–5–3/klubbgrense/trekk; FT +1/tak fem/lokal FH-antakelse; CLI full og bare-poeng, bankstandard og skriveområde; frysebytes/overskrivingsnekt; standardhorisonter R12→19, R19→19, R20→29, R35→38; repo-fallback og kjøpsunivers: **OK i de kjørte eksemplene**. Første 20 skadeverdener mot GW10 r2: største avvik 0. Skadesim: første 100 varigheter identiske, 101–150 avviker med motorens stabile blokkregel. Frossen minuttabell prioriteres foran overstyring: OK. Hovedskriptet tok 35,94 s.

## Fortsettelse

Steg 2: kjør oppdaterte skript og klassifiser F1–F11. Steg 3: kildeekvivalens. Steg 4: tomme chips, R20-vindu, WC/TC/FH nå gjennom CLI og Motor. Steg 5: samlet dom og prioritert retteliste, inkludert `fh_start`. Ingen opplysning om tidspunkt for kvotenullstilling.

## F1–F11 før commit 4ed2cbc (kontroll 21. november)

En gruppe får GJENSTÅR når minst én variant består. Alle linjenumre er i dagens `samarbeid/motor/`.

| Funn | Status | Alvorlighet | Dagens resultat og kilde |
|---|---|---|---|
| F1 | GJENSTÅR | påvirker beslutninger | Kollisjon, BB utenfor horisonten og ulovlige felles datoer stoppes. `Motor(..., fh_runder=[], fh_start=7).standardanalyse(maks_bytter=0)` lykkes fortsatt; rangeringen bruker en utilgjengelig FH. Også `bane`/`alternativ` og `ft_folsomhet` godtar FH7 med tom FH-liste. `motor.py:46`, `motor.py:344`, `motor.py:498`, `motor.py:597`. |
| F2 | GJENSTÅR | påvirker beslutninger | CLI avviser −1/6, men godtar 1,9. Motor godtar alle tre; følsomhet −1 gir −4 ved rull; vekt 2 godtas. `kjor.py:61`, `kjor.py:126`, `motor.py:38`, `motor.py:42`, `motor.py:592`. |
| F3 | GJENSTÅR | påvirker beslutninger | Manglende fil avvises. Rad med intervallet 8–7 og faktor «feil tall» ignoreres fortsatt, uten nyhetsjusteringen. `poeng.py:126`. |
| F4 | RETTET | påvirker beslutninger (før rettelsen) | WC/TC avvises både i `chips` og `felles_chip`. Direkte Motor avviser WC/TC-parametre; FH nå avvises også (steg 4). `kjor.py:67`, `kjor.py:73`. |
| F5 | AKSEPTERT | kosmetisk dokumentasjonsavvik rettet | Poengene overskrives som før. README sier nå uttrykkelig at prognoseskriptet skal fryse dem. Motoren lover ikke lenger å lage SHA256SUMS. |
| F6 | GJENSTÅR | påvirker beslutninger | To bestilte skadetrekk uten BB gir status OK uten simulering eller forklaring. `kjor.py:185`, `skadesim.py:58`. |
| F7 | GJENSTÅR | påvirker beslutninger | CLI avviser R19–20/R38–39. Direkte Motor lager fortsatt planer med BB20/BB39 over vindu/sesong. `kjor.py:64`, `motor.py:35`, `motor.py:43`. |
| F8 | RETTET | kosmetisk for rangeringen; påvirket tolking av modelluenighet | Ingen avvik i kapteinsradenes spredning etter ny beregning. `motor.py:544`. |
| F9 | GJENSTÅR | påvirker beslutninger | Id 13: p_start=0/minutter=30 godtas; P(spiller)=0, codex=0,7662484904, repo=1,875. `poeng.py:148`, `poeng.py:247`, `poeng.py:257`, `poeng.py:291`. |
| F10 | RETTET | påvirker beslutninger (blandet datagrunnlag før rettelsen) | Eksisterende expected_points stopper før player_matches kopieres. Testen bruker et eget lite repo for å verifisere riktig kilde også. `kjor.py:37`, `kjor.py:39`, `kjor.py:45`. |
| F11 | GJENSTÅR | påvirker beslutninger | Claude_test kommer med i felles planer, men ikke i chiprutenett/standardalternativer. Plan-v2 A lover rutenett per alternativ; GW10 r2 hadde dette. `kjor.py:158`, `kjor.py:167`, `motor.py:510`. |

Positive omkjøringer: AST-likhet for lagfunksjonene, dobbel/blank/autobytter/BB (7,32e−13), overstyringsrekkefølge/retur/kilde/id, lovlige FT og budsjett/tropp/salg/gjenkjøp, full CLI og bare-poeng, egne forslag på felles datoer, FT-følsomhet på gyldige verdier, standardhorisonter, begge repo-fallbackene og kjøpsunivers: OK. Første 20 skadeverdener for A/B ved 2 %: **største avvik 0,0** mot GW10 r2. Frossen tabell prioriteres som dokumentert.

## Steg 3: ekvivalens og avvik fra GW10

Lest mot `samarbeid/gw10/codex/modell.py` og `modell_r2.py`; de gamle skriptene importeres/kjøres ikke fordi de skriver til GW10. Nedenfor er linjer i dagens motor, med gamle linjer angitt separat.

| Del | Vurdering / konkret forskjell |
|---|---|
| `poeng.py:20`, `poeng.py:50`, `poeng.py:180`, `poeng.py:238` | **OK**: samme xG-styrke med 7 kampers prior, startvekter/innhopp, 540/270-minutters krymping, siste to sesonger, defensive bidrag, hjemmefaktorer, keeperredninger, bonus/kort, `max(0, val)`. Sammenlignet med gammel `modell.py:32`, `modell.py:47`, `modell.py:86`, `modell.py:103`. Hardkodede R9 og 2026/27 er parametre. Lag uten kamp får nå styrke 1 (`poeng.py:39`); dette endrer ikke GW10-lagene. |
| `poeng.py:73`, `poeng.py:94`, `poeng.py:154`, `poeng.py:166` | **Tilsiktet ny funksjonalitet**: hardkodede nyheter (`modell.py:68`) er filrader i rekkefølge; samme avrunding 4/2 desimaler. Frossen tabell kan dekke en større horisont (`>=` i stedet for eksakt settlikhet i gammel linje 84), og støtter `gw`. Kjente returdatoer overstyrer blokkering per runde; kjøpsfilteret utelukker fortsatt blokkerte spillere. Feil F3/F9/F12 er utenfor GW10-fasiten. |
| `poeng.py:251`, `poeng.py:267`, `poeng.py:278` | **Tilsiktet forbedring**: gammel XP summerte allerede kamper, men PP var uendret ved blank/dobbel, og repo-dict beholdt siste rad. Nå er blank XP/REPO/PP=0, dobbel XP/bonus=2× ved like kamper, PP=1−(1−p)^2, og repo summeres. Ufullstendig kampantall/null repo-minutter gir hel-runde codex-fallback (`poeng.py:288`). Ingen repo-rad gir fallback uten å øke telleren, som før. Egne omkjøringer og fire direkte skaleringstester i `motorkontroll_ekvivalens.py`: OK. Antakelsen om uavhengig oppmøte mellom kamper og like minutter per kamp er spesifisert, ikke verifisert fotballstatistikk. |
| `lag.py:60`, `lag.py:96`, `lag.py:135`, `lag.py:232` | **OK**: `benchweights`, `evaluate_selection`, `select`, `obj_batch` AST-identiske med GW10 etter fjerning av docstrings. Bekreftet på nytt. Dette er eksakt gjenbruk, ikke bare noen like sluttall. |
| `motor.py:77`, `motor.py:102`, `motor.py:115`, `motor.py:131`, `motor.py:145`, `motor.py:202`, `motor.py:281`, `motor.py:333` | **OK for støttede baner**: samme kandidatsiling, 12 beste + 4 billigste, enkeltbytter/finansieringspar, salgsrabatt/gjenkjøp, terskel 1/5 poeng, fire runders byttepolitikk, FT-tak og FH-bevaring, MILP (8 s, én tråd), eksakte sluttvekter. Sammenlignet med gammel linje 302–463. Runde, bank, budsjett, slutt og vekt er parametre; `INGEN=-1` erstatter BB-sentinelen 89/99 som var utenfor horisonten. Wildcard-hjelpegren er fortsatt ubrukt, ikke godkjent chipstøtte. |
| `motor.py:410`, `motor.py:440`, `motor.py:482`, `motor.py:546`, `motor.py:585` | **Tilsiktet generalisering**, med valideringshull F1/F2/F7: tomme chipsett, begrensede chipdatoer, null bytter, kort horisont og felles datoer. Tidligste BB vinner ved lik score, som gammel nanargmax. FH-start var 16 (gammel linje 493/514), nå parameter/første tilgjengelige (`motor.py:46`, `motor.py:456`, `motor.py:498`). Backup-FH følger tilgjengelige datoer. Dette kan endre søket uten å endre verdien av en gitt plan. |
| `motor.py:544`, `motor.py:592`, `kjor.py:156` | **Avvik i rapportering**: G-spredning er rettet (F8); generiske kolonnenavn, eksplisitt blend og ut/inn-ID-er. FT-følsomheten bruker felles chipdatoer som GW10 r2 (`modell_r2.py:109`), mens r1 valgte BB på nytt (`modell.py:555`). Skadeintervaller er egne tabeller i stedet for G/alternativ-kolonner; egne alternativers frie rutenett fra r2 linje 62–78 mangler (F11). Rapporttekst og Groß-spesialtest er bevisst utelatt etter plan-v2 D. |
| `skadesim.py:15`, `skadesim.py:25`, `skadesim.py:51` | **OK**: samme fravær fra andre runde, varigheter 1/2/3/6, skjulte framtidige skader, felles verdener på tvers av planer/rater/poengsett og samme parvise statistikk som `modell_r2.py:83`–104. R2s 200 trekk = nøyaktig to 100-blokker; egen test bekrefter generator og 200 verdener, pluss stabilt 20-prefiks. De første 20 reelle A/B-banene gir avvik 0. Ved 150 trekk avviker varighet 101–150 fra gammel parameterisert R2-generator; motoren fyller alltid hele 100-blokker. **AKSEPTERT**, sikrer at tidligere verdener ikke endres når antallet økes. Ved annet antall enn 100 ville også R1s opprinnelige engangsblokk avvike. Standardrater er R2s 1/2 %, ikke R1s ekstra 3 %. Vekt er parameter; referanse er første plan (A i CLI). Uten BB er F6 et nytt hull. |

**F12 — ny feil, påvirker beslutninger:** `poeng.py:308` returnerer tomt `retur` når en minuttabell leses. `poeng.py:292` nuller dermed alle API-blokkerte spillere selv om den frosne tabellen inneholder en kjent retur. Minimalt eksempel i `motorkontroll_ekvivalens.py`: syntetisk id 3, status i/0 %, overstyring R7–9 med p_start=0,8 og minutter=70. R7 får codex **5,1691075652**, repo **6,125**. Skriv `minutter.csv`, les den som `minuttabell`, beregn igjen: samme minuttverdier, men begge poeng **0**, retursett 3→0. **GJENSTÅR.** Frys/innlesing må bevare retursemantikken eller avvise denne kombinasjonen tydelig. Ikke korriger ved å oppheve API-blokkeringen for alle positive tabellrader uten en avklart kontrakt.

Testlogg: `motorkontroll-data/ekvivalens-naa.log`. Ingen ny tung GW10-søkekjøring eller langsom pytest; eksisterende akseptansetester og den uavhengige R11-prøven dekker tall for gyldige, like planer.

## Steg 4: chipgrenser og analyseinnganger (kontroll 21. november, før 4ed2cbc)

Logg: `motorkontroll-data/chips-naa.log`; selvstendig reproduksjon: `motorkontroll_chips.py`.

- **OK: tomme lister** betyr `chips={"BB": [], "FH": []}` i det dokumenterte objektformatet. Full `kjor.kjor`/Motor gir én rutenettcelle uten chips, BB/FH=None og ingen chip i felles planer. Dette dekker ikke F6: bestilt simulering hoppes fortsatt over. Utelatt `chips` er en annen kontrakt: standard er alle horisontens BB-runder og FH fra neste runde (`motor.py:43`).
- **OK: R20-vindu for støttede chips.** Full syntetisk kjøring R20–21, BB20/FH21, gir kontroll OK og gjenregningsavvik 0. Prognosehorisonter R20–29 og R20–38 godtas, R20–39 stoppes. FH20 stoppes både i `kjor.py:70` og `motor.py:45`. Dette godkjenner vindusgrensen, ikke hele R20-ukeanalysen: WC/TC/FH nå mangler fortsatt som planlagt før R20.
- **OK: WC/TC og FH nå.** Faktiske CLI-prosesser med `--bare-poeng` og `chips={"WC":[6]}`, `{"TC":[6]}`, `{"FH":[6]}` avslutter med feiltekst før spillerpoeng. Det samme gjelder `felles_chip` WC/TC. Full `kjor.kjor` er allerede prøvd i steg 2. Direkte `Motor(..., wc_runder=[6])`/`tc_runder=[6]` og `m.bane(..., wc=6)`/`tc=6` stopper med TypeError «unexpected keyword argument»; ingen plan produseres (`motor.py:27`, `motor.py:333`). FH nå stoppes i konstruktørens `fh_runder`, `bane`, `faste_planer` og ved analyse med `fh_start` nå (`motor.py:45`, `motor.py:344`, `motor.py:587`). Meldingen i sistnevnte sier FH må ligge etter første runde. Ikke overselg dette som et eget WC/TC-validerings-API: parametrene finnes ikke. `ny_tropp(fh=False)` (`motor.py:202`) og `rullering(wc=...)` er gamle interne hjelpere, ikke komplette WC-planer; fortsatt uten støtte/testgaranti.
- **OK: ren kollisjon** med både BB7 og FH7 faktisk tilgjengelige stopper i `alternativ` med «samme runde». `faste_planer` avviser utilgjengelig FH9. Det er altså ikke bare den tomme tilgjengelighetslisten som forårsaket avvisningen i steg 2.
- **FEIL, F7: direkte Motor mangler vindusgrensen.** Lag syntetisk `Uke` R19–20 og `Motor(u, pr, bb_runder=[20], fh_runder=[])`; `faste_planer({'A': u.ORIG}, 20, None)` gir BB20 og 89,7732035034 blend. R38–39 med BB39 gir 69,174345111. Begge burde stoppes etter plan-v2 D. CLI er rettet, men en bruker av biblioteket kan omgå kontrollen. Legg tilsvarende grense i Motor/felles validator; ingen prognosemodellendring trengs.
- **FEIL, F1: utilgjengelig FH omgår deler av API-et.** `m=Motor(u, pr, bb_runder=[], fh_runder=[])`; både `m.alternativ('A', m.bane(u.ORIG, fh=7), None)` og `m.ft_folsomhet({'A':u.ORIG}, None, 7, [2])` lykkes. `bane` sjekker bare horisonten. `fh_start=7` med samme tomme liste brukes også i kandidatrangeringen. Samle valideringen slik at disse inngangene følger samme chipstatus som `faste_planer`.
- **FEIL, F2: full kjøring bekrefter silent feil.** `ft_folsomhet=[-1]` gir fire minuspoeng for rull og kontroll OK; `vekt_codex=2` godtas og blander som 2×codex−repo; `gratisbytter=1.9` rapporteres i kontrollen, men banen bruker FT=1. Dette er ikke bare ubrukte konstruktørverdier. Krev heltall 0–5 for FT/følsomhet og endelig vekt i [0,1] i CLI og Motor, uten å avrunde ugyldige tall til gyldige.

**Minimale resterende reproduksjoner fra steg 2:** F3: `rad(13, fra=8, til=7, faktor='feil tall')` i `bruk_overstyringer` lar hele tabellen være uendret uten feil (`poeng.py:126`); datointervall og tall må valideres før løkken. F6: tomme chip-lister og `skadesim={"trekk":2,"rater":[0.02]}` gir `kontroll.status="OK"`, ingen `skadesim`-nøkkel og ingen simuleringsfil (`kjor.py:185`). F9: `rad(13,p_start=0,forventede_min=30)` gir PP=0 og positive poeng som vist i tabellen; denne kombinasjonen må avvises eller modelleres konsistent, ikke bare sjekkes som to separate intervaller. p_start=0 er ikke alene ulovlig (en innbytter kan spille); problemet er positive minutter/poeng når beregnet P(spiller)=0. F11: `maks_bytter=0`, BB=[6,8], FH=[7,9] og eget `Claude_test` (id 3→4) gir forslaget i felles planer, men rutenettet har bare standardplanens bytteantall 0. Det finnes dermed ingen fri BB/FH-sammenligning for forslaget, i strid med plan-v2 A og funksjonen i GW10 r2. Feilen gjelder sammenligningsdekningen, ikke poengene på de oppgitte felles datoene.


## Kontroll av commit 4ed2cbc — punkt 2 (23. november)

Commit og tester lest. Claudes langsomkjøring i `samarbeid/modell/claude/pytest-langsom-4ed2cbc.log`: **62 bestått, 2 hoppet over, 250,92 s**. Codex kjørte standardtestene med Anaconda og uten pytest-cache: **60 bestått, 2 hoppet over, 74,38 s**. Fire egne kontrollskript ble kjørt sekvensielt; logger står i `motorkontroll-data/*-4ed2cbc.log`.

| Funn | Status nå | Alvorlighet | Kontroll og begrensning |
|---|---|---|---|
| F1 | RETTET | påvirker beslutninger før rettelsen | CLI og direkte Motor avviser `fh_start` uten tilgjengelig FH. `bane`, `alternativ` og `ft_folsomhet` avviser FH utenfor `fh_runder`; FH i inneværende runde stopper. `motorkontroll_chips.py`. |
| F2 | RETTET | påvirker beslutninger før rettelsen | CLI og Motor avviser FT/ft_folsomhet som ikke er heltall 0–5 og vekt utenfor [0,1]. Testet −1, 6, 1,9 og vekt 2 gjennom begge innganger. `kjor.py:64–78`, `motor.py:35–55`, `motor.py:355–359`, `motor.py:625–630`. |
| F3 | GJENSTÅR | kosmetisk for gjeldende poeng; konfigurasjonsfeil rapporteres ikke | Omvendt intervall, desimalrunder, tekstfaktor, negativ faktor og intervall helt utenfor horisonten avvises (`poeng.py:126–154`). Men `gw_fra=5, gw_til=7` på horisont 6–9 godtas; radens runder 6–7 endres, runde 5 klippes bort lydløst (`poeng.py:143–145`). Minimalt eksempel: `rad(id=13, fra=5, til=7, faktor=.5)`. Avklar om delvis overlapp skal avvises, slik oppdraget sier, eller om klipping er tilsiktet og dokumentert. |
| F4 | RETTET | påvirker beslutninger før rettelsen | WC/TC i `chips` og `felles_chip` stoppes med forklaring i CLI; Motor har ingen slike parametre. Kontrollskript `motorkontroll_chips.py`. |
| F5 | RETTET | kosmetisk | README presiserer at spillerpoeng fryses av prognoseskriptet; motoren kan skrive dem på nytt etter kontrakten. `samarbeid/motor/README.md`. |
| F6 | RETTET | påvirker beslutninger før rettelsen | Full kjøring med BB-liste tom og `skadesim={trekk:2,rater:[.02]}` skriver 2 trekkrader for totalen uten BB; `kontroll.json` oppgir `{BB:null,FH:…}`. R12-scenarioet er dermed dekket. `kjor.py:223–236`, `skadesim.py:37–83`. |
| F7 | GJENSTÅR | påvirker beslutninger ved direkte Motor-konfigurasjon | CLI avviser chipdatoer utenfor chipvinduet og horisont over vinduet. Motor avviser horisont R19–20/R38–39. Men konstruktøren filtrerer `bb_runder`/`fh_runder` mot `u.GWS` uten feil (`motor.py:50–51`): `Motor(u_R6–9, pr, bb_runder=[20], fh_runder=[])` lykkes og ender med `bb_runder=[]`. Oppgitt chipdato 20 forsvinner uten melding. Direkte Motor må avvise datoer utenfor vinduet/horisonten før filtreringen. |
| F8 | RETTET | rapportering, ikke rangering | Ny kjøring av kapteinsrader finner ingen spredningsavvik. `kanttilfeller-4ed2cbc.log`. |
| F9 | RETTET | påvirker beslutninger før rettelsen | `p_start=0, forventede_min=30` for id 13 stopper med tydelig `P(spiller)=0`; lovlig `p_start=0` med innhoppsmulighet kan fortsatt gi positiv sannsynlighet. `poeng.py:274–277`. |
| F10 | RETTET | påvirker beslutninger før rettelsen | `--frys` sjekker begge kilder og mål før kopiering; forsøk på eksisterende andre fil etterlater ikke første fil. `kjor.py:31–47`. |
| F11 | RETTET | påvirker beslutninger før rettelsen | Eget forslag får fire rader for BB 6/8 × FH 7/9 i `chiprutenett_egne.csv`. Sammenligningen mot standardrutenettet stemmer; ingen planpoeng endres. `kjor.py:209–211`, `motor.py:606–623`. |
| F12 | RETTET | påvirker beslutninger før rettelsen | `minutter.csv` skriver `retur`, og innlesing gjenoppretter det. Id 3 i R7 beholder codex 5,1691075652 og repo 6,125 før/etter frysing; PP og begge matriser er array-identiske. `poeng.py:177–200`, `kjor.py:162`. |

De gyldige tallene endret seg ikke i kontrollerte planer: GW10-akseptansetester passerer; syntetiske dobbel-/blanke tester består; F12 gir bit-for-bit like poeng ved frys/innlesing; R20 BB20/FH21 gir samme gjenregning (avvik 0); første 20 skadesimverdener mot GW10 r2 er identiske. F6 og F11 tilfører dekning/utdata, F9 stopper bare den inkonsistente kombinasjonen. Nye beregninger for BB uten chip bruker totalen uten BB som referanse.

Andre mulige feil som ble sjekket i endringene: `kontroll.json` i full kjøring registrerer både simulert og eksplisitt hoppet over. `--bare-poeng` avslutter før analysen og oppgir ikke skadesimstatus; det er et separat modusvalg og påvirker ikke R12 fullkjøring. Skadesimrapporten `simuler_raa` har nå H+1 rader; eksisterende testdekning og R12-eksemplet bruker riktig siste rad for uten-BB-totalen.

## Endelig dom før d428750

For R12 via den validerte CLI-rutinen er de åtte rapporterte rettelsene kontrollert; R11 brukte BB, og R12s fullkjøring simulerer nå uten BB. `fh_start` kan fortsatt styres i rutinen: bruk samme lovlige verdi i Codex- og Claude-analysen for sammenlignbare kandidater. Å søke over flere FH-datoer kan forbedre kandidatdekningen senere, men er ikke nødvendig for å regne gyldige planer før R12.

Før en endelig «klar til bruk»-dom gjenstår likevel to avgrensede robusthetsrettinger i biblioteket: (1) `Motor` må avvise eksplisitte chiprunder den filtrerer vekk (F7), og (2) `bruk_overstyringer` må enten avvise intervaller som bare delvis ligger i horisonten eller dokumentere og teste klipping (F3). CLI-konfigurasjon for den aktuelle kjøringen avviser chiprunder utenfor vinduet; F3-klippet endrer ikke de horisontrundene den faktisk regner.

## Kontroll av d428750 — punkt 2

Committen ble lest sammen med README og de nye testene nederst i `samarbeid/motor/tester/test_oppsett.py`. Den avviser chipdatoer etter horisontens slutt i både CLI-validatoren og `Motor`; overstyringsrader må ligge helt i horisonten. README dokumenterer regelen og hvordan et lengre fravær avgrenses. Mine reproduksjoner logger begge funn som `RETTET` i `motorkontroll-data/chips-d428750.log` og `kanttilfeller-d428750.log`.

| Funn | Status etter d428750 | Alvorlighet før rettingen | Kontroll |
|---|---|---|---|
| F3 | **RETTET** | kosmetisk for gjeldende poeng, men feil oppsett ble skjult | Rader 5–7 og 8–10 på horisont 6–9 avvises med `ValueError`; hele raden 6–9 godtas av ny test. Kode: `samarbeid/motor/poeng.py:131–135`. |
| F7 | **RETTET** | påvirker beslutninger | Direkte `Motor` med BB20 eller FH10 på horisont 6–9 gir `AssertionError`; CLI avviser chiprunder utenfor `runde`–`horisont_til`. Kode: `samarbeid/motor/motor.py:51–54`, `samarbeid/motor/kjor.py:87–92`. |

Minimale feiltilfeller: F3 `gw_fra=5, gw_til=7` (eller `8–10`) på horisont 6–9; F7 `Motor(u_R6–9, pr, bb_runder=[20], fh_runder=[])` eller CLI `chips.BB=[18]` med `horisont_til=17`. Nå stoppes begge med melding. Gyldig rad `gw_fra=6, gw_til=9` og BB/FH-datoer i horisonten godtas.

Gyldighetskontrollen ga: GW10 runde 10, horisont 10–19, BB 10–19/FH 11–19 og åtte overstyringsrader innenfor; GW11 runde 11, horisont 11–19, BB 11–19/FH 12–19 og seks rader innenfor; typisk R12 runde 12, horisont 12–19, BB tom og FH 13–19. Alle tre oppsett godtas. Se `motorkontroll-data/gyldige-oppsett-d428750.log`.

Ingen poeng-, planrangerings- eller søkeberegning er endret i d428750; diffen består av validering, README og tester. Claudes langsomtest på committen bestod med **66 bestått**; standardtesten her ga **64 bestått, 2 hoppet over**. GW10-ende-til-ende-testen sammenligner fem alternativer mot `alternativer_r2.csv` innen toleranse og forventer fortsatt plan B med BB12/FH13. Det foreligger derfor ikke tegn til endrede tall for gyldige planer.

## Endelig dom (punkt 3)

klar til bruk fra R12

De siste to funnene er rettet og kontrollert. R12-oppsettet med BB brukt i R11 (tom BB-liste), FH 13–19 og horisont 12–19 passerer. Bruk samme lovlige `fh_start` i Claude- og Codex-analysen for sammenlignbare søkerangeringer; å utvide søket over flere FH-datoer er ikke en forutsetning for gyldig poengberegning.
