"""Felles oppsett for testene: motorens mappe på sys.path, og gw10 lastet én gang."""
import sys
from pathlib import Path

import pytest

MOTOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOTOR))
sys.path.insert(0, str(Path(__file__).resolve().parent))
GW10 = MOTOR.parent / 'gw10'


def pytest_addoption(parser):
    parser.addoption('--langsom', action='store_true', help='kjør også de langsomme testene (flere minutter)')


def pytest_collection_modifyitems(config, items):
    if config.getoption('--langsom'):
        return
    for item in items:
        if 'langsom' in item.keywords:
            item.add_marker(pytest.mark.skip(reason='langsom; kjør med --langsom'))


def pytest_configure(config):
    config.addinivalue_line('markers', 'langsom: tester som tar flere minutter')


@pytest.fixture(scope='session')
def gw10():
    """(uke, minuttabell, prognose, motor) for runde 10 med de frosne gw10-filene."""
    from uke import Uke
    import poeng
    from motor import Motor
    if not (GW10 / 'data' / 'element_summary').exists():
        pytest.skip('samarbeid/gw10/data/element_summary mangler (ligger ikke i git; kopier fra hovedmappen)')
    u = Uke.fra_mappe(GW10, 10, 19, input_mappe=GW10 / 'codex' / 'input')
    md, _ = poeng.lag_minutter(u, minuttabell=GW10 / 'codex' / 'minutter_antatt.csv')
    pr = poeng.prognose(u, md)
    return u, md, pr, Motor(u, pr, ft=2, fh_start=16)


@pytest.fixture(scope='session')
def gw10_standard(gw10):
    """Hele standardanalysen for runde 10 (ca. ett minutt)."""
    return gw10[3].standardanalyse(logg=lambda s: None)
