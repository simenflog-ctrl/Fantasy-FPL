<task>
Vi skal forbedre prediksjonsmodellen for FPL-laget 7089878 (sesong 2026/27). Simen vil at Claude og Codex drøfter og
gjennomfører forbedringer selv. Dette er første steg: en uavhengig gjennomgang fra deg, pluss en målt baseline.
Claude skriver sin egen liste parallelt og har ikke vist deg den.

Repoet er på grenen `modellforbedring`. Produksjonsmodellen ligger i src/ (minutes.py, team_strength.py,
expected_points.py, optimize.py; kjøres av GitHub Actions). Evalueringsverktøy finnes allerede:
src/backtest.py (walk-forward M9), src/evaluate_pred.py (parvis prediksjonsmåling: MAE, Spearman, topp-k)
og src/evaluate.py + src/season_sim.py (parvis sesongsimulering). Les docstringene; de forklarer metodikken.

Historiske data ligger nå lokalt i data/cache/vaastav/<sesong>/gws/merged_gw.csv for 2022-23 til 2025-26, og
data/cache/vaastav/2025-26/cleaned_players.csv. Koden peker på raw.githubusercontent.com; pek den til de lokale filene
(f.eks. ved å sette modulvariablene B.HIST / BASE i en egen kjøringsfil) i stedet for å bruke nett.

Erfaringer fra runde 8 (se samarbeid/gw08/, særlig claude/kritikk-av-codex*.md og codex/kontroll*.md):
- Repoets xP og Codex' gw08-modell var uenige med ~12 poeng per lag per runde, mest på bonus og toppspillere
  (Haaland 8,4 mot 6,1 per runde; Fernandes 7,3 mot 4,8). Ingen av dem er målt ut av utvalg på dette.
- Keepermål er 10 poeng i 2026/27 (API), men expected_points.py har 6 hardkodet.
- Beslutningslaget (optimize.py) brukte nåpris i stedet for salgspris, hardkodet 1 FT og hadde kort horisont.
</task>

<required_work>
1. Kjør en baseline med evaluate_pred-riggen (eller tilsvarende walk-forward) på 2023-24, 2024-25 og 2025-26, offline.
   Rapporter MAE, Spearman og topp-k for dagens modell. Hvis riggen ikke lar seg kjøre offline uten kodeendringer,
   lag en tynn wrapper i samarbeid/modell/codex/ og si hva du måtte gjøre.
2. Mål kalibreringen der vi så uenighet: predikert mot faktisk **bonus** og **totalpoeng** etter prisgruppe
   (f.eks. < 6, 6–8, 8–10, ≥ 10) og posisjon, walk-forward. Er toppspillerne systematisk under- eller overvurdert?
3. Gå gjennom src/ og din egen gw08-modell (samarbeid/gw08/codex/modell_r2.py) og lag en **rangert liste over forbedringer**:
   for hver, forventet gevinst, hvordan den måles (evaluate_pred eller sesongsimulering), kostnad og risiko.
   Skill prediksjonsendringer fra beslutningsendringer.
4. Foreslå hvilke 2–3 tiltak vi bør gjøre først i dag, og hvordan vi avgjør om de er reelle forbedringer
   (krav til effektstørrelse i standardfeil, flere sesonger med samme fortegn).
</required_work>

<action_safety>
Skriv bare i samarbeid/modell/codex/. Ikke endre src/, data/, config/, tests/ eller andre filer ennå; vi avtaler endringer
etter at begge listene er sammenlignet. Ikke commit. Ikke installer pakker. Ikke bruk nett.
</action_safety>

<deliverables>
- samarbeid/modell/codex/gjennomgang.md (norsk): baseline, kalibreringsfunn, rangert forbedringsliste, forslag til første tiltak.
- samarbeid/modell/codex/baseline.csv og kalibrering.csv, og skriptet som lager dem.
</deliverables>

<completeness_contract>
Ferdig betyr: baseline og kalibrering er faktisk kjørt (ikke anslått), tallene i gjennomgang.md stemmer med CSV-ene,
og listen sier tydelig hva som er målt og hva som er antakelse. Hold kjøretiden under ca. 30 minutter; reduser antall
sesonger eller runder hvis nødvendig og si hva du kuttet.
</completeness_contract>
