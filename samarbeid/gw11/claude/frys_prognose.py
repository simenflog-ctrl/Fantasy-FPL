"""Fryser prognosen for R11 før fristen: anbefalt plan og ett sammenligningsalternativ (se `beslutning.md`).

Bruker Codex' poengsett (`codex/spillerpoeng.csv`, kolonnene `codex` og `repo_hybrid`, R11–R19).
Motorens spillerpoeng fra prøvekjøringen (`motor/spillerpoeng.csv`) fryses også, bare for å kunne sammenligne motoren med
Codex etterpå; de er ikke beslutningsgrunnlag.
Elleveren og kapteinen er fastlåst slik de anbefales; ingen automatiske innbytter er regnet med.
Skriver `prognose/prognose_R11.json` og `prognose/SHA256SUMS`. Kjør fra repoets rot.
Prognosen skal ikke endres etter fristen 2026-11-21 11:00 UTC.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path("samarbeid/gw11")
SP = pd.read_csv(ROOT / "codex/spillerpoeng.csv")
BOOT = json.load(open(ROOT / "data/bootstrap.json"))
NAME = {e["id"]: e["web_name"] for e in BOOT["elements"]}
RUNDER = [11, 12, 13, 14]

# Fylles inn etter beslutningen. Nøklene: beskrivelse, bytter_inn, bytter_ut, trekk, bank, chip, elleve, benk, kaptein, visekaptein.
# chip "BB" betyr Bench Boost i R11: da teller benken med i R11 (ikke i R12-R14).
XI_B = [572, 4, 112, 115, 15, 68, 124, 183, 427, 379, 411]  # Tzolakis; Gabriel, Van Hecke, De Cuyper; Ødegaard, Tavernier, Groß, Rudoni, Mbeumo; Isak, Haaland
PLANS = {
    "anbefalt": dict(
        beskrivelse="Muharemović → Van Hecke (1 gratisbytte); Bench Boost i R11; kaptein Haaland, vise Gabriel",
        bytter_inn=[112], bytter_ut=[334], trekk=0, bank=0.4, chip="BB",
        elleve=XI_B, benk=[385, 249, 566, 176], kaptein=411, visekaptein=4),
    "alternativ": dict(
        beskrivelse="Codex' forslag C: Dasilva, Mbeumo → Van Hecke, Le Fée (2 gratisbytter); Bench Boost i R11",
        bytter_inn=[112, 542], bytter_ut=[176, 427], trekk=0, bank=1.5, chip="BB",
        elleve=[572, 4, 112, 115, 15, 68, 124, 183, 542, 379, 411], benk=[385, 249, 566, 334], kaptein=411, visekaptein=4),
    "rull": dict(
        beskrivelse="Ingen bytter (plan A); Bench Boost i R11",
        bytter_inn=[], bytter_ut=[], trekk=0, bank=0.4, chip="BB",
        elleve=[572, 4, 115, 566, 15, 68, 124, 183, 427, 379, 411], benk=[385, 249, 334, 176], kaptein=411, visekaptein=4),
}
SAMMENLIGN = ("anbefalt", "alternativ")


def lineup_points(xi, bench, captain, chip, gws, col):
    s = SP[SP.gw.isin(gws)].pivot_table(index="id", columns="gw", values=col, aggfunc="sum").fillna(0.0)
    per_gw = {}
    for g in gws:
        lag = xi + bench if (chip == "BB" and g == RUNDER[0]) else xi
        pts = sum(s.at[e, g] if e in s.index else 0.0 for e in lag)
        pts += s.at[captain, g] if captain in s.index else 0.0
        per_gw[g] = round(pts, 1)
    return per_gw


def player_rows(xi, bench, col):
    s = SP[SP.gw == RUNDER[0]].set_index("id")[col]
    return {NAME[e]: round(float(s.get(e, 0.0)), 2) for e in xi + bench}


if not PLANS:
    raise SystemExit("PLANS er tom: fyll inn planene fra beslutning.md før frysing.")
assert {"codex", "repo_hybrid"} <= set(SP.columns) and set(RUNDER) <= set(SP.gw), "spillerpoeng.csv mangler kolonner eller runder"
for p in PLANS.values():
    assert len(p["elleve"]) == 11 and len(p["benk"]) == 4 and len(set(p["elleve"] + p["benk"])) == 15
    assert p["kaptein"] in p["elleve"] and p["visekaptein"] in p["elleve"]

out = {
    "frosset_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "frist_utc": "2026-11-21T11:00:00Z",
    "data_hentet_utc": open(ROOT / "data/fetched_at.txt").read().strip(),
    "lag_id": 7089878,
    "merknad": "Faste ellever og kaptein. Ingen autobytter. R12-R14 forutsetter samme ellever. "
               "Med chip BB teller benken med i R11. "
               "To poengsett fra Codex: 'codex' og 'repo_hybrid' (repoets xP R11-16 skalert med minutter, Codex R17-19). "
               "Faktisk resultat sammenlignes med begge.",
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
        r = lineup_points(p["elleve"], p["benk"], p["kaptein"], p.get("chip"), RUNDER, col)
        entry[f"forventet_{col}"] = {"R11": r[11], "R11_R14": round(sum(r.values()) - p["trekk"], 1)}
        entry[f"spiller_xp_R11_{col}"] = player_rows(p["elleve"], p["benk"], col)
    out["planer"][key] = entry

a, b = (out["planer"][k] for k in SAMMENLIGN)
out[f"forventet_gevinst_{SAMMENLIGN[0]}_minus_{SAMMENLIGN[1]}"] = {
    col: {k: round(a[f"forventet_{col}"][k] - b[f"forventet_{col}"][k], 1) for k in ("R11", "R11_R14")}
    for col in ("codex", "repo_hybrid")
}

d = ROOT / "prognose"
d.mkdir(exist_ok=True)
path = d / "prognose_R11.json"
if path.exists():
    raise SystemExit(f"{path} finnes allerede. Prognosen er frosset og skal ikke overskrives.")
path.write_text(json.dumps(out, ensure_ascii=False, indent=1))
files = [path, ROOT / "codex/spillerpoeng.csv", ROOT / "motor/spillerpoeng.csv",
         ROOT / "data/bootstrap.json", ROOT / "data/fixtures.json"]
(d / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(ROOT)}\n" for f in files))
print(json.dumps({k: v for k, v in out.items() if k.startswith("forventet_gevinst")}, indent=1))
print({k: (v["forventet_codex"], v["forventet_repo_hybrid"]) for k, v in out["planer"].items()})
