# Claudes kontroll av Codex' analyse, runde 10

Skrevet 2026-11-06 ca. 06:59 UTC, etter `claude/forslag.md`. Codex stoppet på bruksgrensen 06:58 UTC («try again at 12:44 PM» norsk tid,
11:44 UTC) mens skadesimuleringen pågikk. `codex/analyse.md` er merket foreløpig.

## Det som holder

- Budsjett: £0,4m + Tzolakis 4,7 − Verbruggen 4,6 = £0,5m. Riktige salgspriser.
- Alle alternativer er sammenlignet med samme FH-dato og samme byttepolitikk; BB13/FH13-kollisjonen er håndtert ved å flytte FH i begge baner.
- Europa-belastning (×0,95) og Groß (×0,85) er eksplisitte og testet (Groß 0–0,9 endrer ikke rangeringen).
- Kaptein Haaland i begge poengsett; Gabriel som vise.

## Claudes forslag mot Codex' tall

- **Isak → Evanilson faller.** I Codex' poengsett er Isak bedre enn Evanilson R10–R17: 37,2 mot 31,2 (codex) og 33,8 mot 32,4 (repo_hybrid).
  Claude brukte repoets rå xP (3,8), mens repo_hybrid minuttskalerer Isak til 4,5. Codex' minutter for Isak er bedre begrunnet
  (8 starter av 9). Claude trekker forslaget.
- **Dasilva → Van Hecke** gir +9,5 / +10,6 i spiller-xP R10–R17, men krever £0,6m mer enn banken, og Dasilva står stort sett på benken.
  Codex' beste finansiering (Ødegaard, Dasilva → Iwobi, Van Hecke) ligger +0,5 over rull i søket (`byttesok.csv`). Innenfor støyen.
- **Bench Boost i R10 faller.** BB10 er 1–3 poeng bak BB11, BB12 og BB19 i begge poengsett, også med 1 % nye fravær (−2,0 / −2,3 mot BB12).
  Benken i R10 har svakere kamper (Tzolakis borte mot ARS) enn i R11/R12. Simens argument (alle spiller nå) er reelt, men allerede
  med i p_play og skadesimuleringen.

## Innvendinger

1. **Forskjellene mellom A, B og C er støy** (−0,9 til +1,7 gjennom R19, uenige poengsett). Anbefalingen B (Tzolakis → Verbruggen,
   keeperen solgt for én uke siden) er +0,44 i snitt. Codex sier selv at ingen sikker gevinst er påvist. Skadesimuleringen for A–D ble ikke ferdig.
2. **Haaland:** codex 5,4 mot observert 7,6 per runde og repo 7,4. Undervurderingen fra gw08/gw09 består (bonuskrymping).
   Påvirker ikke kapteinsvalget, men gjør codex-nivåene lave.
3. **FH13:** begrunnelsen er tynn (FH16 er +1,1 i codex, −4,3 i repo). Foreløpig; avgjøres senere.

## Foreløpig vurdering

Ingen bytter eller ett lite keeperbytte er praktisk talt likeverdige. Ikke BB nå. Kaptein Haaland, vise Gabriel.
Oppdrag 2 ber Codex fullføre den parede skadesimuleringen for A mot B (og C), slik at valget mellom å rulle og å bytte keeper tas på tall.
