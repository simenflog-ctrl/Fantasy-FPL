"""
Tester for beslutningslagets regnskap: salgspris og frie transfers.

Begge feilet i gw08 uten at noe sa fra: plan.json foreslo en wildcardtropp som
manglet 0,9 m, og startet med én fri transfer når laget hadde to. Fasiten her er
lagets faktiske tilstand før runde 8, hentet fra API-et 22. okt 2026 og
kontrollert for hånd (samarbeid/gw08/grunnlag.md).
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import optimize as O  # noqa: E402

GW08 = ROOT / "samarbeid" / "gw08" / "data"


def _load(name):
    return json.loads((GW08 / name).read_text())


@pytest.fixture(scope="module")
def gw08():
    if not GW08.exists():
        pytest.skip("gw08-data mangler")
    bs = _load("bootstrap.json")
    squad = [p["element"] for p in _load("picks_gw7.json")["picks"]]
    return bs, squad, _load("transfers.json"), _load("entry_history.json")


def test_selling_price_rules():
    assert O.selling_price(5.7, 6.0) == 5.8     # +0,3 → beholder 0,1
    assert O.selling_price(5.7, 6.2) == 5.9     # +0,5 → beholder 0,2 (rundet ned)
    assert O.selling_price(8.0, 7.8) == 7.8     # fall tas fullt
    assert O.selling_price(4.5, 4.5) == 4.5


def test_purchase_and_selling_prices_gw08(gw08):
    bs, squad, transfers, _ = gw08
    now = {e["id"]: e["now_cost"] / 10 for e in bs["elements"]}
    bought = O.purchase_prices(bs, transfers, squad)
    expected = {e["id"]: e["kjopspris"] for e in _load("salgspriser.json")}
    assert bought == pytest.approx(expected)
    sell = {p: O.selling_price(bought[p], now[p]) for p in squad}
    assert sum(sell.values()) == pytest.approx(98.3)


def test_free_transfers_gw08(gw08):
    *_, history = gw08
    # R2 0 brukt → 2; R3–R5 1 brukt → 2; R6 2 brukt → 1; R7 0 brukt → 2.
    assert O.free_transfers(history, 8) == 2
    assert O.free_transfers(history, 7) == 1
    assert O.free_transfers(history, 2) == 1


def test_free_transfers_chip_preserves():
    history = {"chips": [{"name": "wildcard", "event": 4}],
               "current": [{"event": 1, "event_transfers": 0},
                           {"event": 2, "event_transfers": 0},
                           {"event": 3, "event_transfers": 0},
                           {"event": 4, "event_transfers": 12}]}
    # 3 lagret før wildcard i R4; beholdes, men R4 gir ingen ny.
    assert O.free_transfers(history, 5) == 3
