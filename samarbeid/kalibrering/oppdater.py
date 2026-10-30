"""Prognoseevaluering (steg 2 punkt 4 i samarbeid/RUTINE.md).

Legger én runde inn i logg.csv og skriver oversikt.md på nytt fra hele loggen.
Endrer ikke modellen; måler den bare.

Bruk (fra repoets rot):
  python samarbeid/kalibrering/oppdater.py --runde 8 \
      --forrige samarbeid/gw08 --spillerfil codex/spillerpoeng_r2.csv \
      --ny samarbeid/gw09

  --forrige : forrige ukes mappe (frosset prognose, SHA256SUMS, data/bootstrap.json for pris/posisjon)
  --spillerfil : den frosne spillerfilen, relativ til --forrige; må stå i prognose/SHA256SUMS
  --ny : ukens mappe; leser data/live_gw<runde>.json og data/picks_gw<runde>.json

Nekter å legge inn en runde som allerede finnes i logg.csv, og nekter hvis sjekksummen ikke stemmer.
Med --bare-oversikt skrives bare oversikt.md på nytt.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HER = Path(__file__).resolve().parent
LOGG = HER / "logg.csv"
OVERSIKT = HER / "oversikt.md"
KOLONNER = ["runde", "id", "navn", "posisjon", "pris", "minutter",
            "xp_codex", "xp_repo", "faktisk", "i_tropp", "kaptein"]
POS = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}
SETT = {"codex": "xp_codex", "repo_hybrid": "xp_repo"}


def sjekk_sum(forrige: Path, spillerfil: str) -> None:
    sums = {}
    for linje in (forrige / "prognose" / "SHA256SUMS").read_text().splitlines():
        if linje.strip():
            h, navn = linje.split(maxsplit=1)
            sums[navn.strip()] = h
    if spillerfil not in sums:
        sys.exit(f"STOPP: {spillerfil} står ikke i {forrige}/prognose/SHA256SUMS (ikke frosset).")
    faktisk = hashlib.sha256((forrige / spillerfil).read_bytes()).hexdigest()
    if faktisk != sums[spillerfil]:
        sys.exit(f"STOPP: sjekksummen for {spillerfil} stemmer ikke ({faktisk} != {sums[spillerfil]}).")


def lag_rader(runde: int, forrige: Path, spillerfil: str, ny: Path) -> pd.DataFrame:
    sp = pd.read_csv(forrige / spillerfil)
    sp = sp[sp["gw"] == runde]
    if sp.empty:
        sys.exit(f"STOPP: ingen rader med gw=={runde} i {spillerfil}.")
    if sp["id"].duplicated().any():
        sys.exit("STOPP: duplikate id-er i spillerfilen for runden.")
    sp = sp[(sp["codex"] >= 1) | (sp["repo_hybrid"] >= 1)]

    bs = json.loads((forrige / "data" / "bootstrap.json").read_text())
    el = {e["id"]: e for e in bs["elements"]}
    live = json.loads((ny / "data" / f"live_gw{runde}.json").read_text())
    st = {x["id"]: x["stats"] for x in live["elements"]}
    picks = json.loads((ny / "data" / f"picks_gw{runde}.json").read_text())
    tropp = {p["element"] for p in picks["picks"]}
    kapt = {p["element"] for p in picks["picks"] if p["is_captain"]}

    mangler = [i for i in sp["id"] if i not in el or i not in st]
    if mangler:
        sys.exit(f"STOPP: id-er mangler i bootstrap eller live: {mangler}")

    rader = []
    for r in sp.itertuples():
        e = el[r.id]
        rader.append({
            "runde": runde, "id": r.id, "navn": e["web_name"],
            "posisjon": POS[e["element_type"]], "pris": e["now_cost"] / 10,
            "minutter": st[r.id]["minutes"],
            "xp_codex": round(r.codex, 4), "xp_repo": round(r.repo_hybrid, 4),
            "faktisk": st[r.id]["total_points"],
            "i_tropp": int(r.id in tropp), "kaptein": int(r.id in kapt),
        })
    return pd.DataFrame(rader, columns=KOLONNER)


def prisklasse(p: float) -> str:
    if p < 5.0:
        return "< 5,0"
    if p < 7.5:
        return "5,0–7,4"
    if p < 10.0:
        return "7,5–9,9"
    return "≥ 10,0"


KLASSER = ["< 5,0", "5,0–7,4", "7,5–9,9", "≥ 10,0"]


def mal(df: pd.DataFrame, xp: str) -> dict:
    """Skjevhet = snitt av faktisk − forventet, SE = sd/√n, og tydelighetskriteriet."""
    d = df["faktisk"] - df[xp]
    n = len(d)
    snitt = d.mean() if n else np.nan
    se = d.std(ddof=1) / np.sqrt(n) if n > 1 else np.nan
    per_runde = d.groupby(df["runde"]).mean()
    runder = len(per_runde)
    fortegn = np.sign(snitt) if n else 0
    samme = int((np.sign(per_runde) == fortegn).sum()) if fortegn != 0 else 0
    over2 = bool(se > 0 and abs(snitt) > 2 * se) if not np.isnan(se) else False
    tydelig = over2 and samme >= 4 and runder >= 4
    return dict(n=n, runder=runder, snitt=snitt, se=se, over2=over2, samme=samme, tydelig=tydelig)


def fmt(x: float, d: int = 2) -> str:
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:+.{d}f}".replace(".", ",")


def num(x: float, d: int = 2) -> str:
    return f"{x:.{d}f}".replace(".", ",")


def fmt_se(x: float) -> str:
    return "–" if x is None or np.isnan(x) else f"{x:.2f}".replace(".", ",")


def vurdering(m: dict) -> str:
    if m["tydelig"]:
        return "**tydelig**"
    if m["over2"]:
        return f"> 2 SE, men {m['runder']} runde(r) / {m['samme']} med samme fortegn"
    return ""


def skriv_oversikt(logg: pd.DataFrame) -> None:
    logg = logg.copy()
    logg["prisklasse"] = logg["pris"].map(prisklasse)
    runder = sorted(logg["runde"].unique())
    ut = []
    ut.append("# Prognoseevaluering\n")
    ut.append("Skrevet av `oppdater.py` fra `logg.csv`; ikke rediger for hånd.\n")
    ut.append(f"Runder i loggen: {', '.join(f'R{r}' for r in runder)} ({len(runder)} runde(r), {len(logg)} rader).\n")
    ut.append("Skjevhet = snitt av faktisk − forventet poeng (positiv = modellen undervurderer). SE = standardfeil (sd/√n).\n"
              "Tydelig skjevhet krever |skjevhet| > 2 SE, samme fortegn i minst fire runder og minst fire runder (RUTINE steg 2.4).\n"
              "Svakere mønstre noteres, men brukes ikke.\n")

    tydelige = []
    ut.append("## Totalt og per runde\n")
    ut.append("| Utvalg | n | Codex skjevhet | Codex SE | Repo skjevhet | Repo SE |")
    ut.append("|---|---|---|---|---|---|")
    for navn, sub in [("Alle", logg)] + [(f"R{r}", logg[logg["runde"] == r]) for r in runder]:
        mc, mr = mal(sub, "xp_codex"), mal(sub, "xp_repo")
        ut.append(f"| {navn} | {mc['n']} | {fmt(mc['snitt'])} | {fmt_se(mc['se'])} | {fmt(mr['snitt'])} | {fmt_se(mr['se'])} |")
    ut.append("")

    for sett, xp in SETT.items():
        ut.append(f"## Posisjon × prisklasse, {sett}\n")
        ut.append("| Posisjon | Prisklasse | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |")
        ut.append("|---|---|---|---|---|---|---|---|---|")
        for pos in ["GKP", "DEF", "MID", "FWD"]:
            for k in KLASSER:
                sub = logg[(logg["posisjon"] == pos) & (logg["prisklasse"] == k)]
                if sub.empty:
                    continue
                m = mal(sub, xp)
                if m["tydelig"]:
                    tydelige.append(f"{sett}: {pos} {k}: {fmt(m['snitt'])} (SE {fmt_se(m['se'])}, {m['runder']} runder)")
                ut.append(f"| {pos} | {k} | {m['n']} | {m['runder']} | {num(sub[xp].mean())} | {num(sub['faktisk'].mean())} | "
                          f"{fmt(m['snitt'])} | {fmt_se(m['se'])} | {vurdering(m)} |")
        ut.append("")

    ut.append("## Topp ti forventet per runde (kapteinskandidatene)\n")
    ut.append("Topp ti velges separat for hvert poengsett.\n")
    ut.append("| Poengsett | n | Runder | Snitt forventet | Snitt faktisk | Skjevhet | SE | Merknad |")
    ut.append("|---|---|---|---|---|---|---|---|")
    topp = {}
    for sett, xp in SETT.items():
        sub = logg.sort_values(xp, ascending=False).groupby("runde").head(10)
        topp[sett] = sub
        m = mal(sub, xp)
        if m["tydelig"]:
            tydelige.append(f"{sett}: topp ti: {fmt(m['snitt'])} (SE {fmt_se(m['se'])}, {m['runder']} runder)")
        ut.append(f"| {sett} | {m['n']} | {m['runder']} | {num(sub[xp].mean())} | {num(sub['faktisk'].mean())} | "
                  f"{fmt(m['snitt'])} | {fmt_se(m['se'])} | {vurdering(m)} |")
    ut.append("")
    for sett, xp in SETT.items():
        ut.append(f"### Topp ti {sett}, siste runde (R{runder[-1]})\n")
        ut.append("| Spiller | Pos | Pris | Forventet | Faktisk | Min |")
        ut.append("|---|---|---|---|---|---|")
        s = topp[sett][topp[sett]["runde"] == runder[-1]].sort_values(xp, ascending=False)
        for r in s.itertuples():
            ut.append(f"| {r.navn} | {r.posisjon} | {num(r.pris, 1)} | {num(getattr(r, xp))} | {r.faktisk} | {r.minutter} |")
        ut.append("")

    ut.append("## Konklusjon\n")
    if tydelige:
        ut.append("Tydelige skjevheter:\n")
        ut.extend(f"- {t}" for t in tydelige)
    else:
        ut.append(f"Ingen tydelige skjevheter ennå ({len(runder)} runde(r)). Kriteriet kan tidligst slå inn etter fire runder.")
    ut.append("")
    OVERSIKT.write_text("\n".join(ut))


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--runde", type=int)
    a.add_argument("--forrige", type=Path)
    a.add_argument("--spillerfil")
    a.add_argument("--ny", type=Path)
    a.add_argument("--bare-oversikt", action="store_true")
    args = a.parse_args()

    logg = pd.read_csv(LOGG) if LOGG.exists() else pd.DataFrame(columns=KOLONNER)
    if not args.bare_oversikt:
        if None in (args.runde, args.forrige, args.spillerfil, args.ny):
            sys.exit("Mangler --runde, --forrige, --spillerfil eller --ny.")
        if (logg["runde"] == args.runde).any():
            sys.exit(f"STOPP: runde {args.runde} finnes allerede i logg.csv. Ingenting endret.")
        sjekk_sum(args.forrige, args.spillerfil)
        nye = lag_rader(args.runde, args.forrige, args.spillerfil, args.ny)
        logg = pd.concat([logg, nye], ignore_index=True) if len(logg) else nye
        logg = logg.sort_values(["runde", "id"])
        logg.to_csv(LOGG, index=False)
        print(f"La inn R{args.runde}: {len(nye)} rader.")
    if logg.empty:
        sys.exit("Loggen er tom.")
    skriv_oversikt(logg)
    print(f"Skrev {OVERSIKT}")


if __name__ == "__main__":
    main()
