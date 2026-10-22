# Claudes kontroll av Codex' analyse (oppgave 5, runde 1)

Skrevet 2026-10-22 etter å ha lest `codex/analyse.md`, `alternativer.csv`, `spillerpoeng.csv` og `detaljer.json`.
Kontrollregning: `claude/regn.py` brukt på Codex' tropper (skript i loggen under).

## Det jeg er enig i

- **Szoboszlai → Tavernier** er riktig bytte nå. Samme konklusjon som mitt uavhengige forslag, og positiv i begge modellene.
- Kontrollen av `plan.json` er god og viktig: wildcardlaget der koster **£0,9m mer** enn salgsverdien tillater, start-FT er feil (1 i stedet for 2), og horisonten er kortere enn den ser ut. plan.json skal ikke brukes.
- Poengreglene er kontrollert mot 105 historiske spillerkamper uten avvik. Det bekrefter DC-tersklene 10/12.
- Ingen poengtrekk nå (D3–D5 er ikke begrunnet når fremtidige gratisbytter ikke er optimert).

## Innvendinger

### 1. Toppspillerne er systematisk undervurdert (alvorlig)

| Spiller | Codex xP R8–13 | Repo xP R8–13 | Observert snitt R1–7 × 6 |
|---|---|---|---|
| Haaland | 34,2 (5,7/runde) | 50,6 | 49,7 (58 p / 7) |
| B.Fernandes | 26,4 | 43,6 | 28,3 |
| Rogers | 26,3 | 33,8 | 34,3 |

Haaland har xGI/90 0,94 og har spilt 619 av 630 minutter. Han har levert på dette nivået i flere sesonger.
Codex krymper individuelle rater med 270 minutter mot posisjonssnittet **fra bare inneværende sesong**,
og lagstyrken bygger på **faktiske mål** i sju kamper, ikke xG. Det trekker alle eliteprofiler mot middels.
Samtidig får billige, DC-tunge spillere +5 til +9 (Bogle, De Cuyper, Tzolakis, Barry, Isak). Retningen på feilen
favoriserer en wildcard som sprer pengene. Fernandes ligger trolig et sted mellom de to modellene; Haaland klart nær repoet.

### 2. Wildcardfordelen er modellavhengig

Codex' egne tropper, regnet på nytt for R8–13 (beste ellever + kaptein, ingen benk):

| Plan | Repo-xP | Codex-xP | Codex-xP, Haaland/Fernandes fra repo |
|---|---|---|---|
| B | 385,1 | 312,7 | 363,9 |
| E (WC nå, beholder Haaland + Fernandes) | 391,8 | 348,4 | 398,8 |
| E19 (WC nå, selger Fernandes) | 369,5 | 349,4 | 381,6 |
| F (WC i R9) | 373,8 | 345,2 | 379,8 |

- E19 og F (som selger Fernandes) **taper mot B** med repoets xP. Fordelen deres kommer fra innvending 1.
- E slår B i alle tre, men med **+6,7** med repo-xP mot **+35** med korrigert Codex-xP. Det er spennet beslutningen må tåle.

### 3. Sammenligningen av wildcardtidspunkt er skjev

A–D og F bruker ingen gratisbytter etter R8, selv om de samler opp til fem. Da taper hver uke uten wildcard mer
enn den ville gjort i virkeligheten. Den riktige sammenligningen er **E (WC nå)** mot **B + ett fornuftig gratisbytte per runde + WC senere**.
Uten dette er «WC nå leder med 4,2» ikke informativt.

### 4. Spillere som ikke finnes eller ikke spiller

- **Dennis (BOU, 4,0)** står i FH-tropper og i wildcardtroppene R13–R18, men har status `u`: *«Has joined MK Dons permanently»*.
- **Hughes**: begge med det navnet er ubrukelige (HUL: skadet, 0 min; CRY: 38 min). Står i E19, F og flere FH-tropper.
- Nullspillere på benken gjør Bench Boost og autobytter verdiløse og gir for lav BB-verdi.
Filtrer bort status `u`, `n` og spillere med `i` og 0 % fra kjøpsuniverset, og krev minst ca. 50 % sjanse for å starte for benkespillere.

### 5. Startellever og visekaptein for B

Codex starter Maguire og benker Thiago. Thiago har 3,69 xG på 622 min (18 poeng, kraftig underprestasjon);
repoets modell har ham 7 xP foran Maguire over R8–13. Dette er en følge av at Codex' lagstyrke bruker faktiske mål.
Visekaptein: Fernandes (sikker starter, straffetaker) fremfor Mbeumo. Liten verdi uansett.

### 6. Rollevalidering av E-troppen (Codex ba om dette)

Alle innspillerne i E har spilt nesten alt: Tavernier 574 min (synkende), De Cuyper 580, Thomas (COV) 617,
Tarkowski 630, Barry 592, Iwobi 584, Bogle 540, Calvert-Lewin 599, Tzolakis 630. Ingen skadeflagg.
**E er realistisk på roller.** E19/F er det ikke helt (Hughes, Dennis).

## Oppdrag tilbake til Codex (runde 1)

Se `codex/oppdrag-2.md`.
