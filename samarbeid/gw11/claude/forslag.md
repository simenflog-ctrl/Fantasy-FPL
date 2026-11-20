# Claudes forslag runde 11 (før motorens og Codex' resultat)

Skrevet 2026-11-19 ca. 16:43 UTC. Verken motoren eller Codex er kjørt for gw11. Kontrollregningen bruker repoets xP
(`data/derived/expected_points.csv`, bot 19. nov, R11–R16) og antakelsene i `forutsetninger.md`. Modellresultater er merket som det.
Forutsetter 3 gratisbytter (2–4 mulig).

## Forslag

**To gratisbytter: Ødegaard (salg 6,7) → Le Fée (SUN, 5,7) og Dasilva (salg 4,0) → Van Hecke (TOT, 5,1). Bank £0,3m.
Det tredje gratisbyttet rulles (2 til R12). Ingen chip nå; Bench Boost foreløpig R12 som før.**

- **Ellever (3-5-2):** Trafford eller Tzolakis (likt i repo, se under); Gabriel, Van Hecke, De Cuyper; Tavernier, Le Fée, Rudoni, Groß,
  Mbeumo; Haaland, Barry.
- **Kaptein:** Haaland (FUL hjemme, 8,5 repo). **Visekaptein:** Gabriel (6,3).
- **Benk:** keeper; Isak, Silva, Muharemović.
- Ingen klubb får mer enn to spillere (SUN og TOT én hver).

## Kontrollregning (repo-xP, fast beste ellever med kaptein per runde, uten autobytter; modellresultat)

| Plan | Bank | R11 | R12 | R13 | R14 | R11–R14 | Mot rull |
|---|---|---|---|---|---|---|---|
| A: rull | 0,4 | 64,8 | 61,6 | 62,6 | 64,9 | 253,9 | – |
| **P2: Ødegaard → Le Fée, Dasilva → Van Hecke** | 0,3 | 67,1 | 63,9 | 65,1 | 66,6 | **262,7** | **+8,8** |
| P2b: Isak → N.Jackson, Dasilva → Van Hecke | 1,4 | 67,1 | 63,3 | 64,8 | 66,9 | 262,1 | +8,2 |
| P3: alle tre byttene | 2,4 | 68,0 | 64,2 | 65,2 | 68,4 | 265,8 | +11,9 |

Spiller-xP R11–R16 (repo): Van Hecke 5,8 / 4,8 / 5,4 / 4,1 / 5,2 / 4,2 mot Dasilva 3,8 / 2,9 / 3,6 / 2,5 / 3,3 / 2,4;
Le Fée 5,3 / 5,6 / 4,9 / 5,7 / 5,5 / 6,8 mot Ødegaard 4,4 / 3,8 / 4,2 / 4,0 / 4,2 / 4,8.

**Hvorfor P2 og ikke P3:** Isak → N.Jackson bygger på repoets rå xP, der Isak får for få minutter. Forrige uke falt det samme
argumentet (Isak → Evanilson) når Codex' minuttskalering ble brukt. P2 rører ikke Isak, og bruker bare to bytter, så planen er gratis
også hvis Simen bare har 2. Isak → N.Jackson skal likevel testes av motoren og Codex.

**Hvorfor ikke rulle:** Dasilva er den svakeste i troppen og står på benken, men Van Hecke starter, og Le Fée ligger over Ødegaard i
fem av seks runder. Gevinsten (+8,8 over fire runder i repo) er større enn i R10, der alternativet var +1–2.

## Hva som kan endre forslaget før fristen

- **Ødegaard eller Le Fée med skadenytt** (Arteta/Le Bris fredag): behold Ødegaard, og bruk bare Dasilva → Van Hecke hvis banken rekker
  (den gjør ikke det alene: 0,4 + 4,0 < 5,1). Da Dasilva → en forsvarer til ≤ £4,4m.
- **Haaland tvilsom:** kaptein Gabriel, vise Tavernier.
- **Prisendringer:** natt til fredag og natt til lørdag (01:00 norsk tid). Van Hecke og Le Fée kan stige; byttene gjøres fredag kveld.

## Tillegg 2026-11-19 ca. 16:55 UTC (etter Simens innspill, etter første prøvekjøring av motoren)

Simen opplyser at Ødegaard spilte glitrende i landslagspausen. Det bekrefter at han er frisk, og han har spilt 87–90 minutter i hver av
de fire siste ligarundene. Spilletiden hans er derfor hevet i R11–R12 (`minutter_overstyring.csv`). Landskampform sier lite om poeng i
klubben utover det.

Første prøvekjøring av motoren (før endringen) ga P2 bare +1,5 / +1,7 mot rull over R11–R19 (codex / repo_hybrid), og selve
byttet Ødegaard → Le Fée var nesten nøytralt i `codex` (R11–R14: 16,9 mot 17,1). **Ved så liten forskjell beholdes Ødegaard med mindre
de endelige tallene viser en klar gevinst ved å selge ham (mer enn ca. 3 poeng over R11–R19 i begge poengsett).** Da testes i stedet
å rulle, og å få inn Van Hecke uten å selge Ødegaard (Silva → Van Hecke, Muharemović → Van Hecke).
