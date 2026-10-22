# Datagrunnlag runde 8, 2026/27

Hentet fra det offentlige FPL-API-et 2026-10-22 15:01 UTC (`data/fetched_at.txt`).
Råfilene ligger i `data/`. Ingen innlogging er brukt.

## Verifisert mot FPL-API

| Fakta | Verdi | Kilde |
|---|---|---|
| Sesong | 2026/27 | `bootstrap.json` → `game_config.settings.static_content_url` |
| Siste ferdigspilte runde | 7 | `bootstrap.json` events |
| Neste runde og frist | Runde 8, 2026-10-23 17:30 UTC (19:30 norsk tid) | `bootstrap.json` events |
| Runde 9-frist | 2026-10-31 11:00 UTC | samme |
| Lag | lifegivesyoulammens (7089878), 444 poeng, rank 2 863 812 | `entry.json`, `picks_gw7.json` |
| Bank | £1,0m | `picks_gw7.json` entry_history.bank = 10 |
| Lagverdi | £99,9m (markedsverdi); salgsverdi £98,3m + bank = **£99,3m** | `salgspriser.json` |
| Brukte chips | Triple Captain (runde 3) | `entry_history.json` |
| Byttehistorikk | R3: 1, R4: 1, R5: 1, R6: 2, R7: 0 | `entry_history.json` |
| Blanke/doble runder | Ingen i R8–R38 slik oppsettet står nå; alle 380 kamper har runde | `fixtures.json` |
| Prisendringer | Neste prisjustering 2026-10-22 23:00 UTC (før fristen) | `game_config.settings.price_change_deadlines` |

### Tropp etter runde 7 (rekkefølge = oppstilling R7)

| # | Spiller | Lag | Pos | Kjøpt | Nå | Salg | Status |
|---|---|---|---|---|---|---|---|
| 1 | Verbruggen | BHA | GKP | 4.5 | 4.6 | 4.5 | a |
| 2 | Calafiori | ARS | DEF | 5.7 | 6.0 | 5.8 | a |
| 3 | Maguire | MUN | DEF | 5.0 | 4.8 | 4.8 | a |
| 4 | N.Williams | NFO | DEF | 5.0 | 5.0 | 5.0 | a |
| 5 | Konsa | ARS | DEF | 4.5 | 4.6 | 4.5 | a |
| 6 | Mbeumo | MUN | MID | 8.0 | 7.8 | 7.8 | a |
| 7 | B.Fernandes (V) | MUN | MID | 12.0 | 11.8 | 11.8 | a |
| 8 | E.Le Fée | SUN | MID | 5.7 | 5.7 | 5.7 | a |
| 9 | Groß | BHA | MID | 5.7 | 6.2 | 5.9 | a |
| 10 | Haaland (C) | MCI | FWD | 15.5 | 15.7 | 15.6 | a |
| 11 | Thiago | BRE | FWD | 7.8 | 7.8 | 7.8 | a |
| 12 | Steele | BHA | GKP | 4.0 | 4.0 | 4.0 | a |
| 13 | Szoboszlai | LIV | MID | 7.0 | 6.8 | 6.8 | **i, 0 %: hamstring, ukjent comeback** |
| 14 | van Ewijk | COV | DEF | 4.0 | 3.9 | 3.9 | a |
| 15 | Kusi-Asare | FUL | FWD | 4.5 | 4.4 | 4.4 | a |

Lagbegrensning: **MUN har 3** (Maguire, Mbeumo, Fernandes), ARS 2, BHA 3 (Verbruggen, Steele, Groß).
BHA er dermed også fullt.

Kjøpspris er rekonstruert: de opprinnelige spillerne fra rundepris R1 i `element-summary`,
de andre fra `transfers.json`. Salgspris = kjøpspris + halvparten av økningen, rundet ned
til 0,1; ved prisfall er salgspris lik nåpris.

## Regler (fra `game_config`, ikke fra hukommelse)

- 15 spillere, maks 3 per klubb, budsjett 100,0.
- Gratisbytter: maks 5 lagret (`max_extra_free_transfers: 4`), ekstra bytter koster 4 poeng (standard; API-et oppgir ikke beløpet, se under).
- Salgsgebyr 50 % av prisstigning (`transfers_sell_on_fee: 0.5`).
- Chips: ett sett per halvdel. **WC1, FH1 og BB1 må brukes innen runde 19, ellers går de tapt.** Andre halvdel (R20–38) gir nytt WC, FH, BB og TC.
- Poeng 2026/27 (`game_config.scoring`): mål GKP 10, DEF 6, MID 5, FWD 4; assist 3; nullet GKP/DEF 4, MID 1; -1 per 2 innslupne (GKP/DEF); 1 per 3 redninger; defensive contribution 2 poeng (DEF, MID, FWD); spilletid 1 / 2 (60+ min).

**Avvik oppdaget:** `config/scoring.yaml` i repoet sier keepermål = 6, API-et for 2026/27 sier 10. Liten praktisk betydning, men modellen bør bruke API-verdien.

## Gitt av bruker, ikke kontrollerbart offentlig

| Opplysning | Status |
|---|---|
| 2 gratisbytter | **Stemmer med beregning:** R2 0 brukt → 2 i R3; 1/1/1 brukt i R3–R5 (+1 hver runde) → 2 i R6; 2 brukt → 1 i R7; 0 brukt → **2 i R8** |
| £1,0m i bank | Bekreftet (offentlig bank etter R7-fristen) |
| WC, FH, BB tilgjengelige; TC brukt | Bekreftet: bare 3xc i chip-historikken |
| Troppen | Bekreftet identisk med offentlig R7-tropp |

Offentlige data viser laget slik det var ved R7-fristen. Bytter gjort etter det, før R8,
syns ikke. Brukeren rapporterte samme tropp 22. okt, så det antas at ingen bytter er gjort.

## Antakelser (ikke verifisert)

- Straffen for ekstra bytter er 4 poeng (ikke i API-et).
- Defensive contribution-terskler (DEF 10 CBIT, MID/FWD 12 CBIRT): skal kontrolleres.
- Ingen nye doble/blanke runder før R19. Cupkamper kan flytte ligakamper senere.
