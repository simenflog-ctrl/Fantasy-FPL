# Datagrunnlag runde 12, 2026/27

Hentet fra det offentlige FPL-API-et 2026-11-26 07:44 UTC (`data/fetched_at.txt`, tidspunktet ved start av hentingen) av agenten
`fpl-datagrunnlag`. Det er en automatisk kjøring torsdag 26. november, og Simen har ikke gitt noen opplysninger.
Råfilene ligger i `data/` (fryst etter henting). Ingen innlogging er brukt.
`data/element_summary/` har 282 filer: alle spillerne med ≥ 300 minutter (hele egen tropp er med blant dem). Alle filer er gyldig JSON
med `history`, `history_past` og `fixtures`.
`data/live_gw11.json` (faktiske poeng R11) og `data/picks_gw11.json` er hentet samtidig til evalueringen i steg 2.

## Verifisert mot FPL-API

| Fakta | Verdi | Kilde |
|---|---|---|
| Sesong | 2026/27 | `bootstrap.json` → `game_config.settings.static_content_url` (`.../2026_27/`) |
| Siste ferdigspilte runde | 11 (`finished` og `data_checked`; alle ti R11-kamper `finished`) | `bootstrap.json` events, `fixtures.json` |
| Neste runde og frist | **Runde 12, fredag 2026-11-27 18:30 UTC (19:30 norsk tid, CET)** | `bootstrap.json` events (`is_next`) |
| Første og siste R12-kamp | NFO–CHE fredag 27. nov 20:00 UTC (21:00 norsk tid, 90 minutter etter fristen); siste er ARS–MCI søndag 29. nov 16:30 UTC | `fixtures.json` |
| Senere frister (UTC; norsk tid = UTC + 1) | **R13 tir 1. des 18:30** (midtukerunde, fire dager etter R12-fristen), R14 lør 5. des 11:00, R15 lør 12. des 13:30, R16 lør 19. des 11:00, R17 lør 26. des 11:00, R18 tir 29. des 18:00, R19 fre 1. jan 2027 18:30, R20 tir 5. jan 18:00 | `bootstrap.json` events |
| Prisjusteringer | **2026-11-27 00:00 UTC (01:00 norsk tid, natt til fredag): den eneste før R12-fristen.** 28. og 29. nov 00:00 UTC er etter fristen | `game_config.settings.price_change_deadlines` |
| Lag | lifegivesyoulammens (7089878), **708 poeng**, rank **403 909** (fra 1 122 827 etter R10) | `entry_history.json` |
| R11 | **67 poeng** med Bench Boost (snitt 35, høyest 106), rundens rank 29 427 (topp 1 %), ingen autobytter | `picks_gw11.json`, `bootstrap.json` |
| Bank | **£0,4m** | `picks_gw11.json` entry_history.bank = 4 (også `entry.json` last_deadline_bank = 4) |
| Lagverdi | Markedsverdi nå £101,2m; salgsverdi £99,5m + bank = **£99,9m**. API `value` ved R11: 1011 = markedsverdi 100,7 ved R11 (rundepris i `element-summary`) + bank 0,4 (stemmer) | `salgspriser.json`, `entry_history.json` |
| Brukte chips | Triple Captain (R3), Wildcard (R9), **Bench Boost (R11)**, aktivert 2026-11-21 08:55 UTC | `entry_history.json` chips, `picks_gw11.json` active_chip = `bboost` |
| Tilgjengelige chips | **Bare Free Hit 1** (til og med R19). Andre sett (WC, FH, BB, TC) R20–R38 | `bootstrap.json` chips |
| Byttehistorikk | R3: 1, R4: 1, R5: 1, R6: 2, R7: 0, R8: 1, R9: 0 (wildcard), R10: 0, **R11: 1**. Ingen trekk noen runde | `entry_history.json`; `last_deadline_total_transfers` = 7 |
| Blanke/doble runder | **Ingen i R12–R38** slik oppsettet står nå: alle 380 kamper har runde, og alle 20 lag har én kamp i hver runde. Ingen kamp har endret runde eller avspark siden gw11-hentingen (19. nov) | `fixtures.json` mot `gw11/data/fixtures.json` |
| Flagg i egen tropp | Ingen. Alle 15 har status `a` og tom nyhet. Van Hecke, Haaland, Isak og Rudoni har `chance_of_playing_next_round` = 100 (ikke null), uten nyhet | `bootstrap.json` |

### R11: hva Simen faktisk gjorde (kontroll mot `gw11/beslutning.md`)

Simen har ikke sagt noe om R11. Kontrollert i offentlige data:

