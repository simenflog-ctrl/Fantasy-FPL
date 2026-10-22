# Status modellforbedring (22. okt 2026, kveld)

Arbeidet ligger på grenen `modellforbedring`. `main` er urørt, og GitHub-jobben (man/tor/lør) bruker fortsatt den gamle modellen.

## Ferdig og committet

| Commit | Hva | Skrevet av | Kontrollert av |
|---|---|---|---|
| e1e1fb3 | Optimizer: salgspris, faktiske FT, chipregel 2024/25, horisont | Claude | Codex (godkjent) |
| a82600a | Optimizer: chipvinduer per halvdel | Claude | **Ikke kontrollert ennå** |
| 9b87834 | P0: felles målemotor, paritetstest, keepermål 10 | Codex | Claude |
| 7502dcd | P2: innhoppsfeil i minutes, bak flagg (av) | Claude | Codex: **UAVKLART** (−0,20 % MSE, 5,7 SE; krav 0,5 %) |
| 87a16db | P1: fast bonus-tau, bak flagg (av) | Claude | Codex: **UAVKLART** (tau 7 låst; bonus-MSE −3,5 %, total −0,21 %, 2,6 SE) |

## P1/P2-målingen (ferdig 22. okt kveld)

Se `codex/p1p2-maling.md`. Begge kandidatene forbedrer MSE i alle tre sesonger, men ingen når de forhåndsregistrerte kravene.
Flaggene står av (`SUB_GIVEN_NO_START = False`, `BONUS_TAU_FIXED = None`). Kravene endres ikke i ettertid.
Bonusfeilen for toppspillere (Haaland/Fernandes) er fortsatt reell og målt; neste forsøk bør angripe den mer direkte (B2: krymping
mot egen historisk bonusrate, eller en bonusmodell per hendelse), med ny forhåndsregistrering.

## Gjenstår

1. Vurder ny bonuskandidat (B2 eller hendelsesmodell) og om P1+P2 sammen bør testes, med ny forhåndsregistrering.
2. Codex kontrollerer a82600a (chipvinduer).
3. Senere: `season_sim` bruker framtidig metadata (Codex' funn), D1–D3 i `codex/gjennomgang.md`.
4. Merge til `main` først når målingene er godkjent av den som ikke skrev endringen. Deretter push.
