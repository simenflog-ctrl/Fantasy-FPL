"""
Bygger to tabeller fra rådataene:

  data/derived/player_matches.csv  — én rad per spiller per kamp
  data/derived/team_matches.csv    — én rad per lag per kamp, med xG for og imot

Lag-tabellen er hele grunnlaget for lagstyrkemodellen (M1). FPL publiserer ikke
xG på lagnivå noe sted, så den må aggregeres opp fra spillernivå.

EN VIKTIG FELLE: en spillers `team` i bootstrap er klubben han spiller for NÅ,
ikke klubben han spilte for i kampen. Ndiaye gikk fra Everton til City i
september 2026. Bruker vi bootstrap-laget, havner Everton-kampene hans i City
sin xG-sum, og begge lags ratinger blir feil. Derfor utledes laget alltid fra
kampen selv: fixture-en gir hjemme- og bortelag, og `was_home` sier hvilket av
dem spilleren tilhørte.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"

# Kolonner vi tar vare på fra element-summary. Alt annet er støy for modellen.
PLAYER_COLS = [
    "element", "fixture", "round", "was_home", "minutes", "starts",
    "goals_scored", "assists", "clean_sheets", "goals_conceded", "own_goals",
    "penalties_saved", "penalties_missed", "yellow_cards", "red_cards", "saves",
    "bonus", "bps", "total_points",
    "expected_goals", "expected_assists", "expected_goals_conceded",
    "defensive_contribution", "clearances_blocks_interceptions", "recoveries", "tackles",
]

NUMERIC = [
    "minutes", "starts", "goals_scored", "assists", "clean_sheets", "goals_conceded",
    "own_goals", "penalties_saved", "penalties_missed", "yellow_cards", "red_cards",
    "saves", "bonus", "bps", "total_points", "expected_goals", "expected_assists",
    "expected_goals_conceded", "defensive_contribution",
    "clearances_blocks_interceptions", "recoveries", "tackles",
]


def load_json(path: Path):
    return json.loads(path.read_text())


def build_player_matches(fixtures: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    files = sorted((RAW / "element_summary").glob("*.json"))
    if not files:
        raise SystemExit("Ingen element-summary-filer. Kjør src/fetch.py først.")

    for path in files:
        history = load_json(path).get("history", [])
        for row in history:
            rows.append({c: row.get(c) for c in PLAYER_COLS})

    df = pd.DataFrame(rows)
    if df.empty:
        raise SystemExit("Ingen kamphistorikk funnet — er sesongen i gang?")

    for col in NUMERIC:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Utled laget fra kampen, ikke fra spillerens nåværende klubb (se docstring).
    df = df.merge(
        fixtures[["id", "team_h", "team_a", "event"]].rename(columns={"id": "fixture"}),
        on="fixture",
        how="left",
        validate="many_to_one",
    )
    missing = df["team_h"].isna().sum()
    if missing:
        raise SystemExit(f"{missing} spillerrader mangler kamp — rådataene er inkonsistente.")

    df["team"] = df["was_home"].where(df["was_home"], other=False)
    df["team"] = df.apply(lambda r: r["team_h"] if r["was_home"] else r["team_a"], axis=1).astype(int)
    df["opponent"] = df.apply(lambda r: r["team_a"] if r["was_home"] else r["team_h"], axis=1).astype(int)
    df["gw"] = df["event"].astype("Int64")

    return df.drop(columns=["team_h", "team_a", "event"])


def build_team_matches(players: pd.DataFrame, fixtures: pd.DataFrame) -> pd.DataFrame:
    agg = (
        players.groupby(["fixture", "team", "opponent", "was_home", "gw"], as_index=False)
        .agg(
            xg_for=("expected_goals", "sum"),
            xa_for=("expected_assists", "sum"),
            goals_for=("goals_scored", "sum"),
            player_minutes=("minutes", "sum"),
            def_contrib=("defensive_contribution", "sum"),
        )
    )

    # xG imot = motstanderens xG for i samme kamp. Selvjoin på (fixture, team↔opponent).
    other = agg[["fixture", "team", "xg_for", "goals_for"]].rename(
        columns={"team": "opponent", "xg_for": "xg_against", "goals_for": "goals_against"}
    )
    teams = agg.merge(other, on=["fixture", "opponent"], how="left")

    # Sanity: en fullført kamp har ~990 spillerminutter per lag (11 × 90).
    # Vesentlig mindre betyr at vi mangler spillere og xG-summen er for lav.
    played = teams["player_minutes"] > 0
    suspicious = played & (teams["player_minutes"] < 800)
    if suspicious.any():
        print(f"ADVARSEL: {suspicious.sum()} lag-kamper har under 800 spillerminutter "
              "— xG-summene kan være ufullstendige.")

    return teams.sort_values(["gw", "fixture", "team"]).reset_index(drop=True)


def main() -> None:
    fixtures = pd.DataFrame(load_json(RAW / "fixtures.json"))
    players = build_player_matches(fixtures)
    teams = build_team_matches(players, fixtures)

    DERIVED.mkdir(parents=True, exist_ok=True)
    players.to_csv(DERIVED / "player_matches.csv", index=False)
    teams.to_csv(DERIVED / "team_matches.csv", index=False)

    bootstrap = load_json(RAW / "bootstrap.json")
    names = {t["id"]: t["short_name"] for t in bootstrap["teams"]}
    played = teams[teams["player_minutes"] > 0]

    print(f"✓ {len(players)} spiller-kamper, {len(teams)} lag-kamper "
          f"({played['fixture'].nunique()} kamper spilt)")
    if not played.empty:
        top = (played.groupby("team")["xg_for"].mean().sort_values(ascending=False).head(5))
        print("  Høyest xG per kamp:", ", ".join(f"{names[t]} {v:.2f}" for t, v in top.items()))


if __name__ == "__main__":
    main()