| | Anbefalt (`gw11/beslutning.md`) | Faktisk (`picks_gw11.json`, `transfers.json`) |
|---|---|---|
| Bytter | Muharemović → Van Hecke (1 gratisbytte) | **Muharemović → Van Hecke** (5,1 → 5,1), gjort 21. nov 08:54 UTC, etter prisjusteringen kl. 00:00 UTC, men Van Hecke var ikke steget. event_transfers 1, kostnad 0. Ingen andre nye rader i `transfers.json` |
| Chip | Bench Boost | **Bench Boost** (aktivert 08:55 UTC) |
| Ellever | Tzolakis; Gabriel, Van Hecke, De Cuyper; Ødegaard, Tavernier, Groß, Rudoni, Mbeumo; Isak, Haaland (3-5-2) | **Trafford**; Gabriel, De Cuyper, Van Hecke; Mbeumo, Ødegaard, Groß, Tavernier; Haaland, **Barry**, Isak (3-4-3, R10-oppstillingen med Van Hecke for Muharemović) |
| Kaptein / visekaptein | Haaland / Gabriel | Haaland / **Isak** |
| Benk | Trafford; Barry, Silva, Dasilva | **Tzolakis; Silva, Rudoni, Dasilva** |

**Bytte, chip og kaptein som anbefalt.** Avvik i oppstilling (keeper og Barry/Rudoni) og visekaptein. Med Bench Boost telte alle 15, og
Haaland spilte 90 minutter, så avvikene endret ikke poengsummen: 67 i begge tilfeller (se `claude/evaluering-forrige.md`).

### Tropp etter runde 11 (rekkefølge = `picks_gw11.json`)

| # | Spiller | Lag | Pos | Kjøpt | Nå | Salg | Status | R12-kamp |
|---|---|---|---|---|---|---|---|---|
| 1 | Trafford | LEE | GKP | 5.0 | 5.1 | 5.0 | a | COV (h) |
| 2 | Gabriel | ARS | DEF | 7.9 | 8.1 | 8.0 | a | MCI (h) |
| 3 | De Cuyper | BHA | DEF | 5.3 | 5.5 | 5.4 | a | NEW (h) |
| 4 | Van Hecke | TOT | DEF | 5.1 | 5.2 | 5.1 | a | SUN (b) |
| 5 | Mbeumo | MUN | MID | 8.0 | 7.8 | 7.8 | a | BRE (h) |
| 6 | Ødegaard | ARS | MID | 6.7 | 6.7 | 6.7 | a | MCI (h) |
| 7 | Groß | BHA | MID | 5.7 | 6.3 | 6.0 | a | NEW (h) |
| 8 | Tavernier | BOU | MID | 6.2 | 6.8 | 6.5 | a | FUL (b) |
| 9 | Haaland (C) | MCI | FWD | 15.5 | 15.8 | 15.6 | a | ARS (b) |
| 10 | Barry | EVE | FWD | 5.6 | 5.7 | 5.6 | a | LIV (h) |
| 11 | Isak (V) | LIV | FWD | 9.1 | 9.4 | 9.2 | a | EVE (b) |
| 12 | Tzolakis | HUL | GKP | 4.7 | 4.7 | 4.7 | a | CRY (b) |
| 13 | Silva | BOU | DEF | 5.0 | 5.1 | 5.0 | a | FUL (b) |
| 14 | Rudoni | COV | MID | 4.9 | 5.0 | 4.9 | a | LEE (b) |
| 15 | Dasilva | COV | DEF | 4.0 | 4.0 | 4.0 | a | LEE (b) |

Lagbegrensning: ingen klubb er full. To hver fra ARS, BHA, BOU og COV; én fra LEE, TOT, MUN, MCI, EVE, LIV og HUL.
Alle 15 har én kamp i R12. Egne spillere møter hverandre i ARS–MCI (Gabriel og Ødegaard mot Haaland), LEE–COV (Trafford mot Rudoni og
Dasilva) og EVE–LIV (Barry mot Isak).
Mbeumo spilte bare 21 minutter i R11 (status `a`, ingen nyhet); vurderingen hører til `claude/forutsetninger.md`.

Kjøpspris er utledet på nytt fra rådataene: siste `element_in_cost` i `transfers.json` (Van Hecke R11, ti fra R9, Tavernier R8, Groß R5),
og R1-pris i `element-summary` for Haaland og Mbeumo, som har vært i troppen siden R1. De fjorten som også var i troppen forrige uke,
har samme kjøpspris som i `gw11/data/salgspriser.json`.
Salgspris = kjøpspris + halvparten av økningen, rundet ned til 0,1; ved prisfall er salgspris lik nåpris. Tabellen står i `data/salgspriser.json`.

