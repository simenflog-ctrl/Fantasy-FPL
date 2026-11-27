"""Write the P0 review directly from the executed result artifacts."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,re
import pandas as pd
O=Path(__file__).resolve().parent
b=pd.read_csv(O/'p0_baseline.csv')
old=pd.read_csv(O/'baseline.csv')
a=pd.read_csv(O/'p0_avviksforklaring.csv')
d=pd.read_csv(O/'p0_rekonstruksjon_avvik.csv')
manifest=json.loads((O/'p0_manifest.json').read_text())
test_count,test_seconds=re.search(r'(\d+) passed in ([\d.]+)s',(O/'p0_tests.log').read_text()).groups()

def table(window):
    lines=['| Sesong | N | MAE | RMSE | Spearman, spilte | Topp10 | Topp20 | Topp50 |',
           '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for _,r in b[b.window==window].iterrows():
        lines.append(f'| {r.season} | {int(r.n)} | {r.mae:.4f} | {r.rmse:.4f} | {r.spearman_played:.4f} | {r.top10:.3f} | {r.top20:.3f} | {r.top50:.3f} |')
    return '\n'.join(lines)

ref=old[(old.model=='produksjon_offline')&(old.season=='alle')&(old.window=='GW8-38')].iloc[0]
new=b[(b.season=='alle')&(b.window=='GW8-38')].iloc[0]
delta=d[d.season=='alle'].iloc[0]
text=f'''# P0 – felles målemotor og keepermål

**Ferdig for kontroll, ikke committet.** Hele testsuiten er grønn: **{test_count} tester på {test_seconds} s**, inkludert Claudes P2-tester. `test_parity.py` bruker under ett sekund per produksjons-/motorparitetstest. Ingen nettbruk, installasjon eller endring av produksjonsdata. `minutes.py`, `optimize.py` og `fetch.py` er ikke redigert av Codex.

## Endringen

- `expected_points.forecast` er poengkjeden som både produksjonens `main()` og `eval_engine` nå kaller. Rater, DC, temperatur, målkalibrering og dispersjon bruker produksjonsfunksjonene. Valgfrie prior-/fixture-data inn som argumenter; standard matematikk og flagg er beholdt. Den eksisterende lokale 2025/26-cachen foretrekkes framfor nett for spillerprioren.
- `team_strength` tar også priorer og kampprogram som argumenter; produksjonens eksisterende filvei er standard. Estimatoren er uendret.
- `eval_engine.py` flytter historikkadapteren inn i `src/`: lokal cache, datarydding, rekonstruerte priorfiler og faktiske `minutes.build`, `team_strength.fit_current/project_fixtures` og `expected_points.forecast`. Fixture-ID er `sesongstartår × 1 000 000 + rå-ID`; `source_fixture` bevares. Paring er sesong + stabil spiller-nøkkel + fixture.
- `evaluate_pred.compare` måler denne motoren, kjører konfigurasjoner serielt og gjenoppretter flagg også ved feil. Den verifiserer både nøkler og utfall før paring. MSE, MAE, bonus-MSE og topp-k får **fire-runders blokk-SE innen sesong**, med riktig vekt på korte sluttblokker. GW8–38 gir 24 blokker samlet. Ingen rad-SE eller ny tuningregel erstatter kravene i `plan.md`.
- `backtest.main()` går til samme målemotor. Legacy-hjelpere beholdes uttrykkelig for `season_sim`, som er et senere steg; gamle `B.*`-flagg styrer dermed ikke lenger dagens `evaluate_pred`. Nye kandidater må endre flagget i den faktiske produksjonsmodulen.
- Bare **keepermål** endrer poengregel: 10 i 2026/27, med verdi fra `game_config` når tilgjengelig; historiske sesonger får 6 selv om en nyere API-konfigurasjon sendes inn. Ingen andre posisjons-/poengregler endres.

## Paritetsbevis

`tests/test_parity.py` lager et lite fast utsnitt med begge lag, alle posisjoner, starter, innhopp, fravær og positiv keeper-xG. Produksjonsveien bruker vanlige filinnlesere, mellomlagrede minutt-/lag-/prognosefiler og **`expected_points.main()`** i en midlertidig testmappe. Måleveien får de samme inputene i minnet. xP, angrep, forsvar, bonus, DC og minutter er like innen **1e-11**, både med P2-flagget av og på. Testen kontrollerer også historiske keeperregler, nøyaktig +4 × forventede keepermål, gjenoppretting ved feil, fixture-navnerom, blokkvekting og at feilparinger avvises.

En separat før/etter-kontroll bruker lagret originalkode og **4 008 eksisterende 2026/27-prognoser**, uten å skrive produksjonsutdata. Alle xP og komponenter er identiske; største uventede differanse er **0**. Keeper-xG er null i disse inputene; derfor er selve målendringen bevist separat i testen med keeper-xG > 0. Se `p0_regresjon.py`, `p0_regresjon.log` og `p0_produksjon_regresjon.csv`. Filhashene før/etter bekrefter uendrede `data/raw/`, `data/prior/` og `data/derived/`.

## Ny baseline

Alle tre sesonger, GW2–38, er kjørt med dagens standardflagg (**P2 av**). Kjøretid {manifest['seconds']:.1f} s; ingen sesonger/runder kuttet. Enhet og topp-k er som før: spiller–kamp, nullminutter med i MAE/RMSE, Spearman blant faktisk spilte, faktisk poengsnitt for valgte topp-k per runde. Dette er ikke en budsjett-/formasjonsbegrenset ellever.

**GW2–38:**

{table('GW2-38')}

**Forhåndsregistrert hovedvindu GW8–38:**

{table('GW8-38')}

Samlet MSE i hovedvinduet er **{new.mse:.6f}**. `p0_baseline.csv`, `p0_prediksjoner.csv.gz` og `p0_diagnostikk.csv` er de nye referansene for P1/P2.

**Avvik mot første produksjonsrekonstruksjon:** radantall og faktiske utfall er identiske. MAE i hovedvinduet går fra {ref.mae:.6f} til {new.mae:.6f}; topp20 fra {ref.top20:.6f} til {new.top20:.6f}. Dette er **målefidelitet, ikke godkjent prediksjonsgevinst**. Første wrapper injiserte en eksakt navnebasert minuttprior; produksjonens `last_season_minutes` normaliserer navn og klubbnavn. Motoren bruker nå den virkelige innleseren. Dermed kobles f.eks. David Raya Martín riktig til fjoråret; den største enkeltdifferansen er {delta.max_abs_xp:.6f} xP i 2025/26 GW2. Samlet gjennomsnittlig absolutt differanse er {delta.mean_abs_xp:.6f}, og {int(delta.rows_over_001)} av {int(delta.n)} rader endres mer enn 0,01.

**Avviket er isolert:** `p0_forklar_avvik.py` bytter *bare diagnostisk* tilbake til første wrappers minuttprior. På GW2, 8, 20 og 38 i hver sesong ({int(a.n.sum())} rader) gjenskapes gammel xP med maksimal absolutt differanse **{a.max_abs_xp.max():.2g}**. Standardmotoren beholder produksjonens navnekobling. Temperatur og øvrig matematikk er ikke endret for å få dette til.

## D0: uavhengig kontroll

**Godkjenner e1e1fb3 for avtalt D0-omfang.** Lest `optimize.py`, `fetch.py` og `test_optimize.py`; alle tester er kjørt. GW08-fasiten er salgsverdi 98,3 og 2 FT. Fetch henter nå `transfers.json`, prisøkning rundes ned i tideler, faktiske FT sendes inn i MILP, WC bevarer FT etter valgt regel, og hele tilgjengelige xP-horisonten brukes.

I tillegg består `d0_kontroll.py` selvstendige **solver-tester**, ikke bare hjelpefunksjoner: salg 5,8 blokkerer et kjøp som feilaktig salg 6,0 tillater; to FT gir to oppgraderinger uten hit; tvungen WC med 3 FT tillater nøyaktig 3 videre, ikke 1 eller 4. Hit, FT-tak, FH og gammel reset-policy er også kontrollert. Se `d0_kontroll.json`.

Avgrensning: gjenkjøp og nytt salg innen horisonten bruker fortsatt opprinnelig salgspris for opprinnelig eide spillere; det er dokumentert konservativt, ikke full dynamisk kjøpsprisregnskap. FH-planlegging, chipvinduer og håndtering av ugyldig/ufullstendig solverløsning er ikke godkjent som del av D0. Testen verifiserer implementeringen av avtalt FT-policy, ikke en ny ekstern verifisering av 2026/27-regelen.

## Se spesielt på i Claudes kontroll

1. **Minuttbroen:** fordi `minutes.py` er Claudes fil, brukes en avgrenset `StringIO` som `LAST_SEASON_GWS`. Den gamle verdien gjenopprettes ved feil. Dette er en adapter uten kopiert minuttformel, men er **ikke trådsikker**; konfigurasjoner kjøres serielt. En eksplisitt prior-parameter i `minutes.build` kan erstatte broen senere etter avtalt filoverlevering.
2. **Historiske input er fortsatt en rekonstruksjon:** eksakte navn er spilleridentiteten i datamappingen; integer-ID er stabil innen sesong/konfigurasjon, ikke det originale API-elementnummeret. Manglende status-/deadlinearkiver, observerte rostermetadata og kun neste rundes kampprogram i målkalibreringen er samme begrensninger som før. Priorenes mål/assist/BPS-totaler må rekonstrueres der eldre `cleaned_players.csv` mangler. Ikke tolk dette som arkiverte live-prognoser eller full `season_sim`-paritet.
3. **Bruk ny baseline for P1/P2.** Målekravene i `plan.md` gjelder fortsatt; P0 har ikke målt eller godkjent noen kandidat. `compare` returnerer sammenligningsstatistikk i `result.attrs['comparison']`, inkludert MSE-reduksjon og blokk-SE. En reell parvis API-kjøring på 745 rader med identiske konfigurasjoner ga nøyaktig null differanse i alle mål (`p0_compare_smoke.log`). Bonusendringer trenger i tillegg premiumkalibrering; samlet bonus-MSE alene er ikke tilstrekkelig.

Reproduser med eksisterende Anaconda-miljø (systemets `/usr/bin/python3` mangler pandas; ingen pakker er installert):

```sh
export PATH=/Users/simenflogstad/opt/anaconda3/bin:$PATH
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/
PYTHONDONTWRITEBYTECODE=1 python3 samarbeid/modell/codex/p0_baseline.py
PYTHONDONTWRITEBYTECODE=1 python3 samarbeid/modell/codex/p0_regresjon.py
PYTHONDONTWRITEBYTECODE=1 python3 samarbeid/modell/codex/d0_kontroll.py
```
'''
(O/'p0.md').write_text(text)
