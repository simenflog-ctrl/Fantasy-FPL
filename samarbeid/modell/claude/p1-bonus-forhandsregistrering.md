# P1 bonus: forhåndsregistrering

Skrevet 2026-10-22, **før** noen kandidat er kjørt i Codex' målemotor. Endres ikke etter at målingen er startet;
eventuelle avvik fra planen rapporteres som avvik.

## Problem

`fit_bonus_temperature` tilpasser `tau` på realisert BPS og bruker den på forventet BPS ⇒ for skarp bonusfordeling.
Målt uavhengig av begge agentene (se `avviksrevisjon.md` og `codex/gjennomgang.md`).

## Kandidater (maks to, for å begrense vinnerflaks)

- **B1, fast tau tilpasset offline:** `tau` velges i målemotoren som den verdien som minimerer bonus-MSE walk-forward på
  **utviklingssesongene 2023-24 og 2024-25**, rutenett {4, 5, 6, 7, 8, 10, 12}. Produksjonen bruker så denne faste verdien
  (`BONUS_TAU_MODE = "fixed"`), i stedet for å tilpasse på realisert BPS.
- **B2, B1 + krymping mot egen historisk bonusrate:** `xp_bonus = a · PL-bonus + (1 − a) · (historisk bonus per 90 × minuttandel)`,
  med `a` fra rutenettet {0,5, 0,75}, valgt på de samme utviklingssesongene. Testes bare hvis B1 består.

## Låst test

- **Kontrollsesong:** 2025-26 (ikke brukt til å velge tau eller a). I tillegg rapporteres alle tre sesongene.
- **Primærmål:** parvis MSE på totalpoeng (samme rader), GW8–38.
- **Krav for å slå på:** primærmålet bedre på kontrollsesongen og samlet, minst 3 blokk-SE samlet, samme fortegn i alle tre sesonger,
  ≥ 0,5 % lavere MSE; topp-10/topp-20 ikke dårligere med mer enn 2 blokk-SE; bonus-MSE og bonuskalibrering for premiumspillere bedre.
- **Hvis B1 bare forbedrer bonus-MSE, men ikke total-MSE med 3 SE:** dette er en kjent modellfeil med en mekanistisk forklaring,
  og totalfeilen domineres av mål og nuller. Da avgjør vi ut fra kalibreringen og topp-k, og skriver eksplisitt at det primære kravet ikke ble nådd.
  Dette unntaket er skrevet ned **nå**, før resultatet er kjent.

## Arbeidsdeling

Claude implementerer B1 (og eventuelt B2) bak flagg i `src/expected_points.py` etter at Codex har levert P0. Codex kjører målingen og godkjenner.