Prisendringer siden gw11-hentingen (19. nov): Trafford 5,0 → 5,1, Van Hecke 5,1 → 5,2 (etter kjøpet), Tavernier 6,7 → 6,8, Isak 9,3 → 9,4,
Rudoni 4,9 → 5,0, Mbeumo 7,9 → 7,8. Salgspris: Tavernier +0,1 (6,4 → 6,5), Mbeumo −0,1 (7,9 → 7,8); de andre er uendret.
Salgsverdien er 99,5 som forrige uke (Muharemović 5,1 ut, Van Hecke 5,1 inn).

## Regler (fra `game_config`, ikke fra hukommelse)

Uendret fra gw11 (`game_config.scoring` og `game_config.rules` er identiske med `gw11/data/bootstrap.json`).

- 15 spillere, 11 på banen, maks 3 per klubb, budsjett 100,0.
- Gratisbytter: maks 5 lagret (`max_extra_free_transfers: 4`); ekstra bytter koster 4 poeng (standard; ikke i API-et).
- Salgsgebyr 50 % av prisstigning (`rules.transfers_sell_on_fee: 0.5`).
- Chips: FH1 må brukes innen R19. TC1, WC1 og BB1 er brukt.
- Poeng 2026/27: mål GKP 10, DEF 6, MID 5, FWD 4; assist 3; nullet GKP/DEF 4, MID 1; −1 per 2 innslupne (GKP/DEF); 1 per 3 redninger;
  straffe redd 5, bom −2; gult −1, rødt −3, selvmål −2; defensive contribution 2 poeng (DEF, MID, FWD); spilletid 1 / 2 (60+ min).
- Kjent avvik (fra gw08): `config/scoring.yaml` sier keepermål = 6, API-et sier 10.

## Gratisbytter (beregnet, ikke verifisert)

Fra `entry_history.json` (+1 per runde, maks 5, minus brukte): R2 1 → R3 2 → R4 2 → R5 2 → R6 2 → R7 1 → R8 2 → R9 2 (wildcard) →
R10 2 (antatt) → R11 3 (antatt) → **R12 3 (antatt)**. I R11 ble ett gratisbytte brukt (event_transfers 1, kostnad 0), og Bench Boost
påvirker ikke gratisbyttene: 3 − 1 + 1 = 3.

- **Antakelse: 3 gratisbytter i R12.** Usikkerheten fra wildcarden i R9 er ikke løst og går videre: **4** hvis wildcardrunden ga +1,
  **2** hvis lagrede bytter ble nullstilt. Det offentlige API-et oppgir ikke antallet. Simen ser riktig tall i appen under «Transfers».
  At byttet i R11 kostet 0 poeng, utelukker bare at han hadde 0 (det var aldri mulig).

## Gitt av Simen, ikke kontrollerbart offentlig

| Opplysning | Status |
|---|---|
| Hva Simen gjorde i R11 | Ikke opplyst (automatisk kjøring). Offentlig kontroll: bytte, Bench Boost og kaptein som anbefalt; avvik i oppstilling og visekaptein uten poengeffekt (se over) |
| Bytter etter R11-fristen | Ingen opplyst. Offentlige data viser laget ved R11-fristen; bytter gjort etter det, før R12-fristen, syns ikke |
| Antall gratisbytter | Ikke opplyst. Antatt 3 (se over) |

## Antakelser (ikke verifisert)

- Gratisbytter i R12 = 3 (2–4 avhengig av wildcardregelen).
- Straffen for ekstra bytter er 4 poeng (ikke i API-et).
- Ingen nye doble/blanke runder før R19. Ingen er lagt inn i `fixtures.json` nå; cupkamper kan likevel flytte ligakamper senere.
- Skadevurdering utover API-flaggene er ikke gjort her; den hører til `claude/forutsetninger.md`.

## Avvik

- Ingen feil i data. Sjekksummene i `gw11/prognose/SHA256SUMS` er OK (5 av 5). Prognosen ble committet 2026-11-20 11:19 UTC, før fristen
  21. nov 11:00 UTC.
- Avvik fra anbefalingen i R11: oppstilling (Trafford i mål i stedet for Tzolakis, Barry i stedet for Rudoni, 3-4-3) og visekaptein (Isak
  i stedet for Gabriel). Ingen poengeffekt, fordi Bench Boost var aktiv og kapteinen spilte.
- **Prognoseevalueringen har for første gang tydelige skjevheter etter kriteriet** (fire runder). Den ene (repo_hybrid, FWD ≥ 10,0)
  bygger på bare fire observasjoner av én spiller (Haaland). Se `claude/evaluering-forrige.md`.
- Merknad: rank avviker litt mellom endepunktene (`entry.json`: 403 908 totalt og 29 412 i runden; `entry_history.json`: 403 909 og 29 427).
  Tallene fra `entry_history.json` er brukt.
- Merknad: kalibreringsskriptet trenger pandas, som systemets `python3` (3.9) mangler. Det ble kjørt med `~/opt/anaconda3/bin/python3`
  (pandas 1.2.4). Skriptet er ikke endret.
