"""Sammenligner ukemotorens prøvekjøring (`motor/`) med Codex' egne gw11-tall (`codex/`).

Samme inndata og samme overstyringer; motoren skal gi de samme spillerpoengene som Codex' oppdaterte gw10-skript
med mindre Codex har endret noe. Skriver bare til skjermen. Kjør fra repoets rot:
    python samarbeid/gw11/claude/sammenlign_motor_codex.py
"""
from pathlib import Path

import pandas as pd

U = Path("samarbeid/gw11")
m = pd.read_csv(U / "motor/spillerpoeng.csv")
c = pd.read_csv(U / "codex/spillerpoeng.csv")
print(f"Spillerpoeng: motor {len(m)} rader ({m.id.nunique()} spillere), Codex {len(c)} rader ({c.id.nunique()} spillere)")
print("Codex-kolonner:", list(c.columns))

j = m.merge(c, on=["id", "gw"], suffixes=("_m", "_c"), how="outer", indicator=True)
print("Rader bare i én fil:", j._merge.value_counts().to_dict())
j = j[j._merge == "both"].copy()
for col in ("codex", "repo_hybrid"):
    j[f"d_{col}"] = j[f"{col}_m"] - j[f"{col}_c"]
    a = j[f"d_{col}"].abs()
    print(f"\n{col}: største avvik {a.max():.6f}, snitt {a.mean():.6f}, rader > 0,01: {(a > .01).sum()}, > 0,1: {(a > .1).sum()}")
    if a.max() > 1e-6:
        top = j.loc[a.sort_values(ascending=False).index[:12], ["id", "navn_m", "gw", f"{col}_m", f"{col}_c", f"d_{col}"]]
        print(top.round(3).to_string(index=False))
        per_gw = j.groupby("gw")[f"d_{col}"].apply(lambda s: s.abs().max())
        print("Største avvik per runde:", per_gw.round(4).to_dict())

mm = U / "codex/minutter_antatt.csv"
if mm.exists():
    cm = pd.read_csv(mm)
    print("\nCodex' minuttabell, kolonner:", list(cm.columns))
    mot = pd.read_csv(U / "motor/minutter.csv")
    keys = [k for k in ("id", "gw") if k in cm.columns]
    if keys == ["id", "gw"]:
        pk = next((k for k in ("p_start", "start_prob", "p_start_antatt") if k in cm.columns), None)
        mk = next((k for k in ("forventede_min", "exp_minutes", "minutter", "mins") if k in cm.columns), None)
        jm = mot.merge(cm, on=keys, suffixes=("_m", "_c"))
        if pk:
            d = (jm["p_start_m"] - jm[pk if pk != "p_start" else "p_start_c"]).abs()
            print(f"p_start: største avvik {d.max():.6f}, rader > 0,001: {(d > .001).sum()}")
        if mk:
            d = (jm["forventede_min_m"] - jm[mk if mk != "forventede_min" else "forventede_min_c"]).abs()
            print(f"forventede minutter: største avvik {d.max():.4f}, rader > 0,01: {(d > .01).sum()}")
