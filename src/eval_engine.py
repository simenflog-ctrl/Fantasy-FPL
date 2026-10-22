"""Offline adapters for the production forecast functions.

Only input reconstruction lives here, never alternative xP/minute formulas.
Historical API status and deadline rosters are unavailable: availability=1 and
roster metadata comes from the observed round, as in the original baseline.
Configurations are run serially; the minute prior bridge scopes one module
input because minutes.py belongs to the parallel P2 change.
"""
from __future__ import annotations

from contextlib import contextmanager, redirect_stdout
from functools import lru_cache
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd

import expected_points as E
import minutes as M
import team_strength as T

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data/cache/vaastav"
PRIOR_OF = {"2025-26": "2024-25", "2024-25": "2023-24", "2023-24": "2022-23"}


def fixture_ids(season: str, values: pd.Series) -> pd.Series:
    """Disjoint, reversible integer namespaces; raw FPL IDs restart each year."""
    if not values.between(0, 999999).all():
        raise ValueError("Expected raw fixture IDs in [0, 999999]")
    return int(season[:4]) * 1_000_000 + values.astype('int64')


@lru_cache(maxsize=8)
def _load_season(season: str, cache: str) -> pd.DataFrame:
    path = Path(cache) / season / "gws/merged_gw.csv"
    d = pd.read_csv(path).drop_duplicates().copy()  # fail locally, never fetch
    if d.duplicated(['name', 'fixture']).any():
        # Distinct homonyms (e.g. 2022 Ben Davies) remain in prior data.
        if d.duplicated(['element', 'fixture']).any():
            raise ValueError(f"Conflicting player-fixture rows in {path}")
    d['source_fixture'] = d.fixture
    d['fixture'] = fixture_ids(season, d.fixture)
    d['season'] = season
    d['pos'] = d.position.map({'GKP':'GK', 'GK':'GK', 'DEF':'DEF', 'MID':'MID', 'FWD':'FWD', 'AM':'MID'}).fillna('MID')
    if 'defensive_contribution' not in d:
        d['defensive_contribution'] = 0
    sides = d[['fixture', 'team']].drop_duplicates()
    opp = sides.merge(sides, on='fixture')
    opp = opp[opp.team_x != opp.team_y].rename(columns={'team_x':'team', 'team_y':'_opp_name'})
    if opp.duplicated(['fixture','team']).any():
        raise ValueError("More than two teams per fixture")
    return d.merge(opp, on=['fixture','team'], how='left', validate='many_to_one')


def load_season(season: str, cache=CACHE) -> pd.DataFrame:
    """Copy-on-read cache; one configuration cannot contaminate another."""
    return _load_season(season, str(cache)).copy(deep=True)


def team_matches(d: pd.DataFrame, teams: dict) -> pd.DataFrame:
    q = d.groupby(['fixture','team','GW','was_home'], as_index=False).agg(
        xg_for=('expected_goals','sum'), goals_for=('goals_scored','sum'),
        player_minutes=('minutes','sum'))
    other = q[['fixture','team','xg_for','goals_for']].rename(columns={
        'team':'opponent', 'xg_for':'xg_against', 'goals_for':'goals_against'})
    q = q.merge(other, on='fixture')
    q = q[q.team != q.opponent].copy()
    q['team'] = q.team.map(teams)
    q['opponent'] = q.opponent.map(teams)
    return q.rename(columns={'GW':'gw'})


@contextmanager
def minute_history(csv_text: str):
    """Inject CSV data in memory through the existing production reader.

    No monkeypatch of formulas or functions, no disk/network and no edits to
    minutes.py. Always restore the input, including when a candidate raises.
    Must not be used concurrently from threads (flags are module-wide too).
    """
    saved = M.LAST_SEASON_GWS
    try:
        M.LAST_SEASON_GWS = StringIO(csv_text)
        yield
    finally:
        M.LAST_SEASON_GWS = saved


def predict_frames(pm, bs, team_matches, priors, home_adv, fixtures, *,
                   minute_prior_csv, personal_priors, prior_fixtures,
                   season, n_gw=1):
    """Run actual minute, team and points functions on supplied data frames."""
    with minute_history(minute_prior_csv):
        mins = M.build(pm, bs, M.league_rates(pm))
    ratings = T.fit_current(team_matches, priors, home_adv)
    proj = T.project_fixtures(ratings, n_gw=n_gw, fixtures=fixtures)
    # Production projections are serialized to 3 decimals before xP reads them.
    proj[['xg_for','xg_against']] = proj[['xg_for','xg_against']].round(3)
    xp, diagnostics = E.forecast(pm[pm.minutes > 0], mins, ratings, proj, bs,
        team_matches, personal_priors=personal_priors, prior_fixtures=prior_fixtures,
        season=season, n_gw=n_gw)
    return xp, diagnostics


