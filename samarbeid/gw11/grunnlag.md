# Datagrunnlag runde 11, 2026/27

Hentet fra det offentlige FPL-API-et 2026-11-19 16:30 UTC (`data/fetched_at.txt`) av agenten `fpl-datagrunnlag`.
Råfilene ligger i `data/` (fryst etter henting). Ingen innlogging er brukt.
`data/element_summary/` har 273 filer: alle spillerne med ≥ 300 minutter (hele egen tropp er med blant dem). Alle filer er gyldig JSON
med `history`, `history_past` og `fixtures`.
`data/live_gw10.json` (faktiske poeng R10) og `data/picks_gw10.json` er hentet samtidig til evalueringen i steg 2.

## Verifisert mot FPL-API

| Fakta | Verdi | Kilde |
|---|---|---|
| Sesong | 2026/27 | `bootstrap.json` → `game_config.settings.static_content_url` |
| Siste ferdigspilte runde | 10 (`finished` og `data_checked`; alle ti R10-kamper `finished`) | `bootstrap.json` events, `fixtures.json` |
| Neste runde og frist | **Runde 11, lørdag 2026-11-21 11:00 UTC (12:00 norsk tid, CET)**. Bekreftet | `bootstrap.json` events (`is_next`) |
| Første og siste R11-kamp | MCI–FUL lørdag 21. nov 12:30 UTC (13:30 norsk tid, 90 minutter etter fristen); siste er BRE–EVE mandag 23. nov 20:00 UTC | `fixtures.json` |
| Senere frister (UTC; norsk tid = UTC + 1) | R12 fre 27. nov 18:30, **R13 tir 1. des 18:30** (midtukerunde), R14 lør 5. des 11:00, R15 lør 12. des 13:30, R16 lør 19. des 11:00, R17 lør 26. des 11:00, R18 tir 29. des 18:00, R19 fre 1. jan 2027 18:30 | `bootstrap.json` events |
| Prisjusteringer | 2026-11-20 00:00 UTC (01:00 norsk tid, natt til fredag) og 2026-11-21 00:00 UTC (01:00, natt til lørdag): **to før R11-fristen**. Den tredje, 2026-11-22 00:00 UTC, er etter fristen | `game_config.settings.price_change_deadlines` |
| Lag | lifegivesyoulammens (7089878), 641 poeng, rank 1 122 827 (fra 2 209 960 etter R9) | `entry_history.json` |
| R10 | **88 poeng** (snitt 55, høyest 139), rundens rank 79 055 (topp 1 %), 12 poeng på benken, ingen autobytter | `picks_gw10.json`, `bootstrap.json` |
| Bank | **£0,4m** | `picks_gw10.json` entry_history.bank = 4 (også `entry.json` last_deadline_bank = 4) |
| Lagverdi | Markedsverdi nå £100,8m; salgsverdi £99,5m + bank = **£99,9m**. API `value` ved R10: 1006 = markedsverdi 100,2 ved R10-fristen + bank 0,4 (stemmer) | `salgspriser.json`, `entry_history.json` |
| Brukte chips | Triple Captain (R3), Wildcard (R9) | `entry_history.json` chips |
| Tilgjengelige chips | FH1 og BB1 (til og med R19). Andre sett (WC, FH, BB, TC) R20–R38 | `bootstrap.json` chips |
| Byttehistorikk | R3: 1, R4: 1, R5: 1, R6: 2, R7: 0, R8: 1, R9: 0 (wildcard), **R10: 0**. Ingen trekk noen runde | `entry_history.json`; `last_deadline_total_transfers` = 6 |
| Blanke/doble runder | **Ingen i R11–R38** slik oppsettet står nå: alle 380 kamper har runde, og alle 20 lag har én kamp i hver runde. Ingen kamp i R11–R19 er endret siden gw10-hentingen (6. nov); 21 kamper i R21–R23 har fått nytt avspark innen samme runde | `fixtures.json` mot `gw10/data/fixtures.json` |
| Flagg i egen tropp | Ingen. Alle 15 har status `a` og tom nyhet | `bootstrap.json` |

### R10: hva Simen faktisk gjorde (kontroll mot `gw10/beslutning.md`)

Simen har ikke sagt noe om R10. Kontrollert i offentlige data:

