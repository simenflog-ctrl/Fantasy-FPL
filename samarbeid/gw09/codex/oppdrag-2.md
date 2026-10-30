<task>
Runde 2 av kritikk og revisjon for R9 (frist 31. okt 11:00 UTC). Les claude/kritikk-av-codex.md (Claudes kontroll av analysen din)
og claude/forslag.md (Claudes eget forslag, laget før han leste analysen) og claude/forutsetninger.md (spilletid og cupinfo).
Claude foreslo å rulle begge gratisbyttene og ta WC i R11; du anbefalte WC9. Uenigheten avgjøres med beregninger.
</task>

<required_checks>
1. Autobytter: legg til FPL-autobytter (benkerekkefølge, gyldig formasjon, visekaptein ved 0 min for kaptein) i poengberegningen,
   eller en forventningsverdi-tilnærming med p_play. Beregn A, C, E, F_WC10 og F_WC11 på nytt. I A og C: start Calafiori og N.Williams
   med van Ewijk og Maguire som dekning, hvis det gir høyere forventning med autobytter.
2. Ventingens verdi: parede skadesimuleringer (som gw08 kontroll_r3) for E (WC9) mot F_WC11 og F_WC10, samme BB19/FH16 i alle baner.
   Nye fravær trekkes for R9–R19 for alle eide spillere og kandidater; WC9-banen får reparere med sine opptjente gratisbytter
   (samme byttepolitikk som ellers), WC11-banen velger troppen med kjennskap til fravær som har inntruffet før R11-fristen.
   Rapporter snitt, andel E vinner og p10–p90 for 2–3 nivåer av skaderate.
3. Groß på benken i E: test en WC9-tropp der Groß selges, med samme budsjett. Rapporter forskjell R9–R19 og om BB19 forklarer valget.
4. Opprykkslagene: følsomhet for E og WC11 der HUL, LEE og COV slipper inn 20 % mer (nullen og innslupne) enn modellen antar R9–R19.
5. Bruk Claudes p_start for B.Fernandes (0,75 i R9) og Calafiori (0,5 i R9) fra forutsetninger.md; øvrige minutter som før.
6. Kritiser Claudes forslag direkte: hvor mye koster det å rulle (A) med autobytter, mot E og mot C, og er Claudes argument om
   informasjon etter landslagspausen gyldig når WC9 gir opptjente gratisbytter?
</required_checks>

<action_safety>
Skriv bare i samarbeid/gw09/codex/ (nye filer med suffiks _r2, f.eks. kontroll.md, alternativer_r2.csv, spillerpoeng_r2.csv).
Ikke overskriv runde 1-filene. Ikke endre andre filer, ikke commit. Anaconda: export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH
</action_safety>

<deliverables>
codex/kontroll.md på norsk: svar på punkt 1–6 med tall, oppdatert rangering, og en klar anbefaling for R9 (handling, ellever, kaptein,
visekaptein, benk). Hvis anbefalingen fortsatt er WC9: endelig tropp med budsjettkontroll. Lever codex/spillerpoeng_r2.csv
(id, navn, gw, codex, repo_hybrid; R9–R16) som brukes i frosset prognose. Kjør skriptene selv og bekreft at tallene stemmer.
</deliverables>
