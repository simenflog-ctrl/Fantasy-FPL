# Datagrunnlag runde 10, 2026/27

Hentet fra det offentlige FPL-API-et 2026-11-06 06:38 UTC (`data/fetched_at.txt`) av agenten `fpl-datagrunnlag`.
Råfilene ligger i `data/` (fryst etter henting). Ingen innlogging er brukt.
`data/element_summary/` har 258 filer: alle spillerne med ≥ 300 minutter (hele egen tropp er med blant dem).
`data/live_gw9.json` (faktiske poeng R9) er hentet samtidig til evalueringen i steg 2.

## Verifisert mot FPL-API

| Fakta | Verdi | Kilde |
|---|---|---|
| Sesong | 2026/27 | `bootstrap.json` → `game_config.settings.static_content_url` |
| Siste ferdigspilte runde | 9 (`finished` og `data_checked`; alle R9-kamper `finished`) | `bootstrap.json` events, `fixtures.json` |
| Neste runde og frist | **Runde 10, 2026-11-06 18:30 UTC (19:30 norsk tid, CET)**. Bekreftet | `bootstrap.json` events |
| Første R10-kamp | EVE–COV fredag 2026-11-06 20:00 UTC (21:00 norsk tid) | `fixtures.json` |
| Runde 11-frist | 2026-11-21 11:00 UTC (12:00 norsk tid; landslagspause, 15 dager etter R10-fristen) | `bootstrap.json` events |
| Runde 12-frist | 2026-11-27 18:30 UTC (19:30 norsk tid) | samme |
| Prisjusteringer | 2026-11-07 00:00 UTC (01:00 norsk tid), 2026-11-08 00:00 UTC, 2026-11-09 00:00 UTC. **Ingen før R10-fristen**; neste er natt til lørdag, etter fristen | `game_config.settings.price_change_deadlines` |
| Lag | lifegivesyoulammens (7089878), 553 poeng, rank 2 209 960 | `entry_history.json` |
| R9 | 48 poeng (snitt 47, høyest 122), rundens rank 5 082 696, **16 poeng på benken**, ingen autobytter | `picks_gw9.json`, `bootstrap.json` |
| Bank | **£0,4m** | `picks_gw9.json` entry_history.bank = 4 (også `entry.json` last_deadline_bank = 4) |
| Lagverdi | Markedsverdi nå £100,2m; salgsverdi £99,1m + bank = **£99,5m**. (API `value` ved R9: 1002) | `salgspriser.json`, `entry_history.json` |
| Brukte chips | Triple Captain (R3), **Wildcard (R9, aktivert 2026-10-30 06:53 UTC)** | `entry_history.json` chips, `picks_gw9.json` active_chip = `wildcard` |
| Tilgjengelige chips | FH1 og BB1 (til og med R19). Andre sett (WC, FH, BB, TC) R20–R38 | `bootstrap.json` chips |
| Byttehistorikk | R3: 1, R4: 1, R5: 1, R6: 2, R7: 0, R8: 1, R9: 0 (wildcardbyttene telles ikke). Ingen trekk noen runde | `entry_history.json`; `last_deadline_total_transfers` = 6 |
| Blanke/doble runder | Ingen i R10–R38 slik oppsettet står nå; alle 380 kamper har runde, alle 20 lag har én kamp i hver runde | `fixtures.json` |
| Flagg i egen tropp | Ingen. Alle 15 har status `a` og tom nyhet | `bootstrap.json` |

### R9-wildcarden (kontroll av Simens opplysning)

`transfers.json`: elleve bytter i event 9, alle 2026-10-30 06:57 UTC (etter prisjusteringen 30. okt 00:00, før den 31. okt 00:00).
`entry_history.json`: wildcard aktivert 2026-10-30 06:53 UTC. `picks_gw9.json`: active_chip `wildcard`, event_transfers 0, cost 0.

