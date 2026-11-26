"""Fryser prognosen for R12 før fristen: anbefalt plan, rull og Claudes forslag P (se `beslutning.md`).

Bruker Codex' poengsett (`codex/spillerpoeng.csv`, kolonnene `codex` og `repo_hybrid`, R12–R19).
Elleveren og kapteinen er fastlåst; ingen automatiske innbytter er regnet med. Rull og P får elleveren som maksimerer
blandingen (50/50) i R12 innen lovlige formasjoner; anbefalt plan bruker Codex' ellever (kontrolleres mot samme regel).
R12–R14 regnes med samme ellever (Free Hit er planlagt i R15 og holdes utenfor).
Skriver `prognose/prognose_R12.json` og `prognose/SHA256SUMS`. Kjør fra repoets rot.
Prognosen skal ikke endres etter fristen 2026-11-27 18:30 UTC.
"""
import hashlib
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path("samarbeid/gw12")
SP = pd.read_csv(ROOT / "codex/spillerpoeng.csv")
BOOT = json.load(open(ROOT / "data/bootstrap.json"))
NAME = {e["id"]: e["web_name"] for e in BOOT["elements"]}
POS = {e["id"]: e["element_type"] for e in BOOT["elements"]}
RUNDER = [12, 13, 14]
TROPP = [385, 4, 115, 112, 427, 15, 124, 68, 411, 249, 379, 572, 566, 183, 176]
R12 = SP[SP.gw == 12].set_index("id")
BLEND = (0.5 * R12["codex"] + 0.5 * R12["repo_hybrid"]).to_dict()


def best_xi(squad):
    best = None
    gk = sorted([e for e in squad if POS[e] == 1], key=lambda e: -BLEND.get(e, 0))
    out = [e for e in squad if POS[e] != 1]
    for combo in itertools.combinations(out, 10):
        n = {p: sum(POS[e] == p for e in combo) for p in (2, 3, 4)}
        if n[2] < 3 or n[3] < 2 or n[4] < 1:
            continue
        v = sum(BLEND.get(e, 0) for e in combo)
        if best is None or v > best[0]:
            best = (v, [gk[0]] + list(combo))
    xi = best[1]
    bench = [gk[1]] + sorted([e for e in out if e not in xi], key=lambda e: -BLEND.get(e, 0))
    return xi, bench


def squad_after(inn, ut):
    s = [e for e in TROPP if e not in ut] + inn
    assert len(s) == 15 and len(set(s)) == 15
    return s


def plan(beskr, inn, ut, bank, kaptein, vise, xi=None, benk=None):
    s = squad_after(inn, ut)
    bx, bb = best_xi(s)
    if xi is None:
        xi, benk = bx, bb
    return dict(beskrivelse=beskr, bytter_inn=inn, bytter_ut=ut, trekk=0, bank=bank, chip=None,
                elleve=xi, benk=benk, kaptein=kaptein, visekaptein=vise,
                elleve_blanding_R12_maks=round(sum(BLEND.get(e, 0) for e in bx), 2))


PLANS = {
    "anbefalt": plan("G_keep: Dasilva, Silva → Bogle, Justin (2 av 3 gratisbytter); kaptein De Cuyper, vise Haaland",
                     [330, 332], [176, 566], 0.1, 115, 411,
                     xi=[385, 4, 115, 330, 332, 68, 124, 427, 249, 379, 411], benk=[572, 15, 112, 183]),
    "rull": plan("Ingen bytter (plan A)", [], [], 0.4, 115, 411),
    "claude_P": plan("Claudes forslag P: Ødegaard → Le Fée, Dasilva → Konsa", [542, 31], [15, 176], 0.5, 115, 411),
}
SAMMENLIGN = [("anbefalt", "rull"), ("anbefalt", "claude_P")]


def lineup_points(xi, captain, gws, col):
    s = SP[SP.gw.isin(gws)].pivot_table(index="id", columns="gw", values=col, aggfunc="sum").fillna(0.0)
    return {g: round(sum(s.at[e, g] if e in s.index else 0.0 for e in xi) + (s.at[captain, g] if captain in s.index else 0.0), 2)
            for g in gws}


assert {"codex", "repo_hybrid"} <= set(SP.columns) and set(RUNDER) <= set(SP.gw)
for p in PLANS.values():
    assert len(p["elleve"]) == 11 and len(p["benk"]) == 4 and len(set(p["elleve"] + p["benk"])) == 15
    assert p["kaptein"] in p["elleve"] and p["visekaptein"] in p["elleve"]

out = {
    "frosset_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "frist_utc": "2026-11-27T18:30:00Z",
    "data_hentet_utc": open(ROOT / "data/fetched_at.txt").read().strip(),
    "lag_id": 7089878,
    "merknad": "Faste ellever og kaptein. Ingen autobytter. R13-R14 forutsetter samme ellever. Ingen chip i R12; FH planlagt R15. "
               "To poengsett fra Codex: 'codex' og 'repo_hybrid' (repoets xP R12-16 skalert med minutter, Codex R17-19).",
    "planer": {},
}
for key, p in PLANS.items():
    e = dict(p)
    for f in ("bytter_inn", "bytter_ut", "elleve", "benk"):
        e[f] = [NAME[i] for i in p[f]]
    e["kaptein"], e["visekaptein"] = NAME[p["kaptein"]], NAME[p["visekaptein"]]
    for col in ("codex", "repo_hybrid"):
        r = lineup_points(p["elleve"], p["kaptein"], RUNDER, col)
        e[f"forventet_{col}"] = {"R12": r[12], "R12_R14": round(sum(r.values()) - p["trekk"], 2)}
        e[f"spiller_xp_R12_{col}"] = {NAME[i]: round(float(R12[col].get(i, 0.0)), 2) for i in p["elleve"] + p["benk"]}
    out["planer"][key] = e
for a, b in SAMMENLIGN:
    A, B = out["planer"][a], out["planer"][b]
    out[f"forventet_gevinst_{a}_minus_{b}"] = {
        col: {k: round(A[f"forventet_{col}"][k] - B[f"forventet_{col}"][k], 2) for k in ("R12", "R12_R14")}
        for col in ("codex", "repo_hybrid")}

d = ROOT / "prognose"
d.mkdir(exist_ok=True)
path = d / "prognose_R12.json"
if path.exists():
    raise SystemExit(f"{path} finnes allerede. Prognosen er frosset og skal ikke overskrives.")
path.write_text(json.dumps(out, ensure_ascii=False, indent=1))
files = [path, ROOT / "codex/spillerpoeng.csv", ROOT / "data/bootstrap.json", ROOT / "data/fixtures.json"]
(d / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(ROOT)}\n" for f in files))
print(json.dumps({k: v for k, v in out.items() if k.startswith("forventet_gevinst")}, indent=1, ensure_ascii=False))
for k, v in out["planer"].items():
    print(k, v["elleve"], v["benk"], v["forventet_codex"], v["forventet_repo_hybrid"], v["elleve_blanding_R12_maks"])
