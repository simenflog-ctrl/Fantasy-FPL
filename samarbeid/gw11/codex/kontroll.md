# Kontroll R11 – runde 2

**Enig med Claude om BB11, kaptein Haaland og vise Gabriel. Uenig i at B er modellens beste handling:** C har fortsatt høyest forventning i den avtalte 50/50-blandingen. B er et forsvarlig, mer robust valg på tvers av poengsettene, men det innebærer å gi avkall på beregnet forventning. Ingen modellendringer er gjort.

## 1. Fullført hovedberegning

`status.json` sier fullført. Alle fem planer har 100 parede verdener ved 1 % og 2 %, med BB11/FH15 og 3 FT. Prognosens 6048 rader er uendret. Rekonstruksjon fra spiller-CSV og lagvekter avviker maksimalt 0,000005 poeng; fullt og begrenset elleversøk gir identiske nominelle hovedtotaler. Analyse- og alternativtabellene er oppdatert.

B mot rull: +0,75 poeng i blandingen ved 1 %, +0,79 ved 2 %. Ved 2 % er forskjellen +1,08 / +0,49 i poengsettene, men paret p10–p90 i blandingen er −0,17 til +1,32. Positiv forventning betyr ikke at B vinner i alle verdener.

**C minus B, samme BB11/FH15:**

| Nye fravær | Δ codex / repo | Δ blanding | Paret p10–p90 blanding | MC-SE |
|---|---:|---:|---:|---:|
| 1% | -1.73 / +4.48 | +1.38 | +0.16 til +2.08 | 0.10 |
| 2% | -1.44 / +3.70 | +1.13 | -0.09 til +2.35 | 0.13 |

## 2. Paret test av BB-dato

`bb_skade.csv` har 72 sammenligninger: A/B × FH12/FH15 × 1/2 % × BB11−BB18, BB11−BB19 og BB18−BB19 × tre poengsett. Alle har n=100, egne p10–p90 og MC-SE. Samme laghandling, byttepolitikk og FH holdes fast innen hver sammenligning; nøyaktig de samme skadeverdenene som i punkt 1 brukes. Positiv Δ under betyr fordel BB11.

| Plan B | FH | Rate | Δ codex / repo | Δ blanding | Paret p10–p90 blanding | MC-SE |
|---|---:|---:|---:|---:|---:|---:|
| BB11−BB18 | 12 | 1% | +0.44 / +0.85 | +0.65 | +0.18 til +1.16 | 0.12 |
| BB11−BB19 | 12 | 1% | +0.32 / +0.73 | +0.52 | +0.10 til +0.64 | 0.05 |
| BB11−BB18 | 12 | 2% | +0.91 / +1.32 | +1.12 | +0.14 til +4.06 | 0.16 |
| BB11−BB19 | 12 | 2% | +0.35 / +0.76 | +0.55 | -0.12 til +1.08 | 0.07 |
| BB11−BB18 | 15 | 1% | +0.40 / +0.81 | +0.60 | +0.16 til +1.16 | 0.12 |
| BB11−BB19 | 15 | 1% | +0.30 / +0.71 | +0.51 | +0.09 til +0.65 | 0.05 |
| BB11−BB18 | 15 | 2% | +1.00 / +1.41 | +1.21 | +0.14 til +4.02 | 0.16 |
| BB11−BB19 | 15 | 2% | +0.31 / +0.72 | +0.51 | -0.12 til +1.08 | 0.06 |

**B: BB11 vinner i begge poengsett ved begge rater og begge FH-datoer.** BB19 er den nærmeste av de to sene datoene ved 2 %. For A er BB11s fordel mot BB18/BB19 bare +0,09 til +0,69 i blandingen; ren Codex foretrekker fortsatt sen BB ved 1 %. Dermed er argumentet for BB11 sterkere etter Van Hecke-bytte enn ved rull.

Ingen uenighet om BB11 for B. Nye fravær styrker nå-alternativet, men antatte skaderater er ikke estimerte sannsynligheter. Målrettet benkeoppbygging og eventuelle fremtidige dobbeltrunder er fortsatt utenfor modellen; dette er ikke bevist optimal chipbruk under alle fremtidige scenarioer.

## 3. Hva i Claudes kritikk holder – og hva må korrigeres

**Holder:** C er ikke robust på tvers av poengsettene. Mesteparten av Cs fordel mot B oppstår etter R11; de dokumenterte salg/tilbakekjøpene og faste priser gjør langtidsbanen usikker. Det er riktig å revurdere senere bytter og FH-dato. B gir en liten positiv fordel i begge poengsett ved alle testede FT-antall.

**Må presiseres:** Modelluenighet betyr ikke matematisk uavgjort i den avtalte 50/50-blandingen. C slår B med +1,13 poeng ved 2 % også etter adaptive skadereparasjoner; forskjellen har MC-SE 0,13, men stor modelluenighet. En regel om positiv gevinst i begge poengsett er et ekstra, konservativt beslutningskriterium, ikke det samme som å maksimere den fastsatte blandingen. Jeg har ikke lagt inn et slikt veto eller omvektet repo etter tre evalueringsrunder.

**Fleksibiliteten er allerede regnet med:** C bruker flere FT nå og har færre til senere reparasjoner; dette inngår i hver eierbane og skadeverden. Salg og tilbakekjøp belastes med bytter. En ekstra, skjønnsmessig FT-straff ville dobbelttelle deler av kostnaden. At A/B når taket senere gjør heller ikke ett FT nå garantert verdiløst i alle skadeverdener.

**Reell begrensning:** Den uendrede byttepolitikken er heuristisk; 4 FT gir en annen senere bane og lavere total enn 3 FT for C. Det viser søkeusikkerhet, ikke negativ iboende verdi av et gratisbytte. Claudes opplysning om ny N.Jackson-pris er heller ikke innarbeidet: alle tall beholder de avtalte prisene fra 19. november. Ingen av disse forholdene er kvantifisert som en ny korreksjon denne runden.

**Konklusjon:** Etter oppdragets forventningsmål beholder jeg C + BB11 som modellførstevalg. Hvis Claude velger B fordi gevinsten skal være positiv i begge poengsett, er B + BB11 et forståelig robusthetsvalg; begrunnelsen bør oppgi forventningstapet på omtrent 1,1 poeng mot C ved 2 % stress. B er ikke dårligere enn rull i gjennomsnitt i de testede modellene, men fordelen er liten.

Kjør hovedmodellen som dokumentert i analyse.md; BB-testen gjenskapes med `PYTHONDONTWRITEBYTECODE=1 python samarbeid/gw11/codex/bb_kontroll.py` under Anaconda. `bb_status.json` sier fullført. Ingen uavhengig prøvekjøring er lest; ingen git eller FPL-handlinger er utført.
