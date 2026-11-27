"""Liten syntetisk liga for tester: 6 lag, 90 spillere, runde 1-5 spilt, horisont runde 6-9.

Runde 6: 1-2, 3-4, 5-6.            Vanlig runde.
Runde 7: 1-2, 1-2, 3-4.            Lag 1 og 2 har DOBBELTRUNDE (to like kamper), lag 5 og 6 har BLANK runde.
Runde 8: 2-1, 4-3, 6-5.            Vanlig runde.
Runde 9: 1-3, 2-5, 4-6.            Vanlig runde.
Lag 1 har altså nøyaktig samme kamp (hjemme mot lag 2) én gang i runde 6 og to ganger i runde 7.
"""
import copy

import numpy as np

from conftest import GW10
from uke import Uke, les_json

POSISJONER = [1] * 2 + [2] * 5 + [3] * 5 + [4] * 3
STARTER = [1, 0] + [1, 1, 1, 1, 0] + [1, 1, 1, 1, 0] + [1, 1, 0]
SPILT = {1: [(1, 6), (2, 5), (3, 4)], 2: [(6, 4), (5, 3), (1, 2)], 3: [(2, 6), (3, 1), (4, 5)],
         4: [(6, 3), (4, 2), (5, 1)], 5: [(3, 2), (4, 1), (5, 6)]}
KOMMENDE = {6: [(1, 2), (3, 4), (5, 6)], 7: [(1, 2), (1, 2), (3, 4)], 8: [(2, 1), (4, 3), (6, 5)],
            9: [(1, 3), (2, 5), (4, 6)]}
# Troppen: (lag, plass i lagets spillerliste). Maks tre per lag, 2/5/5/3.
TROPP = [(1, 0), (2, 0), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (3, 7), (4, 7), (5, 7), (6, 7), (6, 8),
         (1, 12), (2, 12), (6, 12)]


def pid(lag, j):
    return (lag - 1) * 15 + j + 1


def bygg(runde=6, slutt=9, kommende=None, bank=20):
    """Returnerer en Uke for den syntetiske ligaen. `kommende` kan erstatte kampprogrammet i horisonten."""
    rng = np.random.RandomState(1)
    scoring = les_json(GW10 / 'data' / 'bootstrap.json')['game_config']['scoring']
    kommende = copy.deepcopy(kommende or KOMMENDE)
    fixtures, fid = [], 0
    for gw, kamper in list(SPILT.items()) + list(kommende.items()):
        for h, a in kamper:
            fid += 1
            fixtures.append(dict(id=fid, event=gw, team_h=h, team_a=a, finished=gw in SPILT,
                                 kickoff_time='2030-08-%02dT15:00:00Z' % (gw + 9)))
    elements, history, pm = [], {}, []
    for lag in range(1, 7):
        for j, pos in enumerate(POSISJONER):
            p = pid(lag, j)
            start = STARTER[j]
            xg90 = {1: 0., 2: .04, 3: .15, 4: .40}[pos] * rng.uniform(.5, 1.5)
            rows, tot = [], dict(minutes=0, starts=0, xg=0., saves=0, bonus=0)
            for f in fixtures:
                if not f['finished'] or lag not in (f['team_h'], f['team_a']):
                    continue
                minutter = 90 if start else (15 if f['event'] % 2 else 0)
                xg = round(xg90 * minutter / 90 * rng.uniform(.5, 1.5), 2)
                rows.append(dict(round=f['event'], starts=start, minutes=minutter,
                                 defensive_contribution=int(rng.randint(5, 15))))
                pm.append(dict(element=p, fixture=f['id'], team=lag, gw=f['event'], minutes=minutter, expected_goals=xg))
                tot['minutes'] += minutter
                tot['starts'] += start
                tot['xg'] += xg
                tot['saves'] += 3 if (pos == 1 and start) else 0
                tot['bonus'] += int(start and rng.rand() < .2)
            history[p] = dict(history=rows, history_past=[])
            elements.append(dict(id=p, web_name='L%dS%02d' % (lag, j), team=lag, element_type=pos,
                                 now_cost=int(40 + 5 * pos * start + rng.randint(0, 8) * start), status='a',
                                 chance_of_playing_next_round=None, can_select=True, minutes=tot['minutes'],
                                 starts=tot['starts'], expected_goals='%.2f' % tot['xg'],
                                 expected_assists='%.2f' % (tot['xg'] * .6), bonus=tot['bonus'], yellow_cards=int(start),
                                 red_cards=0, own_goals=0, penalties_saved=0, penalties_missed=0, saves=tot['saves'],
                                 total_points=10 * start))
    bootstrap = dict(elements=elements, teams=[dict(id=t, short_name='L%d' % t) for t in range(1, 7)],
                     game_config=dict(scoring=scoring))
    repo = []
    for f in fixtures:
        if f['finished']:
            continue
        for e in elements:
            if e['team'] in (f['team_h'], f['team_a']):
                repo.append(dict(element=e['id'], gw=f['event'], xp=2 + (e['id'] % 7) * .5,
                                 exp_minutes=80 if e['starts'] else 10))
    cost = {e['id']: e['now_cost'] for e in elements}
    salg = [dict(id=pid(lag, j), salgspris=cost[pid(lag, j)] / 10) for lag, j in TROPP]
    return Uke(bootstrap, fixtures, salg, history, pm, repo, runde, slutt, bank, '2030/31')
