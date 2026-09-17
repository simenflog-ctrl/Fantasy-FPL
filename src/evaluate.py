"""
Evalueringsrigg — måler om en endring i modellen faktisk gir poeng.

HVORFOR DENNE FINNES

Sesongsimuleringen er deterministisk, men den er én sti. En liten endring gir et
litt annet valg i runde 4, og et helt annet lag i runde 20. Målt direkte er
standardavviket 33 poeng ved en forstyrrelse på bare ±0,2 % i xP — altså kan én
kjøring ikke skille noe under ~65 poeng fra tilfeldighet.

Flere reelle forbedringer er mindre enn det. Uten denne riggen er de umulige å
oppdage, og tilfeldige utslag ser ut som gjennombrudd.

TO GREP SOM GIR PRESISJON

1. PARVIS SAMMENLIGNING. Begge konfigurasjonene kjøres på samme sesong med samme
   forstyrrelsesfrø. Da deler de mye av den samme tilfeldigheten, og differansen
   har langt lavere varians enn hver enkelt total. Dette er felles tilfeldige
   tall, standardteknikken mot nettopp dette problemet.

2. FLERE SESONGER. To sesonger i stedet for én dobler datagrunnlaget og verner
   mot at et funn bare gjelder én bestemt sesong.

BRUK

    python src/evaluate.py <navn-på-test>

Konfigurasjonene defineres i CONFIGS under. Resultatene skrives til
data/derived/eval/<navn>.json, slik at kjøringen kan deles opp over flere
økter — hver kjøring tar et par minutter, og en full test er tolv av dem.
"""

from __future__ import annotations

import fcntl
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest as B
import season_sim as S

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "eval"

BASE = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data"
SEASONS = {
    "2025-26": (f"{BASE}/2025-26", f"{BASE}/2024-25/gws/merged_gw.csv"),
    "2024-25": (f"{BASE}/2024-25", f"{BASE}/2023-24/gws/merged_gw.csv"),
}
SEEDS = (11, 12, 13)

# Forstyrrelsen skal være for liten til å endre hvem som egentlig er best, men
# stor nok til at stien kan skille lag. 0.2 % oppfyller begge.
NOISE = 0.002


def _noisy(orig, seed):
    rng = np.random.default_rng(seed)

    def f(*a, **k):
        out = orig(*a, **k)
        if not out.empty:
            out = out.copy()
            out["xp"] = out.xp * (1 + rng.normal(0, NOISE, len(out)))
        return out

    return f


def run_one(season: str, seed: int, apply_config) -> int:
    """Én sesong, ett frø, én konfigurasjon. Returnerer sesongtotalen."""
    hist, prior = SEASONS[season]
    B.HIST, S.HIST, S.PRIOR_SEASON = hist, hist, prior

    saved = apply_config()
    orig_predict = B.predict
    B.predict = _noisy(orig_predict, seed)
    S.predict = B.predict
    try:
        return int(S.run(use_chips=False)["total"])
    finally:
        B.predict = orig_predict
        S.predict = orig_predict
        if callable(saved):
            saved()


def record(name: str, season: str, seed: int, config: str, total: int) -> None:
    """
    Legger til ett resultat. Låser filen, fordi en test gjerne kjøres som flere
    parallelle prosesser — uten lås leser to av dem samme fil samtidig og den
    ene skriver over den andres resultat, og da forsvinner en kjøring uten spor.
    """
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.json"
    lock = OUT / f"{name}.lock"
    with open(lock, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        data = json.loads(path.read_text()) if path.exists() else []
        data = [r for r in data
                if not (r["season"] == season and r["seed"] == seed and r["config"] == config)]
        data.append({"season": season, "seed": seed, "config": config, "total": total})
        path.write_text(json.dumps(data, indent=1))


def report(name: str) -> None:
    """
    Parvis oppsummering. Differansen tas innenfor hvert (sesong, frø)-par, ikke
    mellom gjennomsnitt — det er dét som gir presisjonen.
    """
    path = OUT / f"{name}.json"
    if not path.exists():
        print(f"ingen resultater for {name}")
        return
    rows = json.loads(path.read_text())
    configs = sorted({r["config"] for r in rows})
    if len(configs) != 2:
        for c in configs:
            v = [r["total"] for r in rows if r["config"] == c]
            print(f"  {c:24s} n={len(v)} snitt {np.mean(v):.1f}")
        return

    a, b = configs
    idx = {(r["season"], r["seed"]): {} for r in rows}
    for r in rows:
        idx[(r["season"], r["seed"])][r["config"]] = r["total"]
    pairs = [(k, v[a], v[b]) for k, v in idx.items() if a in v and b in v]
    if not pairs:
        print("ingen komplette par ennå")
        return

    diffs = np.array([vb - va for _, va, vb in pairs], float)
    print(f"\n  {a} → {b}, {len(pairs)} par")
    for (season, seed), va, vb in sorted(pairs):
        print(f"    {season} frø {seed}: {va} → {vb}  ({vb-va:+d})")
    se = diffs.std(ddof=1) / np.sqrt(len(diffs)) if len(diffs) > 1 else float("inf")
    print(f"\n  snittdifferanse {diffs.mean():+.1f} | standardfeil {se:.1f} "
          f"| {abs(diffs.mean())/se if se else 0:.1f} se")
    print("  → " + ("REELL" if len(diffs) > 1 and abs(diffs.mean()) > 2 * se
                    else "ikke etablert"))

    # Ulike frø gir ikke alltid ulike stier. Forstyrrelsen er med vilje liten,
    # og byttereglene tåler den ofte — da havner flere frø på nøyaktig samme
    # lag hele sesongen. To slike par er ikke to observasjoner, det er én målt
    # to ganger, og standardfeilen over blir da for pen. Derfor telles det.
    for season in sorted({s for s, _ in idx}):
        base = [va for (s, _), va, _ in pairs if s == season]
        if len(base) > 1 and len(set(base)) < len(base):
            print(f"  ADVARSEL: {season} har {len(base)} par, men bare "
                  f"{len(set(base))} ulike grunnlinjer — de like er samme sti, "
                  "og standardfeilen over er derfor for optimistisk.")


if __name__ == "__main__":
    report(sys.argv[1] if len(sys.argv) > 1 else "test")
