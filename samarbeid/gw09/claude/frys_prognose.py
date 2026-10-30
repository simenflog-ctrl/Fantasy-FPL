"""Fryser prognosen for R9 før fristen: anbefalt plan (wildcard nå) og referansealternativ uten bytter.

Bruker Codex' poengsett fra runde 2 (`codex/spillerpoeng_r2.csv`, kolonnene `codex` og `repo_hybrid`).
Elleveren og kapteinen er fastlåst slik de anbefales; ingen automatiske innbytter er regnet med
(Codex' lagforventning med autobytter står i `beslutning.md`).
Anbefalt tropp avviker fra Codex' på ett punkt: Dasilva (COV) i stedet for Thomas (COV), som ble 50 % 30. okt
(`claude/bootstrap_30okt_kontroll.json`).
Skriver `prognose/prognose_R9.json` og `prognose/SHA256SUMS`. Kjør fra repoets rot.
Prognosen skal ikke endres etter fristen 2026-10-31 11:00 UTC.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path("samarbeid/gw09")
SP = pd.read_csv(ROOT / "codex/spillerpoeng_r2.csv")
BOOT = json.load(open(ROOT / "data/bootstrap.json"))
NAME = {e["id"]: e["web_name"] for e in BOOT["elements"]}

PLANS = {
    "anbefalt": {
        "beskrivelse": "Wildcard i R9 (Codex' tropp E, med Dasilva for Thomas); BB19, FH16",
        "bytter_inn": [4, 15, 115, 176, 183, 249, 334, 379, 385, 566, 572],
        "bytter_ut": [8, 31, 106, 109, 111, 175, 272, 418, 426, 469, 542],
        "trekk": 0, "bank": 0.4, "ft_til_R10": 2, "chip": "wildcard",
        "elleve": [572, 4, 566, 176, 15, 68, 183, 427, 249, 379, 411],
        "benk": [385, 124, 115, 334],
        "kaptein": 411, "visekaptein": 427,
    },
    "referanse_ingen_bytter": {
        "beskrivelse": "Ingen bytter, rull til 3 gratisbytter (Claudes forslag), WC i R11",
        "bytter_inn": [], "bytter_ut": [], "trekk": 0, "bank": 1.6, "ft_til_R10": 3, "chip": None,
        "elleve": [109, 31, 8, 469, 426, 427, 68, 542, 124, 411, 106],
        "benk": [111, 175, 418, 272],
        "kaptein": 411, "visekaptein": 68,
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
    s = SP[SP.gw == 9].set_index("id")[col]
    return {NAME[e]: round(float(s.get(e, 0.0)), 2) for e in xi + bench}


out = {
    "frosset_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "frist_utc": "2026-10-31T11:00:00Z",
    "data_hentet_utc": open(ROOT / "data/fetched_at.txt").read().strip(),
    "lag_id": 7089878,
    "merknad": "Faste ellever og kaptein. Ingen autobytter. R10-R12 forutsetter samme ellever (nedre grense for begge planer, som kan gjøre bytter senere). "
               "To poengsett: 'codex' (Codex runde 2) og 'repo_hybrid' (repoets xP R9-14, Codex R15-16). Faktisk resultat sammenlignes med begge.",
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
        r = lineup_points(p["elleve"], p["kaptein"], [9, 10, 11, 12], col)
        entry[f"forventet_{col}"] = {"R9": r[9], "R9_R12": round(sum(r.values()) - p["trekk"], 1)}
        entry[f"spiller_xp_R9_{col}"] = player_rows(p["elleve"], p["benk"], col)
    out["planer"][key] = entry

a, b = out["planer"]["anbefalt"], out["planer"]["referanse_ingen_bytter"]
out["forventet_gevinst_anbefalt_minus_referanse"] = {
    col: {k: round(a[f"forventet_{col}"][k] - b[f"forventet_{col}"][k], 1) for k in ("R9", "R9_R12")}
    for col in ("codex", "repo_hybrid")
}

d = ROOT / "prognose"
d.mkdir(exist_ok=True)
path = d / "prognose_R9.json"
if path.exists():
    raise SystemExit(f"{path} finnes allerede. Prognosen er frosset og skal ikke overskrives.")
path.write_text(json.dumps(out, ensure_ascii=False, indent=1))
files = [path, ROOT / "codex/spillerpoeng_r2.csv", ROOT / "data/bootstrap.json", ROOT / "data/fixtures.json"]
(d / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(ROOT)}\n" for f in files))
print(json.dumps(out["forventet_gevinst_anbefalt_minus_referanse"], indent=1))
print({k: (v["forventet_codex"], v["forventet_repo_hybrid"]) for k, v in out["planer"].items()})
