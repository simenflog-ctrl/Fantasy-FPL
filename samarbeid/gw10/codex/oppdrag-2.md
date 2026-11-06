<task>
Runde 2 av kritikk og revisjon for R10 (frist i dag 18:30 UTC). Du stoppet på bruksgrensen 06:58 UTC mens skadesimuleringen pågikk.
Les claude/kritikk-av-codex.md og claude/forslag.md. Hold det kort; levér kontroll.md innen ca. 30 minutter.
</task>

<required_checks>
1. Fullfør parede skadesimuleringer (1 %, 2 %) for A (rull), B (Tzolakis → Verbruggen) og C (Groß, Muharemović → Van Hecke, Le Fée),
   med samme BB- og FH-dato i alle (BB12, FH13), og rapporter snitt, andel B vinner mot A og p10–p90.
2. Test Claudes forslag eksplisitt med samme metode: (a) Dasilva → Van Hecke finansiert av Ødegaard → Iwobi; (b) Isak → Evanilson + Dasilva → Van Hecke.
3. Bekreft at BB10 ikke er best også når FH-dato velges fritt (chiprutenett.csv), og oppgi BB10 minus beste BB for valgt R10-handling.
4. Kritiser Claudes forslag direkte, og gi endelig anbefaling for R10: handling, ellever, kaptein, visekaptein, benkrekkefølge, BB nå eller ikke.
</required_checks>

<action_safety>
Skriv bare i samarbeid/gw10/codex/ (nye filer med suffiks _r2 og kontroll.md). Ikke overskriv runde 1-filene. Ikke commit.
Anaconda: export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH
Skriv kontroll.md først med det du har, og utvid etterpå, i tilfelle bruksgrensen stopper deg igjen.
Hvis spillerpoeng endres, lever codex/spillerpoeng_r2.csv (id, navn, gw, codex, repo_hybrid; R10–R17).
</action_safety>
