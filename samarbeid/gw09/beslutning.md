# Beslutning runde 9 (2026/27)

Tatt av Claude 2026-10-30 ca. 07:50 UTC, etter analyse og én kritikkrunde med Codex. Codex brukte opp kvoten tre ganger
(se `oppgaver.md`), så en tredje runde ble ikke kjørt. Prognosen er frosset i `prognose/prognose_R9.json` (sjekksummer i
`prognose/SHA256SUMS`) og skal ikke endres etter fristen.

## Handling nå

| | |
|---|---|
| Chip | **Wildcard 1 nå (R9)** |
| Poengtrekk | 0 |
| Bank etter wildcard | £0,4m |
| Gratisbytter til R10 | 2 (antatt bevart gjennom WC, ikke verifisert for 2026/27) |
| Senere chips (foreløpig) | Free Hit R16, Bench Boost R19 |

**Selg (salgspris):** Verbruggen 4,5, Steele 4,0, Calafiori 5,8, Konsa 4,6, N.Williams 5,0, Maguire 4,7, van Ewijk 3,9,
B.Fernandes 11,7, Le Fée 5,7, Thiago 7,8, Kusi-Asare 4,4 (sum £62,1m).

**Kjøp (pris 30. okt):** Tzolakis (HUL) 4,7, Trafford (LEE) 5,0, Gabriel (ARS) 7,9, Silva (BOU) 5,0, De Cuyper (BHA) 5,3,
Dasilva (COV) 4,0, Muharemović (LEE) 5,1, Ødegaard (ARS) 6,7, Rudoni (COV) 4,9, Barry (EVE) 5,6, Isak (LIV) 9,1 (sum £63,3m).

**Beholdes:** Haaland, Mbeumo, Tavernier, Groß.

Budsjett: £1,6m + £62,1m − £63,3m = **£0,4m**. 2/5/5/3, maks to fra samme klubb.

**Startellever (3-4-3):** Tzolakis; Gabriel, Silva, Dasilva; Mbeumo, Tavernier, Ødegaard, Rudoni; Haaland, Isak, Barry.
**Kaptein:** Haaland. **Visekaptein:** Mbeumo.
**Benk:** Trafford (GK); 1. Groß, 2. De Cuyper, 3. Muharemović.

**Avvik fra Codex' tropp:** Codex hadde Thomas (COV, forsvar). Han gikk fra 75 % til **50 %, leggskade** i API-et 30. okt
(`claude/bootstrap_30okt_kontroll.json`). Erstattet med lagkameraten **Dasilva** (samme pris, 8 starter av 8). Han er bedre enn Thomas
i begge poengsett allerede før det nye flagget (R9–R16: 25,1/26,9 mot 23,4/25,3). Ellever og benk er ellers Codex'.

## Rullerende plan R9–R16 (alt etter R9 er foreløpig)

