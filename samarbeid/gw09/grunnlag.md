# Datagrunnlag runde 9, 2026/27

Hentet fra det offentlige FPL-API-et 2026-10-29 06:37 UTC (`data/fetched_at.txt`) av agenten `fpl-datagrunnlag`.
Råfilene ligger i `data/` (fryst etter henting). Ingen innlogging er brukt.
`data/element_summary/` har 241 filer: de 239 spillerne med ≥ 300 minutter, pluss Steele og Kusi-Asare fra egen tropp.
`data/live_gw8.json` (faktiske poeng R8) er hentet samtidig til evalueringen i steg 2.

## Verifisert mot FPL-API

| Fakta | Verdi | Kilde |
|---|---|---|
| Sesong | 2026/27 | `bootstrap.json` → `game_config.settings.static_content_url` |
| Siste ferdigspilte runde | 8 (`finished` og `data_checked`) | `bootstrap.json` events |
| Neste runde og frist | **Runde 9, 2026-10-31 11:00 UTC (12:00 norsk tid)** | `bootstrap.json` events |
| Runde 10-frist | 2026-11-06 18:30 UTC (19:30 norsk tid) | samme |
| Runde 11-frist | 2026-11-21 11:00 UTC (12:00 norsk tid; 15 dager etter R10-fristen) | samme |
| Prisjusteringer | 2026-10-30 00:00 UTC (01:00 norsk tid), 2026-10-31 00:00 UTC, 2026-11-01 00:00 UTC. **Neste: 30. okt 00:00 UTC**; to justeringer før R9-fristen | `game_config.settings.price_change_deadlines` |
| Lag | lifegivesyoulammens (7089878), 505 poeng, rank 2 009 162 | `entry_history.json`, `picks_gw8.json` |
| R8 | 61 poeng (snitt 45, høyest 120), rundens rank 1 099 531, 2 poeng på benken | `picks_gw8.json`, `bootstrap.json` |
| Bank | **£1,6m** | `picks_gw8.json` entry_history.bank = 16 |
| Lagverdi | Markedsverdi nå £98,8m; salgsverdi £97,8m + bank = **£99,4m**. (API `value` ved R8: 1001) | `salgspriser.json`, `entry_history.json` |
| Brukte chips | Triple Captain (runde 3) | `entry_history.json` |
| Tilgjengelige chips | WC1, FH1, BB1 (alle til og med R19). Andre sett (WC, FH, BB, TC) R20–R38 | `bootstrap.json` chips |
| Byttehistorikk | R3: 1, R4: 1, R5: 1, R6: 2, R7: 0, R8: 1 (ingen trekk noen runde) | `entry_history.json` |
| Blanke/doble runder | Ingen i R9–R38 slik oppsettet står nå; alle 380 kamper har runde | `fixtures.json` |

### R8-byttet (kontroll av Simens opplysning)

`transfers.json`: event 8, Szoboszlai (368, salg £6,8m) → Tavernier (68, kjøp £6,2m), 2026-10-22 16:28 UTC.
`picks_gw8.json`: event_transfers 1, event_transfers_cost 0, bank 1,6. **Simens opplysning stemmer**: byttet ble gjort før
R8-fristen (og før prisjusteringen 22. okt), med ett gratisbytte og uten trekk.
Ellever, benkerekkefølge, kaptein (Haaland) og visekaptein (B.Fernandes) i R8 er identisk med `gw08/beslutning.md`.
Autobytte i R8: B.Fernandes (0 min) ut, Maguire inn.

### Tropp etter runde 8 (rekkefølge = `picks_gw8.json` etter autobytte)

