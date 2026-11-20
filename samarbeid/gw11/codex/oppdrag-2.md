<task>
Runde 2 for R11 (frist lørdag 21. nov 11:00 UTC). Kvoten din er liten: gjør punktene i rekkefølge, og oppdater filene etter hvert punkt.
Les først `samarbeid/gw11/claude/kritikk-av-codex.md` (Claudes kontroll av tallene dine og Claudes forslag).
</task>

<steps>
1. Fullfør den påbegynte skadesimuleringen (`modell.py` til `status.json` sier fullført) og fyll inn tabellen i `analyse.md`.
2. Paret skadetest av Bench Boost-datoen for plan B (Muharemović → Van Hecke) og plan A: BB11 mot BB18 mot BB19,
   samme FH (FH12, og FH15 hvis tiden rekker), samme 100 verdener, 1 % og 2 %. Rapporter Δ codex / repo / blanding, p10–p90 og MC-SE.
   Skriv tabellen til `codex/bb_skade.csv`.
3. Kritiser Claudes forslag i `codex/kontroll.md` (kort): B + BB11, kaptein Haaland, vise Gabriel. Er noe i Claudes innvendinger
   mot C feil? Er det noe som gjør B dårligere enn C eller rull som Claude ikke har sett? Si fra om du er uenig i BB11.
</steps>

<rules>
Ingen modellendringer. Skriv bare i `samarbeid/gw11/codex/`. Ikke les `samarbeid/gw11/motor/`. Ingen git, ingen FPL-handlinger.
Del kjøringen slik at ingen enkeltkommando tar mer enn ca. 8 minutter.
</rules>
