# Beslutning runde 12 (2026/27)

Claude tok beslutningen 2026-11-26 ca. 08:55 UTC, etter analyse og to runder med Codex (modell `gpt-6-luna`; se `oppgaver.md`).
Prognosen er frosset i `prognose/prognose_R12.json`, med sjekksummer i `prognose/SHA256SUMS`. Den skal ikke endres etter fristen
fredag 27. november 18:30 UTC (19:30 norsk tid).

Tallpar er codex / repo_hybrid. Alle forventede poeng er modellresultater, ikke observasjoner. Dette var en automatisk kjøring, og Simen
har ikke gitt noen opplysninger denne uken.

## Handling nå

| | |
|---|---|
| Bytter | **Dasilva → Justin (LEE) og Silva → Bogle (LEE)** (2 gratisbytter) |
| Poengtrekk | 0 |
| Bank | £0,1m (salg 4,0 + 5,0, kjøp 4,5 + 4,8). Stiger Bogle 0,1 i natt, blir banken £0,0m, og byttet går fortsatt |
| Gratisbytter | Antatt 3 → 2 til R13 (1–3 er mulig) |
| Chips | Ingen. Free Hit 1: planleggingsdato R15. Bench Boost (R11), Wildcard (R9) og Triple Captain (R3) er brukt |

**Startellever (4-3-3):** Trafford; Gabriel, De Cuyper, Bogle, Justin; Tavernier, Groß, Mbeumo; Barry, Isak, Haaland.
**Kaptein:** De Cuyper. **Visekaptein:** Haaland.
**Benk:** Tzolakis (GK); 1. Ødegaard, 2. Van Hecke, 3. Rudoni.

Leeds får tre spillere (Trafford, Bogle og Justin), som er maks. LEE har COV hjemme i R12.

## Rullerende plan R12–R19 (alt etter R12 er foreløpig)

| Runde | Frist (UTC) | Plan |
|---|---|---|
| R12 | 27. nov 18:30 | Dasilva → Justin, Silva → Bogle. Kaptein De Cuyper. |
| R13 | 1. des 18:30 (midtuke) | *Foreløpig:* 2 gratisbytter. Bruk dem på skader fra helgen, ellers etter ny beregning. |
| R14 | 5. des 11:00 | *Foreløpig:* bytter etter ny beregning. Ødegaard-regelen gjelder fortsatt. |
| R15 | 12. des 13:30 | *Foreløpig:* **Free Hit** (beste dato i codex-settet for denne planen; R13 er like god i repo-settet). |
| R16–R18 | 19.–29. des | *Foreløpig:* gratisbytter etter behov. |
| R19 | 1. jan 18:30 | Siste runde Free Hit 1 kan brukes. Bygg mot nytt chipsett fra R20. |

## Hvorfor