| Ut (salg) | Inn (kjøp) |
|---|---|
| Verbruggen 4,5 | Tzolakis 4,7 |
| Steele 4,0 | Trafford 5,0 |
| Calafiori 5,8 | Gabriel 7,9 |
| Konsa 4,6 | De Cuyper 5,3 |
| N.Williams 5,0 | Silva 5,0 |
| Maguire 4,7 | Dasilva 4,0 |
| van Ewijk 3,9 | Muharemović 5,1 |
| B.Fernandes 11,7 | Ødegaard 6,7 |
| E.Le Fée 5,7 | Rudoni 4,9 |
| Thiago 7,8 | Barry 5,6 |
| Kusi-Asare 4,4 | Isak 9,1 |
| **Sum 62,1** | **Sum 63,3** |

Bank: 1,6 + 62,1 − 63,3 = **0,4**, som stemmer med API-et. Gabriel ble kjøpt til 7,9 før stigningen 31. okt, så banken er
£0,4m og ikke £0,3m.

**Tropp, inn og ut: identisk med `gw09/beslutning.md`.** Ellever, kaptein (Haaland) og benkerekkefølge (Trafford, Groß, De Cuyper,
Muharemović) er også identiske. **Avvik: visekaptein er Ødegaard, ikke Mbeumo som anbefalt.** Det hadde ingen betydning i R9,
fordi Haaland spilte 90 minutter.

### Tropp etter runde 9 (rekkefølge = `picks_gw9.json`)

| # | Spiller | Lag | Pos | Kjøpt | Nå | Salg | Status | R10-kamp |
|---|---|---|---|---|---|---|---|---|
| 1 | Tzolakis | HUL | GKP | 4.7 | 4.7 | 4.7 | a | ARS (b) |
| 2 | Gabriel | ARS | DEF | 7.9 | 8.0 | 7.9 | a | HUL (h) |
| 3 | Silva | BOU | DEF | 5.0 | 5.1 | 5.0 | a | IPS (b) |
| 4 | Dasilva | COV | DEF | 4.0 | 4.0 | 4.0 | a | EVE (b) |
| 5 | Mbeumo | MUN | MID | 8.0 | 7.9 | 7.9 | a | AVL (h) |
| 6 | Ødegaard (V) | ARS | MID | 6.7 | 6.7 | 6.7 | a | HUL (h) |
| 7 | Rudoni | COV | MID | 4.9 | 4.9 | 4.9 | a | EVE (b) |
| 8 | Tavernier | BOU | MID | 6.2 | 6.6 | 6.4 | a | IPS (b) |
| 9 | Haaland (C) | MCI | FWD | 15.5 | 15.8 | 15.6 | a | NFO (b) |
| 10 | Barry | EVE | FWD | 5.6 | 5.6 | 5.6 | a | COV (h) |
| 11 | Isak | LIV | FWD | 9.1 | 9.2 | 9.1 | a | CRY (b) |
| 12 | Trafford | LEE | GKP | 5.0 | 5.0 | 5.0 | a | TOT (h) |
| 13 | Groß | BHA | MID | 5.7 | 6.2 | 5.9 | a | BRE (h) |
| 14 | De Cuyper | BHA | DEF | 5.3 | 5.4 | 5.3 | a | BRE (h) |
| 15 | Muharemović | LEE | DEF | 5.1 | 5.1 | 5.1 | a | TOT (h) |

Lagbegrensning: ingen klubb er full. To hver fra ARS, BOU, COV, LEE og BHA; én fra HUL, MUN, MCI, EVE og LIV.
Alle 15 spiller i R10. Barry, Dasilva og Rudoni spiller i fredagskampen EVE–COV, 90 minutter etter fristen.

Kjøpspris: de elleve wildcardspillerne fra `element_in_cost` i `transfers.json` (R9). Haaland og Mbeumo fra R1-pris, Tavernier og
Groß fra tidligere kjøp i `transfers.json`, alle uendret fra `gw09/data/salgspriser.json`. Salgspris = kjøpspris + halvparten av
økningen, rundet ned til 0,1; ved prisfall er salgspris lik nåpris. Tabellen står i `data/salgspriser.json`.

