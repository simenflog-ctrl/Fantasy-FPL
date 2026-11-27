<task>
P0 er gjennomgått og committet (9b87834), og D0-godkjenningen din er notert. Takk. Nå skal du måle og godkjenne eller avvise
Claudes to kandidater, med målemotoren din og kravene i samarbeid/modell/plan.md. Claude har skrevet begge, så du er uavhengig måler.

Nye commits fra Claude (les diffene):
- 7502dcd: minutes.SUB_GIVEN_NO_START (P2), av som standard.
- 87a16db: expected_points.BONUS_TAU_FIXED (P1-kandidat B1), None som standard; og minutes.build(..., last_season=...)
  så du kan fjerne StringIO-broen i eval_engine (gjør gjerne det, det er din fil).

Forhåndsregistreringen for P1 står i samarbeid/modell/claude/p1-bonus-forhandsregistrering.md. Følg den nøyaktig:
velg tau fra rutenettet {4, 5, 6, 7, 8, 10, 12} på 2023-24 og 2024-25 (bonus-MSE, walk-forward, GW8–38), lås verdien,
og test så mot baseline på 2025-26 og alle tre sesongene. B2 bare hvis B1 består.
</task>

<required_work>
1. P2: SUB_GIVEN_NO_START av mot på, GW8–38, tre sesonger. Primærmål og vern som i plan.md. Rapporter også minutt-/innhoppskalibrering
   (predikert mot faktisk p_play og minutter for spillere med p_start < 0,6), siden det er mekanismen.
2. P1 B1: tau-valg på utviklingssesongene, deretter låst test. Rapporter bonus-MSE, total-MSE, topp-10/20, premiumkalibrering
   (bonus og total for ≥ 10 m og 8–10 m, FWD og MID) før/etter, per sesong og samlet, med blokk-SE.
3. Kombinasjonen P1 + P2 hvis begge består hver for seg (sjekk at effektene ikke opphever hverandre).
4. Konklusjon per kandidat: GODKJENT / AVVIST / UAVKLART etter kravene, inkludert det forhåndsskrevne unntaket for P1.
   Ikke endre kravene etter at du har sett tallene.
</required_work>

<action_safety>
Du kan endre src/eval_engine.py, src/evaluate_pred.py, tests/test_parity.py og samarbeid/modell/codex/. Ikke endre standardverdiene til
flaggene i src/minutes.py eller src/expected_points.py; sett dem bare under målingen og gjenopprett dem. Ikke commit. Ingen nett eller installasjon.
Hele testsuiten skal være grønn før du leverer.
</action_safety>

<deliverables>
samarbeid/modell/codex/p1p2-maling.md (norsk): tabeller, konklusjon per kandidat, og anbefalt verdi for BONUS_TAU_FIXED hvis godkjent.
CSV-er med tallene og skriptet som gjenskaper dem.
</deliverables>

<completeness_contract>
Ferdig betyr: alle målinger er kjørt fra skript, tau er valgt bare på utviklingssesongene, tallene i rapporten stemmer med CSV-ene,
og hver kandidat har en klar konklusjon mot de forhåndsregistrerte kravene.
</completeness_contract>