def _prior_inputs(prev, teams, ids):
    """Reconstruct the prior-season fixture/cleaned-player input files."""
    tm = team_matches(prev, teams)
    # Legacy reconstruction fitted last season in reverse raw fixture order.
    home = tm[tm.was_home].sort_values('fixture', ascending=False)
    fx = pd.DataFrame(dict(id=home.fixture, team_h=home.team, team_a=home.opponent,
        team_h_score=home.goals_for, team_a_score=home.goals_against, finished=True))
    t = pd.DataFrame([dict(id=i, short_name=n) for n,i in teams.items()])
    prior = T.fit_prior_from_last_season(fx, t)
    agg = prev.groupby('name').agg(minutes=('minutes','sum'),
        goals_scored=('goals_scored','sum'), assists=('assists','sum'),
        bps=('bps','sum'), bonus=('bonus','sum'), yellow_cards=('yellow_cards','sum'))
    agg = agg[agg.minutes >= E.PRIOR_MIN_MINUTES].copy()
    agg['element'] = agg.index.map(ids)
    for source, dest in [('goals_scored','p_goals'), ('assists','p_assists'),
                         ('bps','p_bps'), ('bonus','p_bonus'), ('yellow_cards','p_yellow')]:
        agg[dest] = agg[source]/agg.minutes*90
    ep = agg[['element','p_goals','p_assists','p_bps','p_bonus','p_yellow']].reset_index(drop=True)
    return prior, ep, fx


def walk_forward(d, prev, *, first_gw=8, rounds=None, quiet=True):
    """Train strictly before t, score t; same production functions as live.

    Historical player keys retain the original reconstruction's exact names;
    integer element keys are stable within a season/configuration comparison.
    Season, element, fixture is the pairing key (not name/GW alone).
    """
    season = str(d.season.iloc[0])
    names = sorted(set(d.name) | set(prev.name))
    ids = {n:i+1 for i,n in enumerate(names)}
    teams = {n:i+1 for i,n in enumerate(sorted(set(d.team) | set(prev.team)))}
    prior, personal, prior_fx = _prior_inputs(prev, teams, ids)
    prior_csv = prev.to_csv(index=False)
    results, diagnostics = [], []
    for gw in sorted(g for g in d.GW.unique() if g >= first_gw):
        if rounds is not None and gw not in rounds:
            continue
        hist, test = d[d.GW < gw], d[d.GW == gw]
        if hist.empty or test.empty:
            continue
        latest = pd.concat([hist, test]).drop_duplicates('name', keep='last')
        bs = {'teams':[dict(id=i,short_name=n,name=n) for n,i in teams.items()], 'elements':[]}
        pos = {'GK':1,'DEF':2,'MID':3,'FWD':4}
        for r in latest.itertuples():
            bs['elements'].append(dict(id=ids[r.name], team=teams[r.team], first_name=r.name,
                second_name='', web_name=r.name, element_type=pos[r.pos], now_cost=r.value, status='a'))
        now = pd.DataFrame([dict(team_id=teams[n], short_name=n)
                            for n in sorted(set(hist.team) | set(test.team))])
        priors, ha = T.build_priors(now, prior=prior)
        pm = hist.assign(element=hist.name.map(ids)).rename(columns={'GW':'gw'})
        tm = team_matches(hist, teams)
        h = test[test.was_home][['fixture','team','_opp_name']].drop_duplicates()
        fixtures = pd.DataFrame(dict(id=h.fixture, team_h=h.team.map(teams),
            team_a=h._opp_name.map(teams), event=gw, finished=False,
            team_h_difficulty=0, team_a_difficulty=0))
        # No test outcomes in any of the inputs above.
        with redirect_stdout(StringIO()) if quiet else _null_context():
            pred, diag = predict_frames(pm, bs, tm, priors, ha, fixtures,
                minute_prior_csv=prior_csv, personal_priors=personal,
                prior_fixtures=prior_fx, season=season)
        pred['name'] = pred.element.map({i:n for n,i in ids.items()})
        obs = test[['name','fixture','source_fixture','total_points','bonus','minutes','value']].rename(
            columns={'total_points':'actual','bonus':'actual_bonus','minutes':'mins'})
        pred = pred.merge(obs, on=['name','fixture'], validate='one_to_one')
        for col in ['xp','xp_bonus','actual','actual_bonus','mins']:
            pred[col] = pd.to_numeric(pred[col], errors='raise')
        hist_recent = hist[hist.GW >= gw-3].groupby('name').total_points.mean()
        hist_avg = hist.groupby('name').total_points.mean()
        pred['b_form'] = pred.name.map(hist_recent).fillna(pred.name.map(hist_avg)).fillna(0)
        pred['season'] = season
        results.append(pred)
        diagnostics.append(dict(season=season, gw=int(gw), n=len(pred), **diag))
    out = pd.concat(results, ignore_index=True)
    out = out.sort_values(['element','gw','fixture']).reset_index(drop=True)
    out.attrs['diagnostics'] = diagnostics
    return out


@contextmanager
def _null_context():
    yield
