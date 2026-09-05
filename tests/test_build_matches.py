"""
Tester den ene tingen i build_matches som stille kan ødelegge hele modellen:
at et lag utledes fra kampen og ikke fra spillerens nåværende klubb.

Scenarioet er Ndiaye — Everton i GW1-2, Man City fra GW3. Bruker vi bootstrap
sin `team`, havner Everton-prestasjonene hans i City sin xG-sum. Da får City
for høy angrepsrating og Everton for lav, og hver eneste fixture-vurdering
nedstrøms blir feil. Feilen gir ingen feilmelding — den gir bare gale tall.
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import build_matches as bm  # noqa: E402

EVE, MCI, LIV = 7, 13, 12


def setup_fake_data(tmp: Path) -> None:
    raw = tmp / "data" / "raw"
    (raw / "element_summary").mkdir(parents=True)

    fixtures = [
        {"id": 101, "event": 1, "team_h": EVE, "team_a": LIV},
        {"id": 102, "event": 2, "team_h": MCI, "team_a": EVE},
        {"id": 103, "event": 3, "team_h": MCI, "team_a": LIV},
    ]
    (raw / "fixtures.json").write_text(json.dumps(fixtures))
    (raw / "bootstrap.json").write_text(json.dumps({
        "teams": [{"id": EVE, "short_name": "EVE"},
                  {"id": MCI, "short_name": "MCI"},
                  {"id": LIV, "short_name": "LIV"}]
    }))

    def hist(fixture, rnd, was_home, xg, minutes=90):
        return {"element": 0, "fixture": fixture, "round": rnd, "was_home": was_home,
                "minutes": minutes, "starts": 1, "goals_scored": 0, "assists": 0,
                "clean_sheets": 0, "goals_conceded": 0, "own_goals": 0,
                "penalties_saved": 0, "penalties_missed": 0, "yellow_cards": 0,
                "red_cards": 0, "saves": 0, "bonus": 0, "bps": 0, "total_points": 2,
                "expected_goals": xg, "expected_assists": 0.0,
                "expected_goals_conceded": 0.0, "defensive_contribution": 0,
                "clearances_blocks_interceptions": 0, "recoveries": 0, "tackles": 0}

    # Ndiaye: Everton hjemme i GW1, Everton borte i GW2, så City hjemme i GW3.
    (raw / "element_summary" / "1.json").write_text(json.dumps({"history": [
        hist(101, 1, True, 0.50),    # for Everton
        hist(102, 2, False, 0.40),   # for Everton, borte mot City
        hist(103, 3, True, 0.30),    # for City
    ]}))

    # En Liverpool-spiller som aldri bytter, som kontroll.
    (raw / "element_summary" / "2.json").write_text(json.dumps({"history": [
        hist(101, 1, False, 0.20),
        hist(103, 3, False, 0.10),
    ]}))


def test_team_derived_from_fixture_not_current_club(tmp_path, monkeypatch):
    setup_fake_data(tmp_path)
    monkeypatch.setattr(bm, "RAW", tmp_path / "data" / "raw")
    monkeypatch.setattr(bm, "DERIVED", tmp_path / "data" / "derived")

    fixtures = pd.DataFrame(json.loads((bm.RAW / "fixtures.json").read_text()))
    players = bm.build_player_matches(fixtures)
    teams = bm.build_team_matches(players, fixtures)

    def xg(team, fixture):
        row = teams[(teams.team == team) & (teams.fixture == fixture)]
        return float(row["xg_for"].iloc[0])

    # GW1 og GW2 tilhører Everton, ikke City — selv om Ndiaye spiller for City nå.
    assert xg(EVE, 101) == 0.50, "GW1-bidraget skal telle for Everton"
    assert xg(EVE, 102) == 0.40, "GW2-bidraget skal telle for Everton"
    assert xg(MCI, 103) == 0.30, "GW3-bidraget skal telle for City"

    # City skal ikke ha fått noe fra kampene før overgangen. Ndiaye spilte i
    # begge, men for Everton — så City skal ikke ha rader der i det hele tatt.
    assert teams[(teams.team == MCI) & (teams.fixture == 101)].empty
    assert teams[(teams.team == MCI) & (teams.fixture == 102)].empty, \
        "City fikk tildelt en kamp de ikke hadde registrerte spillere i"

    # xG imot skal være motstanderens xG for, i samme kamp.
    liv_against = teams[(teams.team == LIV) & (teams.fixture == 101)]["xg_against"].iloc[0]
    assert float(liv_against) == 0.50


def test_home_away_flags(tmp_path, monkeypatch):
    setup_fake_data(tmp_path)
    monkeypatch.setattr(bm, "RAW", tmp_path / "data" / "raw")
    monkeypatch.setattr(bm, "DERIVED", tmp_path / "data" / "derived")

    fixtures = pd.DataFrame(json.loads((bm.RAW / "fixtures.json").read_text()))
    players = bm.build_player_matches(fixtures)

    gw2 = players[players.fixture == 102].iloc[0]
    assert gw2["team"] == EVE and gw2["opponent"] == MCI and not gw2["was_home"]
