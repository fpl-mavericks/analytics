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
from sklearn.ensemble import GradientBoostingRegressor
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
    xgb_regr = GradientBoostingRegressor(n_estimators=500,
                            learning_rate=0.01,
                            max_depth=5,
                            min_samples_leaf=5)
    xgb_regr.fit(X_train, Y_train)
    preds = xgb_regr.predict(X_test)
    preds_df = pd.DataFrame({'actual': Y_test, 'preds': preds})
    preds_df['preds'] = round(preds_df['preds'])
    return preds_df
