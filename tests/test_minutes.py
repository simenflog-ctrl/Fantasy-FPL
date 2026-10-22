"""
Tester for innhoppsleddet i minuttmodellen (flagget SUB_GIVEN_NO_START).

En spiller som starter annenhver kamp og kommer inn i de andre, skal ha
P(innhopp) nær 0,5. Med flagget av (dagens oppførsel) dempes innhopp to ganger
og havner nær 0,25.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import minutes as M  # noqa: E402

RATES = {"p_start_prior": 0.4, "p_start_given_appeared": 0.7, "min_given_start": 85.0,
         "p60_given_start": 0.9, "min_given_sub": 20.0, "p_sub_given_no_start": 0.1}


def _case(monkeypatch, flag: bool, n: int = 20) -> pd.Series:
    monkeypatch.setattr(M, "SUB_GIVEN_NO_START", flag)
    monkeypatch.setattr(M, "last_season_minutes",
                        lambda bs: pd.DataFrame(columns=["element", "prior_p_start", "moved", "min_given_start"]))
    starts = [1 if g % 2 == 0 else 0 for g in range(1, n + 1)]
    pm = pd.DataFrame({"element": 1, "gw": range(1, n + 1), "starts": starts,
                       "minutes": [90 if s else 25 for s in starts]})
    bs = {"teams": [{"id": 1, "short_name": "AAA"}],
          "elements": [{"id": 1, "web_name": "X", "team": 1, "element_type": 3, "now_cost": 50,
                        "status": "a", "chance_of_playing_next_round": None, "news": ""}]}
    return M.build(pm, bs, RATES).iloc[0]


def test_sub_probability_old_behaviour_is_damped(monkeypatch):
    r = _case(monkeypatch, flag=False)
    p_sub = r.p_play - r.p_start
    assert 0.2 < p_sub < 0.3


def test_sub_probability_fixed(monkeypatch):
    r = _case(monkeypatch, flag=True)
    p_sub = r.p_play - r.p_start
    # Kommer inn hver gang han ikke starter. Krympingen mot ligaraten (0,1, vekt
    # 0,7 kamper mot ~2,6 vektede kamper uten start) trekker noe ned, men langt
    # fra den doble dempingen.
    assert 0.75 * (1 - r.p_start) < p_sub <= 1 - r.p_start
    assert p_sub > 0.35
    assert r.p_play <= 1.0


def test_flag_off_by_default():
    assert M.SUB_GIVEN_NO_START is False
