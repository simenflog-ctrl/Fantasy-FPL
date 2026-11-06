"""Fryser prognosen for R10 før fristen: anbefalt plan (rull, ingen bytter) og Codex' knappe førstevalg (Ødegaard, Dasilva → Iwobi, Van Hecke).

Bruker Codex' poengsett (`codex/spillerpoeng.csv`; runde 2 endret ikke spillerpoengene, kolonnene `codex` og `repo_hybrid`).
Elleveren og kapteinen er fastlåst slik de anbefales; ingen automatiske innbytter er regnet med
(Codex' lagforventning med autobytter står i `beslutning.md`).
Anbefalingen avviker fra Codex' knappe førstevalg (+0,12 mot rull ved 2 % nye fravær), som derfor fryses som sammenligning.
Skriver `prognose/prognose_R10.json` og `prognose/SHA256SUMS`. Kjør fra repoets rot.
Prognosen skal ikke endres etter fristen 2026-11-06 18:30 UTC.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path("samarbeid/gw10")
SP = pd.read_csv(ROOT / "codex/spillerpoeng.csv")
BOOT = json.load(open(ROOT / "data/bootstrap.json"))
NAME = {e["id"]: e["web_name"] for e in BOOT["elements"]}

PLANS = {
    "anbefalt": {
        "beskrivelse": "Ingen bytter, rull gratisbyttene; ikke Bench Boost (foreløpig BB12, FH13)",
        "bytter_inn": [], "bytter_ut": [], "trekk": 0, "bank": 0.4, "chip": None,
        "elleve": [385, 4, 115, 334, 15, 68, 124, 427, 249, 379, 411],
        "benk": [572, 566, 183, 176],
        "kaptein": 411, "visekaptein": 4,
    },
    "alternativ_codex": {
        "beskrivelse": "Codex' knappe førstevalg: Ødegaard, Dasilva -> Iwobi, Van Hecke (2 gratisbytter)",
        "bytter_inn": [261, 112], "bytter_ut": [15, 176], "trekk": 0, "bank": 0.7, "chip": None,
        "elleve": [385, 4, 115, 334, 68, 124, 261, 427, 249, 379, 411],
        "benk": [572, 566, 112, 183],
        "kaptein": 411, "visekaptein": 4,
    },
}


def lineup_points(xi, captain, gws, col):
    s = SP[SP.gw.isin(gws)].pivot_table(index="id", columns="gw", values=col, aggfunc="sum").fillna(0.0)
    per_gw = {}
    for g in gws:
        pts = sum(s.at[e, g] if e in s.index else 0.0 for e in xi)
        pts += s.at[captain, g] if captain in s.index else 0.0
        per_gw[g] = round(pts, 1)
    return per_gw


def player_rows(xi, bench, col):
    s = SP[SP.gw == 10].set_index("id")[col]
    return {NAME[e]: round(float(s.get(e, 0.0)), 2) for e in xi + bench}


out = {
    "frosset_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "frist_utc": "2026-11-06T18:30:00Z",
    "data_hentet_utc": open(ROOT / "data/fetched_at.txt").read().strip(),
    "lag_id": 7089878,
    "merknad": "Faste ellever og kaptein. Ingen autobytter. R11-R13 forutsetter samme ellever. "
               "To poengsett: 'codex' (Codex runde 2) og 'repo_hybrid' (repoets xP R10-15, Codex R16-17). Faktisk resultat sammenlignes med begge.",
    "planer": {},
}
for key, p in PLANS.items():
    entry = dict(p)
    entry["bytter_inn"] = [NAME[e] for e in p["bytter_inn"]]
    entry["bytter_ut"] = [NAME[e] for e in p["bytter_ut"]]
    entry["elleve"] = [NAME[e] for e in p["elleve"]]
    entry["benk"] = [NAME[e] for e in p["benk"]]
    entry["kaptein"] = NAME[p["kaptein"]]
    entry["visekaptein"] = NAME[p["visekaptein"]]
    for col in ("codex", "repo_hybrid"):
        r = lineup_points(p["elleve"], p["kaptein"], [10, 11, 12, 13], col)
        entry[f"forventet_{col}"] = {"R10": r[10], "R10_R13": round(sum(r.values()) - p["trekk"], 1)}
        entry[f"spiller_xp_R10_{col}"] = player_rows(p["elleve"], p["benk"], col)
    out["planer"][key] = entry

a, b = out["planer"]["anbefalt"], out["planer"]["alternativ_codex"]
out["forventet_gevinst_anbefalt_minus_alternativ_codex"] = {
    col: {k: round(a[f"forventet_{col}"][k] - b[f"forventet_{col}"][k], 1) for k in ("R10", "R10_R13")}
    for col in ("codex", "repo_hybrid")
}

d = ROOT / "prognose"
d.mkdir(exist_ok=True)
path = d / "prognose_R10.json"
if path.exists():
    raise SystemExit(f"{path} finnes allerede. Prognosen er frosset og skal ikke overskrives.")
path.write_text(json.dumps(out, ensure_ascii=False, indent=1))
files = [path, ROOT / "codex/spillerpoeng.csv", ROOT / "data/bootstrap.json", ROOT / "data/fixtures.json"]
(d / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(ROOT)}\n" for f in files))
print(json.dumps(out["forventet_gevinst_anbefalt_minus_alternativ_codex"], indent=1))
print({k: (v["forventet_codex"], v["forventet_repo_hybrid"]) for k, v in out["planer"].items()})
