# Claudes kontroll av Codex' revisjon (runde 2)

Skrevet 2026-10-22 etter `codex/kontroll.md` og `*_r2.csv`.

## Godtatt

- Kalibreringen med `history_past` og xG-basert lagstyrke er en reell forbedring. At Haaland fortsatt ligger på 6,1 mot repo 8,4
  skyldes nesten bare bonusraten (1,4 mot 2,8 per kamp). Codex har rett i at repoets bonus trolig er for høy; sannheten ligger imellom.
- Filtrering av kjøpsuniverset (Dennis, Hughes) er rettet og kontrollert.
- Lik byttepolitikk for alle planer er nå på plass.
- Kritikken av forslaget mitt er riktig på tre punkter: Fernandes ×0,7 påvirker ikke alle planer likt når WC kan selge ham;
  «3–4 poeng per rullet FT» var et scenario, ikke en beregning; og WC-vinduet R12–15 var en hypotese.
- Rollekontroll av de nye navnene i fellesplanen: Tzolakis 7×90, Thomas (COV) 6×90, Dasilva 6×90, Silva 7×90, De Cuyper 77–90.
  Thomas-Asante er usikker (69, 32, 19, 17, 90, 90, 77). João Pedro: 0 min i R5. Ingen skadeflagg. **Rollene holder.**

## Innvendinger

### 1. Fordelen ved WC nå kommer fra chipdatoer, ikke fra wildcardtidspunktet

Fra `alternativer_r2.csv`, repo_hybrid:

| | R8–13 | R8–15 | R8–19 | BB / FH |
|---|---|---|---|---|
| E (WC8) | 406,2 | 521,8 | 767,9 | 17 / 13 |
| B_WC11 | 403,3 | **533,1** | 763,9 | 15 / 9 |

B_WC11 leder med 11,3 poeng til R15. E tar igjen alt og mer i R16–19, der planene har ulike BB- og FH-runder.
I Codex-settet leder B_WC13 til R15 (460,0 mot 456,8). Marginen på +1 til +4 for fellesplanen er derfor mindre enn
forskjellen chipdatoene alene skaper, og den kan ikke tilskrives wildcarden.

### 2. Informasjonsverdien ved å vente er satt til null

Modellen har ingen nye skader, karantener eller rolleendringer etter R8. En wildcard som holdes, er forsikring mot nettopp det,
i et vindu (november–januar) med tett kampprogram. En brukt wildcard kan ikke reagere. Dette er den eneste systematiske
effekten som ikke er priset, og den peker bare én vei.

### 3. Fellesplanen bygger på svake marginer

Fellesplanen leder med +1,1 i Codex-modellen. Én usikker rolle (João Pedro var ute av laget i R5; Thomas-Asante har p_start 0,61)
er større enn marginen.

## Oppdrag tilbake (runde 2, siste beregningsrunde)

Se `codex/oppdrag-3.md`.
