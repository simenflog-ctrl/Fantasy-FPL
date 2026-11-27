# Måling av poengsettene `codex` og `repo_hybrid`

Kjørt 16. november 2026 med `samarbeid/motor/historikk.py`, etter at kravene var låst og committet i `plan-v2.md` del C
(commit a7cf667). Rådata: `motor/maling_poengsett.json`. Prognosene per spiller-runde gjenskapes med skriptet (6,5 min).

**Konklusjon: UAVKLART etter den låste regelen. Vekten blir stående på 0,50.**
Målingen støtter likevel dagens praksis: blandingen er bedre enn hvert sett alene.

## Oppsett

Sesongene 2023/24, 2024/25 og 2025/26, runde 8–38, én runde fram. 70 899 spiller-runder (dobbeltrunder summert), alle med
prognose i begge sett, også de som ikke spilte. «±» er én standardfeil med fire-runders blokker innen sesong (24 blokker).
Topp 10 = snittpoeng for de ti høyest rangerte spillerne hver runde (ikke en lovlig tropp).

Ikke målt: API-flagg og Claudes minuttoverstyringer (alle regnes som tilgjengelige). Tallene gjelder ratemodellene og
grunnminuttene, ikke hele ukekjeden. Repo-modellen er tidligere justert på disse sesongene; `codex` er ikke det.

## Resultat

| Kandidat | MSE | Topp 10 | Topp 20 | Skjevhet |
|---|---:|---:|---:|---:|
| `repo` (egne minutter) | 4,120 | 5,43 | 4,81 | +0,01 |
| `repo_hybrid` (w = 0) | 4,132 | 5,48 | 4,89 | −0,01 |
| w = 0,25 | 4,118 | 5,49 | 4,89 | −0,02 |
| **w = 0,50 (i bruk)** | **4,110** | **5,53** | 4,86 | −0,03 |
| w = 0,75 | 4,110 | 5,35 | 4,87 | −0,04 |
| `codex` (w = 1) | 4,116 | 5,32 | 4,84 | −0,05 |

Skjevhet = prognose minus faktisk. Lavere MSE er bedre, høyere topp 10 er bedre.

### Den låste regelen

1. Lavest MSE på utviklingsårene 2023/24 + 2024/25: **w = 0,75** (4,2496 mot 4,2509 for 0,50).
2. Krav for å bytte fra 0,50 til 0,75:

| Krav | Målt | Oppfylt |
|---|---|---|
| Minst 0,5 % lavere MSE samlet | 0,02 % | nei |
| Minst 3 blokk-SE | 0,3 SE | nei |
| Samme fortegn i alle tre sesonger | bedre bare i 2024/25 | nei |
| Topp 10 ikke dårligere enn 2 SE | −0,17 ± 0,04 (3,9 SE dårligere) | nei |

Ingen av kravene holder. Vekten blir 0,50, og det kjøres ingen ny runde med andre vekter på disse sesongene.

### Parede sammenligninger

| Sammenligning | Δ MSE | Per sesong (23/24, 24/25, 25/26) | Δ topp 10 |
|---|---:|---|---:|
| `repo_hybrid` alene mot 0,50 | +0,52 % (4,1 SE) | dårligere i alle tre | −0,05 ± 0,06 |
| `codex` alene mot 0,50 | +0,13 % (1,2 SE) | dårligere i alle tre | −0,21 ± 0,05 |
| `codex` mot `repo_hybrid` | −0,39 % (1,7 SE) | `codex` bedre i alle tre | −0,17 ± 0,08 |
| `repo_hybrid` mot `repo` | +0,28 % (1,5 SE) | blandet | +0,06 ± 0,07 |

Lest sammen:

- **Blandingen 50/50 er bedre enn hvert sett alene**, i alle tre sesonger. Mot `repo_hybrid` alene er forskjellen 0,5 % og 4 SE.
  Å vise begge sett og rangere på blandingen er altså riktig praksis, ikke bare en nødløsning.
- `codex` treffer bredden litt bedre (MSE), `repo_hybrid` rangerer toppspillerne bedre (topp 10). `codex` alene taper
  0,2 poeng per spiller i topp 10. De to settene har ulike styrker, og det er derfor blandingen vinner.
- Minuttskaleringen i `repo_hybrid` er verken vist bedre eller dårligere enn repoets egne minutter.

### Skjevhet for dyre spillere (diagnose, ikke grunnlag for justering)

| Gruppe | N | Faktisk | `repo_hybrid` | `codex` | Blanding 0,50 |
|---|---:|---:|---:|---:|---:|
| Spiss ≥ 10,0 | 148 | 3,24 | +1,23 ± 0,37 | +0,41 ± 0,35 | +0,82 ± 0,35 |
| Midtbane ≥ 10,0 | 243 | 4,72 | +0,46 ± 0,36 | −0,32 ± 0,35 | +0,07 ± 0,35 |
| Spiss 7,5–9,9 | 502 | 3,64 | +0,04 ± 0,18 | −0,13 ± 0,17 | −0,04 ± 0,17 |
| Midtbane 7,5–9,9 | 934 | 3,71 | −0,10 ± 0,14 | −0,44 ± 0,14 | −0,27 ± 0,14 |

- **Spisser over 10,0**: `repo_hybrid` overvurderer med 1,2 poeng per runde, positivt i alle tre sesonger (+0,6, +2,9, +1,0).
  Det bekrefter funnet i `codex/gjennomgang.md`. `codex` ligger nærmere (+0,4, blandet fortegn). Blandingen overvurderer
  med 0,8 (positivt i alle tre). Gruppen er liten og består av få spillere, mest Haaland.
- **Midtbane 7,5–9,9**: `codex` undervurderer med 0,44 poeng (3 SE, negativt i alle tre sesonger).
- For Haaland i R10 (5,4 `codex` mot 7,4 `repo_hybrid`) betyr dette at sannheten historisk har ligget nærmere `codex` for
  denne spillertypen. Det er en opplysning til kapteinsvalget, og kan nevnes som uttalt antakelse i `beslutning.md`.
  En fast nivåjustering i motoren krever egen forhåndsregistrering (plan-v2 del D).

## Hva dette betyr for ukeanalysen

1. Behold `vekt_codex = 0,5`. Ranger på blandingen, vis begge sett.
2. Ikke la ett poengsett alene avgjøre noe. Særlig ikke `codex` alene for toppspillere eller `repo_hybrid` alene for premiumspisser.
3. Den løpende loggen (`samarbeid/kalibrering/logg.csv`) er eneste måling av hele ukekjeden. Regelen for den står i
   plan-v2 del C («Nest beste») og gjelder fra loggen har 8 runder.
