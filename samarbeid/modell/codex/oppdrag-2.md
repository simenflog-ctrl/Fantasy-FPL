<task>
Takk, gjennomgangen din overlappet sterkt med Claudes uavhengige liste. Les nå samarbeid/modell/plan.md (felles plan, filansvar
og forhåndsregistrerte godkjenningskrav, hentet fra ditt forslag), samarbeid/modell/claude/avviksrevisjon.md og
samarbeid/modell/claude/forslag.md.

Claude har allerede rettet D0 i src/optimize.py og src/fetch.py (commit e1e1fb3 på grenen, tester i tests/test_optimize.py).
Claude jobber nå parallelt med P2 i src/minutes.py bak et flagg. **Ikke endre src/minutes.py, src/optimize.py eller src/fetch.py.**

Ditt oppdrag: P0 + keepermål.
1. Gjør produksjonens funksjoner til felles prognosemotor for målingen. Utgangspunkt: din produksjonsrekonstruksjon i
   samarbeid/modell/codex/kjor_baseline.py. Flytt den inn i src/ (f.eks. src/eval_engine.py) slik at evaluate_pred kan måle
   produksjonsmodellen parvis med konfigurasjonsflagg. Gjør minimale endringer i produksjonsfunksjonene: bare det som trengs for å
   ta data inn som argumenter (i stedet for filstier og nett) og lokal cache for historiske sesonger. Behold produksjonsoppførselen identisk.
   Inkluder unike fixture-ID-er på tvers av sesonger og blokk-SE (fire-runders blokker) i sammenligningen.
2. tests/test_parity.py: produksjonens xP for et lite fast utsnitt skal være lik når den kjøres via produksjonsveien og via målemotoren.
   Testen skal kjøre offline og raskt (< 30 s).
3. Keepermål per sesong: 10 for 2026/27 (fra API-et / game_config), historiske sesonger beholder sin regel. Ingen andre regelendringer.
4. Kjør baseline på nytt med den nye motoren og bekreft at den er lik din produksjonsrekonstruksjon (eller forklar avvik).
5. Kontroller Claudes D0-rettelser i src/optimize.py (les koden og testene; kjør tests/). Godkjenn eller skriv konkrete innvendinger.
</task>

<action_safety>
Endre bare filene plan.md gir deg (src/backtest.py, src/evaluate_pred.py, src/expected_points.py, src/team_strength.py, nye src/eval_*.py,
tests/test_parity.py, samarbeid/modell/codex/). Ikke commit; Claude committer etter kontroll. Ikke installer pakker, ingen nett.
Ikke endre data/derived/ eller produksjonens utdata. Kjør hele testsuiten (python3 -m pytest -q tests/) før du leverer.
</action_safety>

<deliverables>
- Kode i src/ og tests/ som beskrevet, alle tester grønne.
- samarbeid/modell/codex/p0.md (norsk, kort): hva som er endret og hvorfor, paritetsbevis, ny baseline (samme tabellform som før),
  kontrollen av D0, og hva Claude bør se spesielt på i kodegjennomgangen.
</deliverables>

<completeness_contract>
Ferdig betyr: målemotoren bruker produksjonens funksjoner, paritetstesten består, baseline er gjenskapt, produksjonens utdata er uendret
for 2026/27 bortsett fra keepermål, og hele testsuiten er grønn. Hold kjøretiden nede; si hva du eventuelt kuttet.
</completeness_contract>
