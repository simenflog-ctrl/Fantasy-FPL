"""Fast offline parity of production I/O and the in-memory evaluation engine."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import expected_points as E
import minutes as M
import team_strength as T
import eval_engine as X
import evaluate_pred as P


@pytest.fixture
def frozen(tmp_path, monkeypatch):
    """Two teams, all positions, starts/subs/unavailable and keeper xG > 0."""
    names=['Alpha Keeper','Alpha Back','Alpha Mid','Alpha Forward',
           'Beta Keeper','Beta Back','Beta Mid','Beta Forward']
    bs={'teams':[dict(id=1,name='Alpha',short_name='A'),dict(id=2,name='Beta',short_name='B')],
        'elements':[], 'game_config':{'scoring':{'goals_scored':{'GKP':10,'DEF':6,'MID':5,'FWD':4}}}}
    for i,name in enumerate(names,1):
        first,last=name.rsplit(' ',1)
        bs['elements'].append(dict(id=i,first_name=first,second_name=last,web_name=name,
            team=1 if i<=4 else 2,element_type=(i-1)%4+1,now_cost=50,
            status='i' if i==8 else 'a'))
    rows=[]
    for gw in range(1,7):
        for i,name in enumerate(names,1):
            start=not(i==4 and gw%2==0)
            mins=90 if start else 22
            rows.append(dict(name=name,element=i,team='Alpha' if i<=4 else 'Beta',
                fixture=100+gw,GW=gw,gw=gw,starts=int(start),minutes=mins,
                expected_goals=.05*i,expected_assists=.03*i,saves=3 if i in (1,5) else 0,
                defensive_contribution=12,yellow_cards=int(i==3),bps=10+3*i,
                goals_scored=int(i==4 and gw==2),assists=int(i==3 and gw==2),
                bonus=3 if i==4 else 2 if i==7 else 1 if i==3 else 0))
    prev=pd.DataFrame(rows)
    pm=prev[prev.gw<=3].copy()
    pm['team']=np.where(pm.element<=4,1,2)
    # Production prior matching compares full team names.
    prior_csv=prev.to_csv(index=False)
    tm=pd.DataFrame([dict(fixture=100+g,gw=g,team=t,opponent=3-t,
        was_home=t==(1 if g%2 else 2),xg_for=1+.1*t,goals_against=g%3,
        player_minutes=360) for g in range(1,4) for t in (1,2)])
    fxprev=pd.DataFrame([dict(id=i,finished=True,team_h=1,team_a=2,
        team_h_score=i%3,team_a_score=(i+1)%3) for i in range(1,7)])
    teams=pd.DataFrame([dict(id=1,short_name='A'),dict(id=2,short_name='B')])
    fx=pd.DataFrame([dict(id=201,event=4,finished=False,team_h=1,team_a=2,
        team_h_difficulty=2,team_a_difficulty=3)])
    totals=prev.groupby('element',as_index=False).agg(minutes=('minutes','sum'),
        goals_scored=('goals_scored','sum'),assists=('assists','sum'),bps=('bps','sum'),
        bonus=('bonus','sum'),yellow_cards=('yellow_cards','sum'))
    totals['first_name']=[e['first_name'] for e in bs['elements']]
    totals['second_name']=[e['second_name'] for e in bs['elements']]
    raw=tmp_path/'raw';derived=tmp_path/'derived';prior=tmp_path/'prior'
    for d in [raw,derived,prior]:d.mkdir()
    prev.to_csv(prior/'minutes.csv',index=False)
    totals.to_csv(prior/'cleaned.csv',index=False)
    fxprev.to_csv(prior/'fixtures_2025-26.csv',index=False)
    teams.to_csv(prior/'teams_2025-26.csv',index=False)
    (raw/'bootstrap.json').write_text(json.dumps(bs))
    done=pd.DataFrame([dict(id=i,finished=True,event=i-100) for i in range(101,104)])
    (raw/'fixtures.json').write_text(pd.concat([fx,done],ignore_index=True).to_json(orient='records'))
    pm.to_csv(derived/'player_matches.csv',index=False)
    tm.to_csv(derived/'team_matches.csv',index=False)
    monkeypatch.setattr(E,'ROOT',tmp_path)
    monkeypatch.setattr(E,'RAW',raw);monkeypatch.setattr(E,'DERIVED',derived)
    monkeypatch.setattr(E,'LAST_SEASON',str(prior/'cleaned.csv'))
    monkeypatch.setattr(E,'PRIOR_FIXTURES',prior/'fixtures_2025-26.csv')
    monkeypatch.setattr(T,'RAW',raw);monkeypatch.setattr(T,'PRIOR',prior)
    monkeypatch.setattr(M,'LAST_SEASON_GWS',str(prior/'minutes.csv'))
    now=pd.DataFrame([dict(team_id=1,short_name='A'),dict(team_id=2,short_name='B')])
    return dict(pm=pm,bs=bs,tm=tm,fxprev=fxprev,fx=fx,now=now,teams=teams,
                totals=totals,prev=prev,derived=derived)


@pytest.mark.parametrize("minute_flag", [False, True])
def test_production_main_and_engine_parity(frozen, monkeypatch, minute_flag):
    monkeypatch.setattr(M,"SUB_GIVEN_NO_START",minute_flag,raising=False)
    f=frozen
    # Production path: original file readers, stage serialization, actual main.
    minutes=M.build(f['pm'],f['bs'],M.league_rates(f['pm']))
    priors,ha=T.build_priors(f['now'])
    ratings=T.fit_current(f['tm'],priors,ha)
    proj=T.project_fixtures(ratings)
    proj[['xg_for','xg_against']]=proj[['xg_for','xg_against']].round(3)
    for name,df in [('minutes',minutes),('team_ratings',ratings),('fixture_projections',proj)]:
        df.to_csv(f['derived']/f'{name}.csv',index=False)
    E.main()  # only writes to the test's temporary directory
    production=pd.read_csv(f['derived']/'expected_points.csv')
    # Evaluation path: all inputs injected, no production files written/read.
    prior=T.fit_prior_from_last_season(f['fxprev'],f['teams'])
    priors2,ha2=T.build_priors(f['now'],prior=prior)
    personal=E.last_season_priors(f['bs'],last_season=f['totals'])
    saved=M.LAST_SEASON_GWS
    via_engine,_=X.predict_frames(f['pm'],f['bs'],f['tm'],priors2,ha2,f['fx'],
        last_season=f['prev'],personal_priors=personal,
        prior_fixtures=f['fxprev'],season='2026-27')
    assert M.LAST_SEASON_GWS==saved
    cols=['element','fixture','xp','xp_attack','xp_bonus','xp_defence','xp_dc','exp_minutes']
    pd.testing.assert_frame_equal(production[cols].sort_values('element').reset_index(drop=True),
        via_engine[cols].sort_values('element').reset_index(drop=True),
        check_dtype=False,rtol=1e-11,atol=1e-11)
    assert len(production)==8
    assert production.xp_attack.max()>0
    assert production.xp_bonus.max()>0


def test_score_cases_use_fixed_tau_and_restore_on_failure(frozen):
    f=frozen
    prior=T.fit_prior_from_last_season(f['fxprev'],f['teams'])
    priors,ha=T.build_priors(f['now'],prior=prior)
    personal=E.last_season_priors(f['bs'],last_season=f['totals'])
    saved=E.BONUS_TAU_FIXED
    def fixed():
        E.BONUS_TAU_FIXED=8.
        return lambda:setattr(E,'BONUS_TAU_FIXED',saved)
    pred,diag=X.predict_frames(f['pm'],f['bs'],f['tm'],priors,ha,f['fx'],
        last_season=f['prev'],personal_priors=personal,
        prior_fixtures=f['fxprev'],season='2026-27',score_cases={'fixed8':fixed})
    assert E.BONUS_TAU_FIXED is saved
    assert diag['score_taus']['fixed8']==8.
    np.testing.assert_allclose(pred['xp__fixed8']-pred.xp,
        pred['bonus__fixed8']-pred.xp_bonus,rtol=1e-12,atol=1e-12)
    assert (pred['bonus__fixed8']-pred.xp_bonus).abs().max()>1e-3
    # Reusing minute/team stages must equal the independent full flag path.
    E.BONUS_TAU_FIXED=8.
    try:
        independent,_=X.predict_frames(f['pm'],f['bs'],f['tm'],priors,ha,f['fx'],
            last_season=f['prev'],personal_priors=personal,
            prior_fixtures=f['fxprev'],season='2026-27')
    finally:
        E.BONUS_TAU_FIXED=saved
    pd.testing.assert_series_equal(pred.set_index('element')['xp__fixed8'].sort_index(),
        independent.set_index('element').xp.sort_index(),check_names=False)
    def bad():
        E.BONUS_TAU_FIXED=0.
        return lambda:setattr(E,'BONUS_TAU_FIXED',saved)
    with pytest.raises(Exception):
        with np.errstate(all='raise'):
            X.predict_frames(f['pm'],f['bs'],f['tm'],priors,ha,f['fx'],
                last_season=f['prev'],personal_priors=personal,
                prior_fixtures=f['fxprev'],season='2026-27',score_cases={'bad':bad})
    assert E.BONUS_TAU_FIXED is saved


def test_keeper_rule_only_changes_keeper_goals(frozen):
    f=frozen
    mins=M.build(f['pm'],f['bs'],M.league_rates(f['pm']))
    rates=E.per90_rates(f['pm'][f['pm'].minutes>0],mins,f['bs'])
    rates['dc_rate']=0.
    priors,ha=T.build_priors(f['now']);ratings=T.fit_current(f['tm'],priors,ha)
    proj=T.project_fixtures(ratings)
    def predict(season,config=None):
        return E.expected_points(rates,ratings,proj,4.,1.,50.,season=season,
            game_config=config).sort_values('element').reset_index(drop=True)
    old=predict('2025-26');new=predict('2026-27')
    for season in ['2022-23','2023-24','2024-25','2025-26']:
        pd.testing.assert_frame_equal(old,predict(season))
    for _,r in rates.iterrows():
        scale=float(proj[proj.team==r.team].xg_for.iloc[0])/float(ratings[ratings.short_name==r.team].xg_vs_avg.iloc[0])
        delta=4*r.expected_goals90*r.exp_minutes/90*scale if r.pos=='GK' else 0.
        i=int(np.where(new.element.to_numpy()==r.element)[0][0])
        assert new.xp.iloc[i]-old.xp.iloc[i]==pytest.approx(delta,abs=1e-12)
        assert new.xp_attack.iloc[i]-old.xp_attack.iloc[i]==pytest.approx(delta,abs=1e-12)
    for col in ['xp_bonus','xp_dc','xp_defence','exp_minutes']:
        np.testing.assert_array_equal(old[col],new[col])
    # API only overrides keeper scoring, never changes other position rules.
    config={'scoring':{'goals_scored':{'GKP':10,'MID':999}}}
    pd.testing.assert_frame_equal(new,predict('2026-27',config))
    pd.testing.assert_frame_equal(old,predict('2025-26',config))


def test_minute_frame_input_matches_file_and_is_not_modified(frozen):
    f=frozen
    saved=M.LAST_SEASON_GWS
    before=f['prev'].copy(deep=True)
    via_file=M.last_season_minutes(f['bs'])
    via_frame=M.last_season_minutes(f['bs'],last_season=f['prev'])
    pd.testing.assert_frame_equal(via_file,via_frame)
    pd.testing.assert_frame_equal(before,f['prev'])
    assert M.LAST_SEASON_GWS is saved


def test_fixture_namespaces_and_four_round_blocks():
    raw=pd.Series([1,2,380])
    assert set(X.fixture_ids('2024-25',raw)).isdisjoint(X.fixture_ids('2025-26',raw))
    delta=np.array([1.,1.,1.,1.,3.,3.,3.,3.])
    gw=np.arange(8,16);season=np.repeat('2025-26',8)
    mu,se,n=P.block_effect(delta,season,gw)
    assert (mu,n)==(2.,2)
    assert se==pytest.approx(1.)
    assert P.block_effect(delta[:-1],season[:-1],gw[:-1])[1]==pytest.approx(48/49)
    # Duplicating player observations must not manufacture precision.
    assert P.block_effect(np.repeat(delta,5),np.repeat(season,5),np.repeat(gw,5))[1]==pytest.approx(se)
    _,_,n=P.block_effect(np.tile(delta,2),np.repeat(['2024-25','2025-26'],8),np.tile(gw,2))
    assert n==4


def test_compare_uses_production_flags_and_restores_on_failure(monkeypatch):
    # Exercise the public configuration/strict pairing contract without a season run.
    monkeypatch.setattr(P,'load_season',lambda season:pd.DataFrame())
    original=E.SHRINK_MINUTES
    def fake_walk(*args,**kwargs):
        return pd.DataFrame(dict(element=[1],gw=[8],fixture=[2025000001],name=['A'],pos=['MID'],
            value=[50],actual=[2],actual_bonus=[0],mins=[90],b_form=[1],xp=[E.SHRINK_MINUTES],xp_bonus=[0]))
    monkeypatch.setattr(P,'walk_forward',fake_walk)
    def config():
        E.SHRINK_MINUTES=700.
        return lambda:setattr(E,'SHRINK_MINUTES',original)
    p=P.compare({'base':lambda:None,'candidate':config},seasons=['2025-26'])
    assert p['xp__base'].iloc[0]==original and p['xp__candidate'].iloc[0]==700.
    assert E.SHRINK_MINUTES==original
    def bad_pair(*args,**kwargs):
        frame=fake_walk()
        if E.SHRINK_MINUTES==700.:frame['actual']=3
        return frame
    monkeypatch.setattr(P,'walk_forward',bad_pair)
    with pytest.raises(RuntimeError,match='ikke parvis'):
        P.compare({'base':lambda:None,'candidate':config},seasons=['2025-26'])
    assert E.SHRINK_MINUTES==original
    def fail(*args,**kwargs):raise RuntimeError('failed')
    monkeypatch.setattr(P,'walk_forward',fail)
    with pytest.raises(RuntimeError):P.compare({'candidate':config},seasons=['2025-26'])
    assert E.SHRINK_MINUTES==original
