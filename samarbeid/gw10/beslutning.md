# Beslutning runde 10 (2026/27)

Tatt av Claude 2026-11-06 ca. 13:34 UTC, etter analyse og én kritikkrunde med Codex (Codex stoppet to ganger på bruksgrensen; se `oppgaver.md`).
Prognosen er frosset i `prognose/prognose_R10.json` (sjekksummer i `prognose/SHA256SUMS`) og skal ikke endres etter fristen 18:30 UTC.

## Handling nå

| | |
|---|---|
| Bytter | **Ingen. Rull gratisbyttene** (antatt 2 → 3 til R11; maks 5) |
| Poengtrekk | 0 |
| Bank | £0,4m |
| Chips | **Ikke Bench Boost nå.** Foreløpig BB12, FH13 |

**Startellever (3-4-3):** Trafford; Gabriel, De Cuyper, Muharemović; Mbeumo, Tavernier, Ødegaard, Groß; Haaland, Isak, Barry.
**Kaptein:** Haaland. **Visekaptein:** Gabriel.
**Benk:** Tzolakis (GK); 1. Silva, 2. Rudoni, 3. Dasilva.

Tzolakis står over i R10 (HUL borte mot ARS); Trafford (LEE hjemme mot TOT) starter.

## Rullerende plan R10–R17 (alt etter R10 er foreløpig)

| Runde | Frist (UTC) | Plan |
|---|---|---|
| R10 | 6. nov 18:30 | Ingen bytter. |
| R11 | 21. nov 11:00 | *Foreløpig:* 3 gratisbytter etter landslagspausen. Reparer skader; Dasilva → Van Hecke er førstekandidat. |
| R12 | 27. nov 18:30 | *Foreløpig:* **Bench Boost** (beste BB-dato i blandingen av poengsettene). |
| R13 | – | *Foreløpig:* **Free Hit** (modellene er uenige mot FH16; revurderes). |
| R14–R17 | – | *Foreløpig:* gratisbytter etter behov. |
| R18–R19 | – | FH1 og BB1 utløper etter R19. |

## Hvorfor

**Bench Boost nå:** BB10 er 1,5–2,3 poeng bak beste BB-dato i alle ni tester (tre planer × codex/repo/blanding), også med fritt valgt
FH og med 1–2 % nye fravær. Benken har svakere kamper i R10 enn i R11/R12. At alle 15 er friske nå, er allerede med i beregningen.
Simens argument var reelt, men ikke nok.

**Rulle mot å bytte:** Codex' førstevalg (Ødegaard, Dasilva → Iwobi, Van Hecke) er +0,12 mot rull ved 2 % nye fravær
(p10–p90 −0,89 til +1,08), og keeperbyttet Tzolakis → Verbruggen +0,03. Det er uavgjort. Rull vinner likevel fordi:
- Antall gratisbytter er ikke verifisert. Med 1 FT er rull best i Codex' egen følsomhet, og tobyttepakken ville kostet 4 poeng.
- Rull er best ved 1 FT og under 1 poeng fra beste ved 2 og 3 FT (`codex/ft_sensitivitet.csv`).
- Tre gratisbytter etter landslagspausen gir rom til å reparere skader før BB12.

Dette er et valg mellom likeverdige alternativer, ikke en beregnet fordel for å rulle.

**Claudes eget forslag falt:** Isak → Evanilson er −0,8 mot rull (Claude brukte repoets rå xP, der Isak er minuttskalert for lavt).
BB10 falt også.

## Forventning (modellresultater, ikke observasjoner)

| | Codex-modell | Repo-hybrid |
|---|---|---|
| R10, anbefalt, fast ellever uten autobytter (frosset) | 56,3 | 64,7 |
| R10, med autobytter (Codex' plan A) | 60,8 | 69,6 |
| R10–R13, anbefalt minus Codex' alternativ (frosset, fast ellever) | +1,2 | +1,6 |
| R10–R19, plan A med BB12/FH13 | ≈ 619 | ≈ 675 |

## Usikkerheter

1. **Gratisbytter:** antatt 2 i R10. Simen kan se tallet i appen. Endrer ikke anbefalingen (rull).
2. **Groß** har en smell i foten (Sussex Express 5. nov), ingen diagnose. Hvis han er helt ute, blir C (Groß, Muharemović → Van Hecke, Le Fée)
   best, men bare med ≈ 0,8 poeng (`codex/gross_sensitivitet.csv`). Faller han ut, kommer Silva inn automatisk.
3. **Haaland:** Codex' modell har ham på 5,4 mot observert 7,6 per runde; repoets 7,4. Haaland er kaptein i blandingen og i repo,
   men Mbeumo ligger marginalt over i ren Codex (5,5).
4. **FH13 og BB12** er foreløpige; poengsettene er uenige om FH13 mot FH16.
5. Pressekonferanser fredag (Brighton, City) var bare delvis tilgjengelige da beslutningen ble tatt.

## Før fristen (19:30 norsk tid)

- Ingen bytter å gjøre. Sett elleveren, kaptein Haaland og **visekaptein Gabriel** (ikke Ødegaard, som i R9), og benkrekkefølgen.
- **Groß meldt ute:** ingen endring nødvendig (Silva inn automatisk). Vil du heller ha en sikker starter: Silva inn for Groß (3-4-3 blir 4-3-3).
- **Haaland tvilsom:** kaptein Gabriel, vise Mbeumo.
- Ingen prisjusteringer før fristen.

## Uenighet mellom agentene

Claude foreslo to bytter og BB10; Codex anbefalte først keeperbytte, deretter Claudes Iwobi-variant. Begge forslagene fra Claude falt på
beregninger (Isak → Evanilson, BB10). Codex' siste førstevalg (+0,12) ble ikke fulgt fordi det er uavgjort og avhenger av et uverifisert FT-antall.
Kritikken endret: BB10 er droppet, og Isak beholdes.