| Runde | Frist (UTC) | Plan |
|---|---|---|
| R9 | 31. okt 11:00 | **Wildcard.** |
| R10 | 6. nov 18:30 | *Foreløpig:* gratisbytter bare ved fravær; ellers rull (2 → 3 FT). |
| R11 | 21. nov 11:00 | *Foreløpig:* etter landslagspausen: reparer skader med opptjente FT. |
| R12–R15 | – | *Foreløpig:* gratisbytter etter behov (Codex' bane har nesten ingen). |
| R16 | – | *Foreløpig:* **Free Hit**. Vurderes mot en eventuell blank runde i jula. |
| R17–R19 | – | *Foreløpig:* **Bench Boost i R19.** WC1, FH1 og BB1 utløper etter R19. |

## Hvorfor

**Wildcard nå mot senere:** Codex beregnet med automatiske innbytter, lik chipkalender (FH16/BB19) og samme byttepolitikk i alle baner.
Skadesimuleringen brukte 200 parede verdener og nye fravær på 1–3 % per spiller per runde.
WC9 leder i alle tester (R9–R19, codex/repo_hybrid):

| WC9 minus | Uten nye skader | 1–3 % nye skader | Opprykkslag slipper inn 20 % mer |
|---|---|---|---|
| WC10 | +5,2 / +1,2 | +5,3–5,9 / +1,9–3,1 | – |
| WC11 (beste tobytte først) | +8,6 / +2,5 | +9,1–9,8 / +3,8–5,5 | +7,2 / +0,9 |
| Rulle nå, WC11 (Claudes forslag) | +12,5 / +7,5 | +12,5–13,4 / +8,4–10,1 | – |

WC9 hadde høyest forventning i 88–100 % av skadeverdenene.

**Claudes argument falt igjen:** Jeg ville vente til R11 for å få mer skadeinformasjon etter landslagspausen. Simuleringen viser at
nye skader *øker* fordelen med WC nå: tidlig WC gir opptjente gratisbytter og en spillende benk som reparerer. Det samme skjedde i gw08.
Forrige uke valgte jeg å holde på skjønn ved en margin på 2–7 poeng. Denne uka er marginen mot WC11 større og stabil på tvers av
skaderater. De spillerne vi ville vente for å få avklart (Calafiori, N.Williams, Fernandes), selges uansett.
Det som gjenstår av umodellert informasjonsverdi (rolleendringer, retur for Saka, Semenyo, João Pedro), er ikke nok til å veie opp.

**Rulle (referansen):** koster 6–8 forventede poeng i R9 alene (51,8/59,9 mot 59,7/66,1 med autobytter) og 7,5–12,5 gjennom R19.

**To bytter nå og WC i R11 (C: Calafiori + Thiago → Gabriel + Barry):** er det beste uten wildcard, men 8,6 / 2,5 bak WC9 (R9–R19).

## Forventning (modellresultater, ikke observasjoner)

| | Codex-modell | Repo-hybrid |
|---|---|---|
| R9, anbefalt, med autobytter (Codex, med Thomas) | 59,7 | 66,1 |
| R9, referanse uten bytter, med autobytter | 51,8 | 59,9 |
| R9, frosset prognose, fast ellever uten autobytter (anbefalt / referanse) | 56,0 / 48,0 | 62,8 / 55,4 |
| R9–R12, frosset, anbefalt minus referanse | +17,9 | +7,7 |
| R9–R19, hele planen (WC9, FH16, BB19) | ≈ 685 | ≈ 734 |

## Usikkerheter

1. **Fem spillere fra opprykkslagene** (Tzolakis HUL; Trafford og Muharemović LEE; Dasilva og Rudoni COV). Hvis forsvarene deres er 20 %
   dårligere enn antatt, krymper fordelen mot WC11 til +7 (codex) og +1 (repo).
2. **Fernandes selges** (£11,7m) for Ødegaard og Isak. Repoets modell vurderer Fernandes høyere enn Codex' modell.
   Groß-testen viste også at poengsettene er uenige om disponering av midtbanebudsjettet (−8,5 / +4,4).
3. **Modellene er uenige om nivået** (≈ 6–7 poeng per runde) og om WC10 mot WC9 (+5 mot +1–3). Retningen er den samme.
4. **Søket er avgrenset** (de beste og billigste kandidatene per posisjon). Ingen garanti for at troppen er globalt optimal.
5. **Gratisbytter gjennom WC/FH** er ikke verifisert i API-et for 2026/27.
6. **Pressekonferansene før R9** var ikke holdt da beslutningen ble tatt.

## Før fristen

- **Gjør wildcarden fredag kveld, etter pressekonferansene og før prisjusteringen 31. okt 00:00 UTC (01:00 norsk tid).**
  Calafiori har falt til £5,9m; ett fall til gir salgspris £5,7m. Banken på £0,4m dekker inntil fire prisendringer på £0,1m.
- Sjekk på pressekonferansene: Isak (LIV), Gabriel og Ødegaard (ARS), Dasilva og Rudoni (COV), Haaland.
- **Dasilva flagget:** ta **Egan (HUL, £4,1m)** i stedet; bank £0,3m.
- **Isak eller Ødegaard ute:** ikke kjøp dem; spør igjen, eller behold Fernandes (£11,7m) i stedet for Ødegaard + Isak
  og kjøp en spiss til ≤ £4,4m + bank. Det må regnes på før wildcarden aktiveres.
- **Haaland tvilsom:** kaptein Mbeumo, visekaptein Tavernier.

## Uenighet mellom agentene

Codex anbefalte WC9 i begge runder. Claude foreslo å rulle og ta WC i R11, men godtar WC9 etter skadesimuleringen.
Claude byttet ut én spiller (Thomas → Dasilva) på grunn av nytt skadeflagg som Codex ikke kunne se.
Codex' innvending mot Claudes grovregning holdt: Claude la autobytteverdi bare til A, ikke til WC-troppen.
