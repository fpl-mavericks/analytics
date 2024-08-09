#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  9 13:56:08 2023

@author: timyouell
"""

import pandas as pd
from fpl_utils.fpl_api_collection import (
    get_player_url_list, get_fixture_data, get_bootstrap_data
)
from concurrent.futures import ThreadPoolExecutor
from sklearn.model_selection import train_test_split
import requests

base_url = 'https://fantasy.premierleague.com/api/'


def call_api(endpoint):
    resp = requests.get(endpoint)
    data = resp.json()
    df = pd.DataFrame(data['history'])
    return df

def get_curr_season_hist_data():
    player_endpoints = get_player_url_list()[:10]
    with ThreadPoolExecutor(max_workers=100) as executor:
        res = executor.map(call_api, player_endpoints)
    hist_df = pd.concat(res)
    return hist_df
    

hist_df = get_curr_season_hist_data()

# shift data down
cols_list = ['minutes', 'goals_scored', 'assists', 'goals_conceded', 'saves',
             'bonus', 'bps', 'influence', 'creativity', 'threat', 'ict_index',
             'yellow_cards', 'red_cards', 'total_points', 'expected_goals',
             'expected_assists', 'expected_goal_involvements', 'expected_goals_conceded'] #, 'team_goals', 'team_conceded']

for col in cols_list:
    new_col = 'player_' + str(col) + '_FPGW'
    hist_df[new_col] = hist_df[col].astype(float).shift(1)
    

fixt_df = pd.DataFrame(get_fixture_data())
fixt_df.rename(columns={'id': 'fixture'}, inplace=True)
drop_cols = ['kickoff_time', 'team_h_score', 'team_a_score', 'minutes']
fixt_df.drop(drop_cols, axis=1, inplace=True)

teams_df = pd.DataFrame(get_bootstrap_data()['teams'])
teams_df.rename(columns={'id': 'opponent_team'}, inplace=True)


hist_fixt_merge = hist_df.merge(fixt_df, how='left', on='fixture')
hist_fixt_teams_merge = hist_fixt_merge.merge(teams_df, how='left', on='opponent_team')



fpgw_list = [col for col in hist_df.columns if '_FPGW' in col]
model_cols = ['was_home', 'short_name', 'strength', 'strength_overall_home',
              'strength_overall_away', 'strength_attack_home',
              'strength_attack_away', 'strength_defence_home',
              'strength_defence_away']
y_key = 'total_points'
nonmodel_cols = ['element', 'fixture', 'opponent_team', 'round']
x_cols = fpgw_list + model_cols

df_all = hist_fixt_teams_merge[[y_key] + nonmodel_cols + x_cols]

def train_xgb_regr(df, y_key, nonmodel_vars):
    train, test = train_test_split(df, test_size=0.25, shuffle=True) 
    
    train_out = train[nonmodel_vars]
    test_out = test[nonmodel_vars]
    train.drop(nonmodel_vars, axis=1, inplace=True)
    test.drop(nonmodel_vars, axis=1, inplace=True)
    X_train = train
    Y_train = train_out[y_key]
    X_test = test
    Y_test = test_out[y_key]
    xgb_regr = XGBRegressor(n_estimators=500,
                            learning_rate=0.01,
                            max_depth=5,
                            min_samples_leaf=5)
    xgb_regr.fit(X_train, Y_train)
    preds = xgb_regr.predict(X_test)
    preds_df = pd.DataFrame({'actual': Y_test, 'preds': preds})
    preds_df['preds'] = round(preds_df['preds'])
    print('R2_Score: ' + str(r2_score(preds_df['actual'], preds_df['preds'])))
    print('MAE: ' + str(mean_absolute_error(preds_df['actual'], preds_df['preds'])))
    sns.regplot(preds_df['actual'], preds_df['preds'])
    plt.title('R^2 Score: ' + str(r2_score(preds_df['actual'], preds_df['preds'])))
    return xgb_regr


xgb_regr = train_xgb_regr(df, y_key, nonmodel_vars)


def get_fixtures_data():
    fixtures_url = base_url + '/fixtures/'
    resp = requests.get(fixtures_url)
    data = resp.json()
    fixtures_df = pd.DataFrame(data)
    gw_dict = dict(zip(np.arange(1, 381),
                       [num for num in np.arange(1, 39) for x in range(10)]))
    fixtures_df.loc[fixtures_df['event'].isnull(),
                    'event2'] = fixtures_df['id'].map(gw_dict)
    fixtures_df['event2'].fillna(fixtures_df['event'], inplace=True)
    fixtures_df.loc[fixtures_df['event'].isnull(), 'blank'] = True
    fixtures_df['blank'].fillna(False, inplace=True)
    fixtures_df.sort_values('event2', ascending=True, inplace=True)
    return fixtures_df


hist_df = get_curr_season_hist_data()


def transform_fixt_data(fixt_df):
    # remove event = nan
    cut_df = fixt_df.loc[fixt_df['event'] >= 1]
    # event = gw
    # gw_dict = cut_df.set_index('id')['event'].astype(int).to_dict()
    
    return cut_df
    

cut_cols = ['total_points', 'round', 'fixture', 'was_home',
            'player_minutes_FPGW', 'total_minutes_FPGW', 'player_goals_scored_FPGW',
            'total_goals_scored_FPGW', 'player_assists_FPGW',
            'total_assists_FPGW', 'player_goals_conceded_FPGW',
            'total_goals_conceded_FPGW', 'player_saves_FPGW',
            'total_saves_FPGW', 'player_bonus_FPGW', 'total_bonus_FPGW',
            'player_bps_FPGW', 'total_bps_FPGW', 'player_influence_FPGW',
            'total_influence_FPGW', 'player_creativity_FPGW',
            'total_creativity_FPGW', 'player_threat_FPGW', 'total_threat_FPGW',
            'player_ict_index_FPGW', 'total_ict_index_FPGW',
            'player_yellow_cards_FPGW', 'total_yellow_cards_FPGW',
            'player_red_cards_FPGW', 'total_red_cards_FPGW',
            'player_team_goals_FPGW', 'total_team_goals_FPGW',
            'player_team_conceded_FPGW', 'total_team_conceded_FPGW',
            'player_total_points_FPGW', 'total_total_points_FPGW', 'player',
            'team_full', 'opponent_full', 'position', 'value', 'element',
            'player_value_FPGW']

cut_df = hist_df[cut_cols]