**Dasilva og Silva ut, Justin og Bogle inn (Codex' G_keep).** Planen er positiv mot rull i begge poengsett i alle Codex' tester:

| G_keep mot rull | codex / repo | blanding |
|---|---|---|
| R12–R19 med modellens senere bytter, FH15, nominelt | +2,42 / +1,04 | +1,73 |
| R12–R19, 1 % nye fravær (100 parede verdener) | +2,03 / +1,35 | +1,69 (p10–p90 +0,95 til +2,40) |
| R12–R19, 2 % nye fravær | +1,97 / +1,21 | +1,59 (p10–p90 +0,34 til +2,77) |
| Fast tropp R12–R15 uten senere bytter (eksakte autobytter, FH15) | +0,06 / +0,85 | +0,46 |
| R12 alene | +1,08 / +1,19 | +1,14 |

Dasilva var utenfor laget i R11 (0 minutter), og en forhåndsomtale melder ham skadet. Med bank 0,4 kan han bare erstattes av en forsvarer
til 4,4 eller mindre. Beste slike var Mitchell, med −0,85 i blandingen mot B, og den er svakere enn begge. Silva er bedre enn både Bogle
og Justin over R12–R19 (35,4 / 35,3 mot 29,5–32,5). Han selges for å finansiere byttet og fordi Bogle og Justin starter i R12.
Gevinsten etter R12 ligger derfor mest i modellens senere bytter. Med fast tropp er den nesten null (+0,06 / +0,85), men ikke negativ
i noen av poengsettene.

**Ikke Claudes forslag P (Ødegaard → Le Fée, Dasilva → Konsa).** Mot G_keep gir P −2,70 / +0,04 over R12–R19 og −0,39 i blandingen
ved 2 % nye fravær (P best i 33 % av verdenene). P selger dessuten Ødegaard uten å oppfylle regelen.
Den grove kontrollen i `claude/forslag.md` brukte repoets rå xP over fem runder, uten minuttoverstyringer og uten codex-settet.
Den var for optimistisk.

**Ødegaard beholdes.** Beste salg mot beste behold gir −0,56 / +1,39 over R12–R19. Regelen krever mer enn ca. 3 poeng i begge
poengsett. Codex' C (Ødegaard, Dasilva → Justin, Le Fée) har høyest blandingsverdi (+2,14 mot rull, +0,41 mot G_keep), men
poengsettene er uenige om salget.

**Ikke rull og ikke B (Silva → Muharemović).** G_keep slår begge i blandingen: +1,73 mot rull og +0,67 mot B. B beholder den skadde
Dasilva og gir −0,62 / +0,49 med fast tropp. Ett poengtrekk (D4, fire bytter) gir −1,06 mot rull og forkastes.

**Kaptein De Cuyper, vise Haaland.** I anbefalt tropp er De Cuyper øverst i begge poengsett (ekstrakopi 5,45 / 6,41, blanding 5,93),
foran Haaland (5,21 / 6,28, blanding 5,74) og Groß (5,68). Faktoren 0,95 for BHAs europakamp torsdag er med (p_start 0,895).
Haaland spiller borte mot Arsenal, og repo-settet har overvurdert ham i alle fire rundene i prognoseevalueringen (−4,8 per runde, n = 4,
bare én spiller). Med skjevhetene lagt til i følsomhetstesten er De Cuyper fortsatt øverst. Forskjellen er under 0,2 poeng i blandingen,
så Haaland som kaptein er nesten like godt. En forsvarer som kaptein er uvanlig, men begge poengsettene peker samme vei.

**Prognoseevalueringen** har for første gang tydelige skjevheter etter kriteriet. Codex undervurderer GKP < 5,0 (+0,97), MID 5,0–7,4
(+0,39) og FWD 5,0–7,4 (+0,74), og repo overvurderer MID 7,5–9,9 (−1,40) og FWD ≥ 10,0 (−4,76, bare Haaland). Alle bygger på fire runder.
De er brukt bare som følsomhetstest for kapteinsvalget og endrer ikke valget. Modellen er ikke endret.

## Forventning (modellresultater)

| | codex | repo_hybrid |
|---|---|---|
| R12, anbefalt ellever med kaptein, fast lag uten autobytter (frosset) | 55,3 | 60,9 |
| R12, rull (frosset) | 54,8 | 60,1 |
| R12, anbefalt minus rull (frosset) | +0,6 | +0,8 |
| R12–R14, anbefalt minus rull, **samme R12-ellever låst i tre runder** (frosset) | −1,5 | −2,9 |
| R12–R19, G_keep mot rull, 2 % nye fravær (Codex, med senere bytter og FH15) | +1,97 | +1,21 |

Den frosne tretrundersraden låser R12-elleveren, med Bogle og Justin på banen, også i R13–R14. I Codex' faste tropp-test der elleveren
velges på nytt hver runde, er planen omtrent lik rull over R12–R15 (+0,06 / +0,85). Byttet er altså en R12-gevinst pluss fleksibilitet.

## Usikkerheter

1. **Gratisbytter:** antatt 3 (2–4 er mulig). Med bare 2 velger Codex' byttesøk B (Silva → Muharemović, 1 bytte) som beste plan
   som beholder Ødegaard. Da følges B. Med 4 velger søket tre bytter, men poengsettene spriker; G_keep står da.
2. **Dasilva:** skaden er ikke bekreftet (API-status `a`). Er han frisk og spiller, er salget mindre viktig. Han erstattes likevel av
   en spiller som starter.
3. **Mbeumo:** 21 minutter i R11 uten forklaring. Han starter med p_start 0,8. Meldes han ute, se under.
4. **Liten gevinst og senere modellbytter:** forskjellene mellom planene er 0,4–2,4 poeng over åtte runder, på størrelse med usikkerheten i byttesøket.
5. **Priser:** prisene fra 26. nov morgen. Bogle (76 000 inn denne runden) kan stige i natt.

## Før fristen (fredag 19:30 norsk tid)

- Sjekk antall gratisbytter i appen. Med **3 eller 4**: gjør Dasilva → Justin og Silva → Bogle. **Bare 2:** gjør Silva → Muharemović
  i stedet (bank £0,3m). Ellever da (3-4-3): Trafford; Gabriel, De Cuyper, Muharemović; Mbeumo, Ødegaard, Groß, Tavernier; Haaland, Barry, Isak.
  Benk: Tzolakis; Van Hecke, Rudoni, Dasilva. Kaptein De Cuyper, vise Haaland. Elleveren er den beste i R12 i blandingen
  (Claudes beregning på Codex' spillerpoeng).
- Gjør byttene **gjerne torsdag kveld før kl. 01:00 norsk tid** (prisjusteringen 27. nov 00:00 UTC). Bogle kan stige 0,1, og da
  forsvinner hele banken. Byttet avhenger ikke av fredagens nyheter.
- Sett kaptein og ellever **fredag etter pressekonferansene**:
  - **De Cuyper tvilsom eller ventet på benken** (Brighton spilte europacup torsdag): kaptein Haaland, vise Groß.
  - **Mbeumo ute:** Ødegaard inn i elleveren (han står først på benken uansett).
  - **Justin eller Bogle meldt ute** før byttet er gjort: bruk Konsa (4,9) i stedet. Justin + Konsa koster nøyaktig 9,4 og går opp.

## Uenighet mellom agentene og hva kritikken endret

Claude foreslo først P, Ødegaard → Le Fée og Dasilva → Konsa, før Codex' resultat forelå. Codex anbefalte G_keep og kaptein De Cuyper.
Etter kritikken (`claude/kritikk-av-codex.md`) testet Codex P, en fast tropp-tabell, Dasilva-salg med ett bytte og Justin + Konsa (`codex/kontroll.md`).
Konklusjonen:
- P taper mot G_keep i blandingen og bryter Ødegaard-regelen, så Claude følger Codex.
- Kritikken viste at gevinsten til G_keep etter R12 mest kommer fra senere modellbytter, men at den ikke er negativ med fast tropp.
- Justin + Konsa er nesten lik G_keep i blandingen (−0,24), men poengsettene spriker kraftig (−2,55 / +2,07). G_keep er positiv i begge og velges.

Det er ingen gjenstående uenighet om handling og kaptein.
