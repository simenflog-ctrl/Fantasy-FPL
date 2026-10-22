# Status modellforbedring (22. okt 2026, kveld)

Arbeidet ligger på grenen `modellforbedring`. `main` er urørt, og GitHub-jobben (man/tor/lør) bruker fortsatt den gamle modellen.

## Ferdig og committet

| Commit | Hva | Skrevet av | Kontrollert av |
|---|---|---|---|
| e1e1fb3 | Optimizer: salgspris, faktiske FT, chipregel 2024/25, horisont | Claude | Codex (godkjent) |
| a82600a | Optimizer: chipvinduer per halvdel | Claude | **Ikke kontrollert ennå** |
| 9b87834 | P0: felles målemotor, paritetstest, keepermål 10 | Codex | Claude |
| 7502dcd | P2: innhoppsfeil i minutes, bak flagg (av) | Claude | Måles av Codex |
| 87a16db | P1: fast bonus-tau, bak flagg (av) | Claude | Måles av Codex |

## Pågikk da økten ble avsluttet

Codex målte P1 og P2 (`codex/oppdrag-3.md`). Hvis `codex/p1p2-maling.md` finnes, er målingen ferdig: les den, gjennomgå eventuelle
endringer i `src/eval_engine.py` og `src/evaluate_pred.py`, kjør `python3 -m pytest -q tests/` og commit. Hvis ikke: send oppdrag-3 på nytt.

## Gjenstår

1. P1/P2-måling → slå på flaggene som består, med verdien Codex anbefaler.
2. Codex kontrollerer a82600a (chipvinduer).
3. Senere: `season_sim` bruker framtidig metadata (Codex' funn), D1–D3 i `codex/gjennomgang.md`.
4. Merge til `main` først når målingene er godkjent av den som ikke skrev endringen. Deretter push.
