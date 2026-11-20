# Beslutning runde 11 (2026/27)

Tatt av Claude 2026-11-20 ca. 11:10 UTC, etter analyse og to runder med Codex (Codex mistet forbindelsen én gang og stoppet én gang på
bruksgrensen; se `oppgaver.md`). Prognosen er frosset i `prognose/prognose_R11.json` (sjekksummer i `prognose/SHA256SUMS`) og skal ikke
endres etter fristen lørdag 21. november 11:00 UTC (12:00 norsk tid).

Tallpar er codex / repo_hybrid. Alle forventede poeng er modellresultater, ikke observasjoner.

## Handling nå

| | |
|---|---|
| Bytte | **Muharemović → Van Hecke** (1 gratisbytte) |
| Poengtrekk | 0 |
| Bank | £0,4m (salg 5,1, kjøp 5,1). Stiger Van Hecke 0,1 i natt: £0,3m |
| Gratisbytter | antatt 3 → 3 til R12 (2–4 mulig) |
| Chips | **Bench Boost nå (R11).** Free Hit: planleggingsdato R15, avgjøres senere. Wildcard 1 er brukt (R9) |

**Startellever (3-5-2):** Tzolakis; Gabriel, Van Hecke, De Cuyper; Ødegaard, Tavernier, Groß, Rudoni, Mbeumo; Isak, Haaland.
**Kaptein:** Haaland. **Visekaptein:** Gabriel.
**Benk (teller med Bench Boost):** Trafford (GK); 1. Barry, 2. Silva, 3. Dasilva.

Med Bench Boost teller alle 15, så hvem som står på benken, betyr bare noe for kapteinen.
Rekkefølgen over gjelder hvis Bench Boost likevel ikke aktiveres.

## Rullerende plan R11–R19 (alt etter R11 er foreløpig)

| Runde | Frist (UTC) | Plan |
|---|---|---|
| R11 | 21. nov 11:00 | Muharemović → Van Hecke. **Bench Boost.** |
| R12 | 27. nov 18:30 | *Foreløpig:* 2 av 3 gratisbytter. Modellbanen: Ødegaard, Dasilva → Le Fée, Muharemović. Ødegaard-regelen gjelder (se under). Isak → N.Jackson vurderes (Cs fordel, se under). |
| R13 | 1. des 18:30 | *Foreløpig:* rull. |
| R14 | 5. des 11:00 | *Foreløpig:* rull. |
| R15 | 12. des 13:30 | *Foreløpig:* **Free Hit** (planleggingsdato; for B foretrekker codex FH14 og repo FH12, alle innen 0,4). |
| R16–R18 | 19.–29. des | *Foreløpig:* gratisbytter etter behov (Van Hecke → Konsa i modellbanen). Gratisbyttene når taket på 5. |
| R19 | 1. jan 18:30 | Free Hit 1 utløper. Bygg mot nytt chipsett fra R20. |

## Hvorfor

**Muharemović → Van Hecke (plan B).** Positiv mot rull i begge poengsett ved alle antall gratisbytter og begge skaderater:

| B mot rull, R11–R19 (Codex, BB11/FH15) | codex / repo | blanding |
|---|---|---|
| Nominelt, 2 / 3 / 4 FT | +0,92 / +1,45; +0,66 / +1,11; +0,27 / +1,29 | +1,2; +0,9; +0,8 |
| 3 FT, 1 % nye fravær (100 parede verdener) | +0,71 / +0,80 | +0,75 (B best i 87 %) |
| 3 FT, 2 % nye fravær | +1,08 / +0,49 | +0,79 (B best i 86 %; p10–p90 −0,17 til +1,32) |

Ukemotoren (uavhengig kode, samme tall for samme plan) gir +0,63 / +0,68 ved 1 % (88–90 % vinnende verdener). Gevinsten er liten,
men byttet bruker et gratisbytte som ellers går tapt: i både A og B står gratisbyttene på taket (5) i R16–R18. Med Bench Boost i R11
teller hele forskjellen Van Hecke mot Muharemović: +0,94 / +1,47 i R11. Van Hecke (TOT hjemme mot Ipswich) er bare kjøpbar ved å selge
Muharemović (Dasilva gir for lite: 0,4 + 4,0 < 5,1).

**Ikke Codex' forslag C (Dasilva, Mbeumo → Van Hecke, Le Fée).** C har høyest forventning i 50/50-blandingen. Mot B over R11–R19:

