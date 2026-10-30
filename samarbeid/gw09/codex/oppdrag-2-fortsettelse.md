<task>
Fortsett oppdrag 2 (codex/oppdrag-2.md) der du stoppet på bruksgrensen kl. 12:11 UTC. Du hadde levert alternativer_r2.csv, autobytter_r2.csv,
gross_r2.csv, opprykk_r2.csv, skadesim_r2.csv (bare 1 % skaderate) og innhopp_sensitivitet_r2.csv, men ikke codex/kontroll.md.
Siste kommando ble avbrutt (exit 130) etter at spillerpoeng_r2.csv og minutter_antatt_r2.csv ble skrevet kl. 12:11.
</task>

<claude_observations>
1. WC9-troppen i alternativer_r2.csv inneholder «Thomas». Hvis det er id 173 (COV, forsvarer), er han status d, 75 %, «Unspecified injury»
   i API-et. Bekreft id-en og om troppen holder seg best også med p_start for ham satt slik det står i minutter_antatt_r2.csv.
2. WC9-troppen er endret fra runde 1 (nå med Ødegaard, Isak, Muharemović og Fernandes solgt). Bekreft at den rapporterte troppen,
   elleveren og benken er samme tropp som tallene i alternativer_r2.csv og gross_r2.csv bygger på. Lever id-er.
3. Du nevnte selv to forhold: det raske byttesøket kan overse en bedre plan frem til WC11, og testen uten Bench Boost må bruke en
   byttepolitikk som ikke planlegger for BB19. Avklar dem.
4. Kjør skadesimuleringen med 2–3 skaderater (minst 1 % og 3 % nye fravær per spiller per runde), som oppdrag 2 ber om.
5. Kontroller at spillerpoeng_r2.csv er konsistent med tallene i kontroll.md, siden den ble skrevet rett før avbruddet.
</claude_observations>

<deliverables>
codex/kontroll.md på norsk som beskrevet i oppdrag-2.md, med endelig anbefaling for R9 (handling, tropp med id og salgs-/kjøpspris,
budsjettkontroll, ellever, kaptein, visekaptein, benkrekkefølge). Skriv bare i codex/. Ikke commit.
Hvis du nærmer deg bruksgrensen: skriv kontroll.md først med det du har, og merk hva som mangler.
</deliverables>