| # | Spiller | Lag | Pos | Kjøpt | Nå | Salg | Status |
|---|---|---|---|---|---|---|---|
| 1 | Verbruggen | BHA | GKP | 4.5 | 4.6 | 4.5 | a |
| 2 | Calafiori | ARS | DEF | 5.7 | 6.0 | 5.8 | **d, 75 %: «Hip injury»** |
| 3 | N.Williams | NFO | DEF | 5.0 | 5.0 | 5.0 | **d, 75 %: «Arm injury»** |
| 4 | Konsa | ARS | DEF | 4.5 | 4.7 | 4.6 | a |
| 5 | Maguire | MUN | DEF | 5.0 | 4.7 | 4.7 | a (kom inn for Fernandes i R8) |
| 6 | Mbeumo | MUN | MID | 8.0 | 7.9 | 7.9 | a |
| 7 | Tavernier | BOU | MID | 6.2 | 6.4 | 6.3 | a |
| 8 | E.Le Fée | SUN | MID | 5.7 | 5.7 | 5.7 | a |
| 9 | Groß | BHA | MID | 5.7 | 6.2 | 5.9 | a |
| 10 | Haaland (C) | MCI | FWD | 15.5 | 15.8 | 15.6 | a |
| 11 | Thiago | BRE | FWD | 7.8 | 7.8 | 7.8 | a |
| 12 | Steele | BHA | GKP | 4.0 | 4.0 | 4.0 | a |
| 13 | B.Fernandes (V) | MUN | MID | 12.0 | 11.7 | 11.7 | a (0 min i R8; ingen nyhet i API-et) |
| 14 | van Ewijk | COV | DEF | 4.0 | 3.9 | 3.9 | a |
| 15 | Kusi-Asare | FUL | FWD | 4.5 | 4.4 | 4.4 | a |

Lagbegrensning: **MUN 3** (Maguire, Mbeumo, Fernandes) og **BHA 3** (Verbruggen, Steele, Groß) er fulle; ARS 2.

Kjøpspris: de opprinnelige spillerne fra rundepris R1 i `element-summary`, de andre fra siste kjøp i `transfers.json`.
Alle kjøpspriser er like med `gw08/data/salgspriser.json`; Tavernier er ny (6,2). Salgspris = kjøpspris + halvparten av
økningen, rundet ned til 0,1; ved prisfall er salgspris lik nåpris. Tabellen står i `data/salgspriser.json`.

## Regler (fra `game_config`, ikke fra hukommelse)

- 15 spillere, 11 på banen, maks 3 per klubb, budsjett 100,0.
- Gratisbytter: maks 5 lagret (`max_extra_free_transfers: 4`); ekstra bytter koster 4 poeng (standard; ikke i API-et).
- Salgsgebyr 50 % av prisstigning (`rules.transfers_sell_on_fee: 0.5`).
- Chips: WC1, FH1, BB1 må brukes innen R19. TC1 er brukt.
- Poeng 2026/27 (`game_config.scoring`), uendret fra gw08: mål GKP 10, DEF 6, MID 5, FWD 4; assist 3; nullet GKP/DEF 4, MID 1;
  −1 per 2 innslupne (GKP/DEF); 1 per 3 redninger; straffe redd 5, bom −2; gult −1, rødt −3, selvmål −2;
  defensive contribution 2 poeng (DEF, MID, FWD); spilletid 1 / 2 (60+ min).
- Kjent avvik (fra gw08): `config/scoring.yaml` sier keepermål = 6, API-et sier 10.

## Gratisbytter (beregnet)

R8 startet med 2 (bekreftet i gw08). 1 brukt i R8 → 2 − 1 + 1 = **2 gratisbytter i R9**. Stemmer med `gw08/beslutning.md`
(«Gratisbytter til R9: 2»). Ikke direkte oppgitt i offentlig API.

## Gitt av Simen, ikke kontrollerbart offentlig

| Opplysning | Status |
|---|---|
| Szoboszlai → Tavernier før R8-fristen, 1 gratisbytte, ingen trekk | **Bekreftet** i `transfers.json` og `picks_gw8.json` |
| Bytter etter R8-fristen | Ingen opplyst. Offentlige data viser laget ved R8-fristen; senere bytter syns ikke |

## Antakelser (ikke verifisert)

- Straffen for ekstra bytter er 4 poeng (ikke i API-et).
- Gratisbytteregelen ved WC/FH er ikke verifisert.
- Ingen nye doble/blanke runder før R19. Cupkamper kan flytte ligakamper senere.
- Skadevurdering utover API-flaggene (Calafiori, N.Williams, Fernandes' 0 minutter) er ikke gjort her; hører til `claude/forutsetninger.md`.

## Avvik

- Ingen feil i data. Sjekksummene i `gw08/prognose/SHA256SUMS` er OK (4 av 4).
- Merknad: `element_summary/` har 241 filer mot ≈ 220 i gw08, fordi flere spillere har passert 300 minutter.
- Merknad: `data/live_gw8.json` er lagt i ukens `data/` (ikke i gw08-mappen, som bare leses).