| C minus B | codex / repo | blanding | Paret p10–p90, blanding |
|---|---|---|---|
| 1 % nye fravær | −1,73 / +4,48 | **+1,38** (C best i 91 %) | +0,16 til +2,08 |
| 2 % nye fravær | −1,44 / +3,70 | **+1,13** (C best i 89 %) | −0,09 til +2,35 |
| Nominelt, 2 / 3 / 4 FT | +0,48 / +0,71; −2,03 / +5,67; −1,96 / +3,49 | +0,6; +1,8; +0,8 | |

Claude velger B og gir dermed avkall på ca. 1,1 poeng i blandingens forventning (Codex' tall ved 2 %), fordi:
1. **Poengsettene er uenige om fortegnet** ved 3 og 4 gratisbytter. B er positiv mot rull i begge; C er negativ mot rull i codex-settet.
2. **Forskjellen er på størrelse med søkestøyen.** Cs totaler er ikke stigende i antall gratisbytter, slik de ville vært med en optimal
   byttepolitikk: codex 569,08 → 566,59 fra 2 til 3 FT, repo 628,31 → 626,48 fra 3 til 4 FT. Byttepolitikken finner altså svært ulike
   senere baner for C, med 2–5 poengs utslag. A og B er stigende. Med 2 og 4 FT er C bare +0,6 og +0,8 foran i blandingen.
3. **Fordelen ligger i senere bytter.** I R11 er C +0,48 / +0,71 foran B. Uten flere bytter er B +2,6 / +1,2 foran over R12–R14 i begge
   poengsett (Mbeumo foran Le Fée; frosset prognose). Cs fordel krever at modellbanen i R12 kjøper Mbeumo tilbake og selger Isak for
   N.Jackson, som bare repo-settet liker (det samme gjaldt Isak i R10). Det kan gjøres fra B neste uke, med 3 gratisbytter, hvis begge
   poengsett da støtter det.

Codex har rett i at kravet om enighet mellom poengsettene er et konservativt tilleggskriterium og ikke en del av den avtalte blandingen.
Det står ikke i `RUTINE.md`; det er praksis siden gw08 («en konkret tropp må testes under begge poengsettene»). Claude kalte det
«fast regel» i kritikken; det var for sterkt. Med 2 gratisbytter er C foran B i begge poengsett (+0,48 / +0,71, alt i R11; nominelt,
ikke skadetestet), og da velges C etter samme regel.

**Ikke rull.** B slår rull i begge poengsett ved 2, 3 og 4 gratisbytter, i begge regnemotorene og i 86–87 % av skadeverdenene.

**Ødegaard beholdes.** Regelen fra 19. november står: han selges bare hvis de endelige tallene viser mer enn ca. 3 poengs gevinst
over R11–R19 i begge poengsett. Claudes første forslag (Ødegaard, Dasilva → Le Fée, Van Hecke) er det nærmeste: i motorens
prøvekjøring (bare til sammenligning) +1,36 / +1,45 mot rull og 97–98 % vinnende skadeverdener, altså ca. +0,7 / +0,5 foran B.
Det er under terskelen. Modellbanen selger ham i R12 (ARS hjemme mot MCI); det vurderes neste uke med samme regel.

**Bench Boost nå.** Nominelt er datoen flat. For B (Codex' rutenett, R11–R19):

| FH | BB11 | BB18 | BB19 |
|---|---|---|---|
| FH12 | 568,63 / 623,36 | 568,65 / 622,98 | 568,36 / 622,69 |
| FH14 | 568,96 / 623,00 | 568,98 / 622,61 | 568,70 / 622,32 |
| FH15 | 568,62 / 622,64 | 568,64 / 622,25 | 568,35 / 621,97 |

Med nye fravær vinner BB11 i begge poengsett, ved begge rater og begge FH-datoer (Codex' parede test, `codex/bb_skade.csv`, 100 verdener):

| B, FH15 | BB11 − BB18 | BB11 − BB19 |
|---|---|---|
| 1 % | +0,40 / +0,81 (blanding +0,60, p10–p90 +0,16 til +1,16) | +0,30 / +0,71 (+0,51, p10–p90 +0,09 til +0,65) |
| 2 % | +1,00 / +1,41 (+1,21, p10–p90 +0,14 til +4,02) | +0,31 / +0,72 (+0,51, p10–p90 −0,12 til +1,08) |

FH12 gir nesten de samme tallene. Alle 15 er friske nå, og benken (Trafford, Barry, Silva, Dasilva) har vanlige kamper i R11.
Codex er enig i BB11.

**Kaptein Haaland** (6,18 / 8,33) foran Isak (5,23 / 4,82) og Gabriel (4,93 / 6,26) i begge poengsett. Visekaptein Gabriel
(best av resten i blandingen). Haaland har hatt 2 poeng to runder på rad, men det endrer ikke forventningen. Repo overvurderer spisser
over 10,0 (måling over tre sesonger: +1,2 per runde), codex mindre (+0,4); han er kaptein også etter en slik justering. Codex er enig.

## Forventning (modellresultater)

| | codex | repo_hybrid |
|---|---|---|
| R11, anbefalt med Bench Boost, fast lag uten autobytter (frosset) | 74,3 | 84,1 |
| R11, rull med Bench Boost (frosset) | 73,4 | 82,7 |
| R11, anbefalt minus C (frosset) | −0,5 | −0,7 |
| R11–R14, anbefalt minus C, fast lag uten flere bytter (frosset) | +2,1 | +0,5 |
| R11–R19, B mot rull, 2 % nye fravær (Codex, 3 FT, BB11/FH15, med modellbanens senere bytter) | +1,08 | +0,49 |
| R11–R19, B med BB11/FH15, nominelt | 568,6 | 622,6 |

## Usikkerheter

1. **Gratisbytter:** antatt 3 (2–4 mulig). Simen ser tallet i appen. B ved 3 og 4; ved 2 er C litt foran i begge sett og velges da.
2. **Lagnyheter fredag:** ingen i troppen eller Van Hecke har skade- eller tvilsmerke i FPL (sjekket 20. nov 11:00 UTC).
   Pressekonferanser for blant annet ARS, MCI, LIV, MUN, BHA, TOT og EVE kom etter at beslutningen ble tatt.
3. **Bench Boost-datoen:** skadetesten taler for nå. Ikke modellert: en eventuell dobbeltrunde før R19 (ingen er annonsert; taler for å
   vente) og målrettet styrking av benken med gratisbytter som ellers går tapt i R16–R18 (taler for å vente).
4. **Modellbanen etter R11** (Ødegaard ut i R12, tilbakekjøp av Muharemović, Free Hit R15) er foreløpig og regnes på nytt hver uke.
   Byttepolitikken er heuristisk; langtidsrangeringen mellom nære planer er usikker med 2–5 poeng (punkt 2 under C).
5. **Priser:** alle tall bruker prisene fra 19. november (N.Jackson har steget til 7,2 siden).

## Før fristen (lørdag 12:00 norsk tid)

- Sjekk antall gratisbytter i appen. **3 eller 4** (antatt): Muharemović → Van Hecke. **Bare 2:** gjør Codex' C i stedet:
  Dasilva → Van Hecke og Mbeumo → Le Fée (bank £1,5m). Le Fée tar Mbeumos plass i elleveren, Muharemović står på benken der Dasilva sto.
- Gjør byttet **fredag kveld etter pressekonferansene**, helst før prisjusteringen i natt (ca. 02:30 norsk tid): Van Hecke er kjøpt inn
  av over 300 000 denne runden og kan stige 0,1. Det stopper ikke byttet, men koster £0,1m i bank.
- **Aktiver Bench Boost**, sett kaptein Haaland og visekaptein Gabriel.
- **En spiller meldes ute før fristen:** med Bench Boost teller alle 15, så bruk et av de to gjenværende gratisbyttene på å erstatte ham.
- **Haaland tvilsom:** kaptein Gabriel, vise Isak.

## Uenighet mellom agentene

Claude foreslo først Ødegaard, Dasilva → Le Fée, Van Hecke (før Codex' og motorens tall). Simens opplysning om Ødegaards form gjorde at
Ødegaard beholdes. Codex foreslo C (Dasilva, Mbeumo → Van Hecke, Le Fée) med BB11. Etter kontrollen (`claude/kritikk-av-codex.md`)
foreslo Claude B med BB11.

Codex (`codex/kontroll.md`): enig i BB11, Haaland og Gabriel. Uenig i at B er modellens beste handling: C har fortsatt høyest
forventning i blandingen (+1,13 mot B ved 2 %), og kravet om enighet mellom poengsettene er et konservativt tilleggskriterium.
Codex kaller B «et forståelig robusthetsvalg» hvis forventningstapet oppgis. Det er gjort over. Uenigheten står: den gjelder
beslutningsregelen, ikke tallene, og bør avklares i rutinen (se `samarbeid/modell/STATUS.md`, punkt 3).

Kritikken endret: Codex' C ble ikke fulgt. BB11 ble bekreftet med skadetesten. Claudes «fast regel» om enighet mellom poengsettene
ble korrigert til praksis, og forventningstapet ved B er oppgitt.