| | Anbefalt (`gw10/beslutning.md`) | Faktisk (`picks_gw10.json`, `transfers.json`) |
|---|---|---|
| Bytter | Ingen, rull | **Ingen**: event_transfers 0, event_transfers_cost 0; `transfers.json` er byte-identisk med gw10-versjonen (siste bytte 30. okt, R9) |
| Chip | Ikke Bench Boost | **Ingen** (`active_chip` null; chips bare 3xc R3 og wildcard R9) |
| Ellever | Trafford; Gabriel, De Cuyper, Muharemović; Mbeumo, Tavernier, Ødegaard, Groß; Haaland, Isak, Barry | **Identisk** (3-4-3) |
| Kaptein / visekaptein | Haaland / Gabriel | **Haaland / Gabriel** |
| Benk | Tzolakis; Silva, Rudoni, Dasilva | **Identisk, samme rekkefølge** |

**Ingen avvik fra anbefalingen i R10.** (I R9 var visekapteinen et avvik; det er rettet.)

### Tropp etter runde 10 (rekkefølge = `picks_gw10.json`)

| # | Spiller | Lag | Pos | Kjøpt | Nå | Salg | Status | R11-kamp |
|---|---|---|---|---|---|---|---|---|
| 1 | Trafford | LEE | GKP | 5.0 | 5.0 | 5.0 | a | CHE (b) |
| 2 | Gabriel (V) | ARS | DEF | 7.9 | 8.1 | 8.0 | a | NEW (b) |
| 3 | De Cuyper | BHA | DEF | 5.3 | 5.5 | 5.4 | a | HUL (b) |
| 4 | Muharemović | LEE | DEF | 5.1 | 5.1 | 5.1 | a | CHE (b) |
| 5 | Mbeumo | MUN | MID | 8.0 | 7.9 | 7.9 | a | LIV (b) |
| 6 | Ødegaard | ARS | MID | 6.7 | 6.7 | 6.7 | a | NEW (b) |
| 7 | Groß | BHA | MID | 5.7 | 6.3 | 6.0 | a | HUL (b) |
| 8 | Tavernier | BOU | MID | 6.2 | 6.7 | 6.4 | a | NFO (h) |
| 9 | Haaland (C) | MCI | FWD | 15.5 | 15.8 | 15.6 | a | FUL (h) |
| 10 | Barry | EVE | FWD | 5.6 | 5.7 | 5.6 | a | BRE (b) |
| 11 | Isak | LIV | FWD | 9.1 | 9.3 | 9.2 | a | MUN (h) |
| 12 | Tzolakis | HUL | GKP | 4.7 | 4.7 | 4.7 | a | BHA (h) |
| 13 | Silva | BOU | DEF | 5.0 | 5.1 | 5.0 | a | NFO (h) |
| 14 | Rudoni | COV | MID | 4.9 | 4.9 | 4.9 | a | CRY (h) |
| 15 | Dasilva | COV | DEF | 4.0 | 4.0 | 4.0 | a | CRY (h) |

Lagbegrensning: ingen klubb er full. To hver fra ARS, BHA, BOU, COV og LEE; én fra HUL, MUN, MCI, EVE og LIV.
Alle 15 har én kamp i R11. Egne spillere møter hverandre i HUL–BHA (Tzolakis mot De Cuyper og Groß) og LIV–MUN (Isak mot Mbeumo).
Haaland spiller i den første kampen (MCI–FUL), 90 minutter etter fristen.

Kjøpspris er utledet på nytt fra rådataene: siste `element_in_cost` i `transfers.json` (elleve fra R9, Tavernier R8, Groß R5), og R1-pris
i `element-summary` for Haaland og Mbeumo, som har vært i troppen siden R1. Alle er identiske med `gw10/data/salgspriser.json`.
Salgspris = kjøpspris + halvparten av økningen, rundet ned til 0,1; ved prisfall er salgspris lik nåpris. Tabellen står i `data/salgspriser.json`.

Prisendringer siden gw10-hentingen (6. nov): Gabriel 8,0 → 8,1, De Cuyper 5,4 → 5,5, Groß 6,2 → 6,3, Tavernier 6,6 → 6,7, Barry 5,6 → 5,7,
Isak 9,2 → 9,3. Salgspris +0,1 for Gabriel, De Cuyper, Groß og Isak (Tavernier og Barry uendret), så salgsverdien har økt fra 99,1 til 99,5.