## Regler (fra `game_config`, ikke fra hukommelse)

- 15 spillere, 11 på banen, maks 3 per klubb, budsjett 100,0.
- Gratisbytter: maks 5 lagret (`max_extra_free_transfers: 4`); ekstra bytter koster 4 poeng (standard; ikke i API-et).
- Salgsgebyr 50 % av prisstigning (`rules.transfers_sell_on_fee: 0.5`).
- Chips: FH1 og BB1 må brukes innen R19. TC1 og WC1 er brukt.
- Poeng 2026/27 (`game_config.scoring`), uendret fra gw08/gw09: mål GKP 10, DEF 6, MID 5, FWD 4; assist 3; nullet GKP/DEF 4, MID 1;
  −1 per 2 innslupne (GKP/DEF); 1 per 3 redninger; straffe redd 5, bom −2; gult −1, rødt −3, selvmål −2;
  defensive contribution 2 poeng (DEF, MID, FWD); spilletid 1 / 2 (60+ min).
- Kjent avvik (fra gw08): `config/scoring.yaml` sier keepermål = 6, API-et sier 10.

## Gratisbytter (beregnet, ikke verifisert)

R9 startet med 2 (gw09). I R9 ble wildcard brukt, og API-et viser `event_transfers` 0 og `event_transfers_cost` 0 for R9;
`last_deadline_total_transfers` er fortsatt 6, så wildcardbyttene er ikke regnet som vanlige bytter.
Antall gratisbytter oppgis ikke i det offentlige API-et, og regelen for gratisbytter ved WC/FH er ikke verifisert.

- **Antakelse: 2 gratisbytter i R10.** Dette forutsetter at lagrede gratisbytter beholdes ved wildcard, men at runden med chip
  ikke gir et ekstra bytte. Det samme ble lagt til grunn i `gw09/prognose/prognose_R9.json` (`ft_til_R10: 2`).
- Usikkerhet: 3 hvis runden med wildcard også gir +1, og 1 hvis lagrede bytter nullstilles ved wildcard. Simen kan se det riktige
  tallet i FPL-appen under «Transfers». Det bør sjekkes før planen låses.

## Gitt av Simen, ikke kontrollerbart offentlig

| Opplysning | Status |
|---|---|
| Wildcard før R9-fristen, «Jeg er klar» | **Bekreftet**: wildcard aktivert 30. okt 06:53 UTC, elleve bytter 06:57 UTC |
| Anbefalt R9-tropp, ellever, kaptein og benk | **Bekreftet** identisk, bortsett fra visekaptein (Ødegaard i stedet for Mbeumo) |
| Gabriel steg til £8,0m 31. okt, bank kanskje £0,3m | Prisstigningen stemmer (nå 8,0), men kjøpet skjedde 30. okt til 7,9; **bank £0,4m** |
| Bytter etter R9-fristen | Ingen opplyst. Offentlige data viser laget ved R9-fristen; senere bytter syns ikke |

## Antakelser (ikke verifisert)

- Gratisbytter i R10 = 2 (se over).
- Straffen for ekstra bytter er 4 poeng (ikke i API-et).
- Ingen nye doble/blanke runder før R19. Cupkamper kan flytte ligakamper senere.
- Skadevurdering utover API-flaggene er ikke gjort her; hører til `claude/forutsetninger.md`.

## Avvik

- Ingen feil i data. Sjekksummene i `gw09/prognose/SHA256SUMS` er OK (4 av 4).
- Visekaptein i R9 var Ødegaard, ikke Mbeumo som i `gw09/beslutning.md` (uten betydning for poengene i R9).
- Merknad: første hentingsforsøk feilet med HTTP 400 fordi zsh-løkken ikke delte argumentene (feil i agentens kommando, ikke i API-et).
  Alt ble hentet på nytt med bash; alle filer er gyldig JSON.
- Merknad: `data/live_gw9.json` er lagt i ukens `data/` (gw09-mappen er bare lest).