## Regler (fra `game_config`, ikke fra hukommelse)

Uendret fra gw10 (`game_config.scoring` og `game_config.rules` er identiske med `gw10/data/bootstrap.json`).

- 15 spillere, 11 på banen, maks 3 per klubb, budsjett 100,0.
- Gratisbytter: maks 5 lagret (`max_extra_free_transfers: 4`); ekstra bytter koster 4 poeng (standard; ikke i API-et).
- Salgsgebyr 50 % av prisstigning (`rules.transfers_sell_on_fee: 0.5`).
- Chips: FH1 og BB1 må brukes innen R19. TC1 og WC1 er brukt.
- Poeng 2026/27: mål GKP 10, DEF 6, MID 5, FWD 4; assist 3; nullet GKP/DEF 4, MID 1; −1 per 2 innslupne (GKP/DEF); 1 per 3 redninger;
  straffe redd 5, bom −2; gult −1, rødt −3, selvmål −2; defensive contribution 2 poeng (DEF, MID, FWD); spilletid 1 / 2 (60+ min).
- Kjent avvik (fra gw08): `config/scoring.yaml` sier keepermål = 6, API-et sier 10.

## Gratisbytter (beregnet, ikke verifisert)

Fra `entry_history.json` (+1 per runde, maks 5, minus brukte): R2 1 → R3 2 → R4 2 → R5 2 → R6 2 → R7 1 → R8 2 → R9 2 (wildcard) →
R10 2 (antatt) → **R11 3 (antatt)**. I R10 ble ingen bytter gjort (event_transfers 0, ingen chip), så R10 gir +1.

- **Antakelse: 3 gratisbytter i R11.** Den bygger på antakelsen fra gw10 om 2 i R10: lagrede bytter beholdes ved wildcard, men runden
  med chip gir ikke +1. Det offentlige API-et oppgir ikke antallet, og regelen for gratisbytter ved WC/FH er fortsatt ikke verifisert.
- Usikkerhet: **4** hvis wildcardrunden også ga +1 (3 i R10), og **2** hvis lagrede bytter ble nullstilt av wildcarden (1 i R10).
  Taket på 5 binder ikke i noen av tilfellene. Simen kan se riktig tall i FPL-appen under «Transfers». Det bør sjekkes før planen låses,
  særlig hvis planen bruker alle tre.

## Gitt av Simen, ikke kontrollerbart offentlig

| Opplysning | Status |
|---|---|
| Hva Simen gjorde i R10 | Ikke opplyst (ifølge hovedagenten). Offentlig kontroll: anbefalingen ble fulgt nøyaktig (se over) |
| Bytter etter R10-fristen | Ingen opplyst. Offentlige data viser laget ved R10-fristen; bytter gjort etter det, før R11-fristen, syns ikke |
| Antall gratisbytter | Ikke opplyst. Antatt 3 (se over) |

## Antakelser (ikke verifisert)

- Gratisbytter i R11 = 3 (2–4 avhengig av wildcardregelen).
- Straffen for ekstra bytter er 4 poeng (ikke i API-et).
- Ingen nye doble/blanke runder før R19. Ingen er lagt inn i `fixtures.json` nå; cupkamper kan likevel flytte ligakamper senere.
- Skadevurdering utover API-flaggene er ikke gjort her; den hører til `claude/forutsetninger.md`.

## Avvik

- Ingen feil i data. Sjekksummene i `gw10/prognose/SHA256SUMS` er OK (4 av 4). Prognosen ble committet 2026-11-06 13:34 UTC, før fristen 18:30.
- Ingen avvik mellom anbefalt og faktisk lag i R10.
- Merknad: rank avviker litt mellom endepunktene (`entry.json`: 1 122 797 totalt og 79 010 i runden; `entry_history.json`: 1 122 827 og 79 055).
  Det skyldes trolig ulik oppdateringstid i API-et og har ingen betydning. Tallene fra `entry_history.json` er brukt.
- Merknad: `data/live_gw10.json` og `data/picks_gw10.json` er lagt i ukens `data/` (gw10-mappen er bare lest).
