#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 16:26:11 2023

@author: timyouellservian
"""

import requests
import pandas as pd
from fpl_utils.fpl_api_collection import (
    get_player_url_list, get_fixture_data, get_bootstrap_data, get_current_gw,
    get_current_season, remove_moved_players
)
from concurrent.futures import ThreadPoolExecutor
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor

t_cols = ['id', 'name', 'strength', 'strength_overall_home',
          'strength_overall_away', 'strength_attack_home',
          'strength_attack_away', 'strength_defence_home',
          'strength_defence_away']

team_cols = ['id', 'team', 'team_str', 'team_str_h', 'team_str_a',
             'team_str_att_h', 'team_str_att_a', 'team_str_def_h',
             'team_str_def_a']

oppo_cols = ['opponent_team', 'oppo_name', 'oppo_str', 'oppo_str_h',
             'oppo_str_a', 'oppo_str_att_h', 'oppo_str_att_a',
             'oppo_str_def_h', 'oppo_str_def_a']

fixt_cols = ['fixture', 'team_h_difficulty', 'team_a_difficulty']

ele_cols = ['element', 'name', 'position', 'team']

renamed_cols = {'total_points': 'points_fpf',
                'minutes': 'mins_fpf',
                'goals_scored': 'goals_fpf',
                'assists': 'assists_fpf',
                'clean_sheets': 'cs_fpf',
                'goals_conceded': 'gc_fpf',
                'own_goals': 'og_fpf',
                'penalties_saved': 'ps_fpf',
                'penalties_missed': 'pm_fpf',
                'yellow_cards': 'yc_fpf',
                'red_cards': 'rc_fpf',
                'saves': 'saves_fpf',
                'bonus': 'bonus_fpf',
                'bps': 'bps_fpf',
                'influence': 'i_fpf',
                'creativity': 'c_fpf',
                'threat': 't_fpf',
                'ict_index': 'ict_fpf',
                'starts': 'start_fpf',
                'expected_goals': 'xG_fpf',
                'expected_assists': 'xA_fpf',
                'expected_goal_involvements': 'xGI_fpf',
                'expected_goals_conceded': 'xGC_fpf'}

cols_to_tf = ['points_fpf', 'mins_fpf', 'goals_fpf', 'assists_fpf', 'cs_fpf',
              'gc_fpf', 'og_fpf', 'ps_fpf', 'pm_fpf', 'yc_fpf', 'rc_fpf',
              'saves_fpf', 'bonus_fpf', 'bps_fpf', 'i_fpf', 'c_fpf', 't_fpf',
              'ict_fpf', 'start_fpf', 'xG_fpf', 'xA_fpf', 'xGI_fpf', 'xGC_fpf']

str_cols = ['position', 'team', 'oppo_name', 'was_home', 'season']

x_keys = ['assists_fpf', 'bonus_fpf', 'bps_fpf', 'cs_fpf', 'c_fpf', 'xA_fpf',
          'xGI_fpf', 'xG_fpf', 'xGC_fpf', 'gc_fpf', 'goals_fpf', 'ict_fpf',
          'i_fpf', 'mins_fpf', 'og_fpf', 'pm_fpf', 'ps_fpf', 'rc_fpf',
          'saves_fpf', 'start_fpf', 't_fpf', 'points_fpf',
          'transfers_balance', 'transfers_in',
          'transfers_out', 'value', 'yc_fpf', 'team_str', 'team_str_h',
          'team_str_a', 'team_str_att_h', 'team_str_att_a', 'team_str_def_h',
          'team_str_def_a', 'oppo_str', 'oppo_str_h', 'oppo_str_a',
          'oppo_str_att_h', 'oppo_str_att_a', 'oppo_str_def_h',
          'oppo_str_def_a', 'oppo_difficulty', 'position_DEF', 'position_FWD',
          'position_GKP', 'position_MID', 'team_Arsenal',
          'team_Aston Villa', 'team_Bournemouth', 'team_Brentford',
          'team_Brighton', 'team_Burnley', 'team_Chelsea',
          'team_Crystal Palace', 'team_Everton', 'team_Fulham', 'team_Leeds',
          'team_Leicester', 'team_Liverpool', 'team_Luton', 'team_Man City',
          'team_Man Utd', 'team_Newcastle', "team_Nott'm Forest",
          'team_Sheffield Utd', 'team_Southampton', 'team_Spurs',
          'team_West Ham', 'team_Wolves', 'oppo_name_Arsenal',
          'oppo_name_Aston Villa', 'oppo_name_Bournemouth',
          'oppo_name_Brentford', 'oppo_name_Brighton', 'oppo_name_Burnley',
          'oppo_name_Chelsea', 'oppo_name_Crystal Palace', 'oppo_name_Everton',
          'oppo_name_Fulham', 'oppo_name_Leeds', 'oppo_name_Leicester',
          'oppo_name_Liverpool', 'oppo_name_Luton', 'oppo_name_Man City',
          'oppo_name_Man Utd', 'oppo_name_Newcastle',
          "oppo_name_Nott'm Forest", 'oppo_name_Sheffield Utd',
          'oppo_name_Southampton', 'oppo_name_Spurs', 'oppo_name_West Ham',
          'oppo_name_Wolves', 'was_home_False', 'was_home_True',
          'season_2022/23', 'season_2023/24']

new_ele_cols = ['element', 'name', 'position', 'team', 'now_cost',
                'transfers_in_event', 'transfers_out_event']

new_fixt_cols = ['fixture', 'GW', 'team_h', 'team_a', 'team_h_difficulty',
                 'team_a_difficulty']

fut_cols = ['element', 'name', 'fixture', 'id', 'opponent_team', 'GW', 'value']

base_url = 'https://fantasy.premierleague.com/api/'

init_file = './data/2022_23_'
data_22_23 = pd.read_csv(init_file + 'merged_gw.csv')
teams_22_23 = pd.read_csv(init_file + 'teams.csv')
fixts_22_23 = pd.read_csv(init_file + 'fixtures.csv')

hist_df = data_22_23.copy()

ele_df = remove_moved_players(pd.DataFrame(get_bootstrap_data()['elements']))
teams_df = pd.DataFrame(get_bootstrap_data()['teams'])
ele_types_df = pd.DataFrame(get_bootstrap_data()['element_types'])
fixt_df = pd.DataFrame(get_fixture_data())
fixt_df.rename(columns={'id': 'fixture'}, inplace=True)

crnt_gw = get_current_gw()

def call_api(endpoint):
    resp = requests.get(endpoint)
    data = resp.json()
    df = pd.DataFrame(data['history'])
    return df


def get_curr_season_hist_data():
    player_endpoints = get_player_url_list()
    with ThreadPoolExecutor(max_workers=100) as executor:
        res = executor.map(call_api, player_endpoints)
    hist_df = pd.concat(res)
    return hist_df


def get_current_season_df():
    a_curr_df = get_curr_season_hist_data()
    ele_copy = ele_df.copy()
    ele_copy.rename(columns={'id': 'element'}, inplace=True)
    ele_copy['name'] = ele_copy['first_name'] + ' ' + ele_copy['second_name']
    ele_copy['position'] = ele_df['element_type'].map(
        ele_types_df.set_index('id')['singular_name_short'])
    ele_cut = ele_copy[ele_cols]
    merge_df = a_curr_df.merge(ele_cut, on='element', how='left')
    merge_df['GW'] = merge_df['round']
    fixt_cut = fixt_df[fixt_cols]
    team_cut = teams_df[t_cols]
    oppo_cut = teams_df[t_cols]
    team_cut.columns = team_cols
    oppo_cut.columns = oppo_cols
    merge_df.rename(columns={'team': 'id'}, inplace=True)
    curr_teams_df = merge_df.merge(team_cut, on ='id', how='left')
    curr_df = curr_teams_df.merge(oppo_cut, on='opponent_team', how='left')
    curr_df = curr_df.merge(fixt_cut, on='fixture', how='left')
    curr_df['season'] = '2023/24'
    return curr_df


def get_historic_season_df():
    fixts_22_23.rename(columns={'id': 'fixture'}, inplace=True)
    fixt_22_23_cut = fixts_22_23[fixt_cols]
    team_22_23_cut = teams_22_23[t_cols]
    oppo_22_23_cut = teams_22_23[t_cols]
    team_22_23_cut.columns = team_cols
    oppo_22_23_cut.columns = oppo_cols
    hist_copy = hist_df.copy()
    hist_copy.drop('xP', axis=1, inplace=True)
    hist_t_df = hist_copy.merge(team_22_23_cut, on ='team', how='left')
    hist_t_df = hist_t_df.merge(oppo_22_23_cut, on='opponent_team', how='left')
    hist_t_df = hist_t_df.merge(fixt_22_23_cut, on='fixture', how='left')
    hist_t_df['season'] = '2022/23'
    return hist_t_df


def get_total_df():
    curr_df = get_current_season_df()
    hist_df = get_historic_season_df()
    
    total_df = pd.concat([hist_df, curr_df])
    total_df['p_id'] = total_df['season'] + '_' + total_df['element'].astype(str)
    total_df.sort_values(['p_id', 'fixture'], ascending=True, inplace=True)
    total_df['points'] = total_df['total_points']
    total_df.rename(columns=renamed_cols, inplace=True)
    
    total_df[cols_to_tf] = total_df.groupby('p_id')[cols_to_tf].shift(1)
    total_cut = total_df.loc[total_df['points_fpf'].notnull()]
    total_cut.reset_index(inplace=True)
    t_cut = total_cut.copy()
    t_cut.loc[t_cut['was_home'] == True,
              'oppo_difficulty'] = t_cut['team_h_difficulty']
    t_cut.loc[t_cut['was_home'] == False,
              'oppo_difficulty'] = t_cut['team_a_difficulty']
    t_cut['position'].replace('GK', 'GKP', inplace=True)
    t_cut.set_index('index', inplace=True)
    dummy_df = pd.get_dummies(t_cut, columns=str_cols)
    return dummy_df


def define_model(df):
    y_key = 'points'
    train, test = train_test_split(df, test_size=0.3, shuffle=True)
    
    y_train = train[y_key].values.reshape(-1,1)
    y_test = test[y_key].values.reshape(-1,1)
    
    X_train = train[x_keys]
    X_test = test[x_keys]
    
    reg = GradientBoostingRegressor(random_state=0)
    reg.fit(X_train, y_train)
    
    reg.predict(X_test)
    print(reg.score(X_test, y_test))
    return reg



df = get_total_df()
model = define_model(df)


def get_future_df():
    curr_df = get_current_season_df()
    fixt_copy = fixt_df.copy()
    ele_copy = ele_df.copy()
    mr_fixt_df = curr_df.sort_values('kickoff_time', ascending=False) \
        .groupby('element').head(1)
    mr_fixt_df.rename(columns=renamed_cols, inplace=True)
    mr_fixt_row = mr_fixt_df[['element'] + cols_to_tf]
    fixt_cut = fixt_copy.loc[fixt_copy['event'] >= crnt_gw]
    team_id_list = teams_df['id'].tolist()
    total_fixts_df_list = []
    for team in team_id_list:
        team_fixt_list = fixt_cut.loc[(fixt_cut['team_h'] == team) |
                                      (fixt_cut['team_a'] == team)]['fixture']
        team_fixt_df = pd.DataFrame({'team': team, 'fixture': team_fixt_list})
        total_fixts_df_list.append(team_fixt_df)
    fixts_by_team = pd.concat(total_fixts_df_list)
    ele_copy.rename(columns={'id': 'element'}, inplace=True)
    ele_copy['name'] = ele_copy['first_name'] + ' ' + ele_copy['second_name']
    ele_copy['position'] = ele_df['element_type'].map(
        ele_types_df.set_index('id')['singular_name_short'])
    ele_cut = ele_copy[new_ele_cols]
    e_cut = ele_cut.copy()
    ele_renames = {'now_cost': 'value', 'transfers_in_event': 'transfers_in',
                   'transfers_out_event': 'transfers_out'}
    e_cut.rename(columns=ele_renames, inplace=True)
    e_cut['transfers_balance'] = e_cut['transfers_in'] - e_cut['transfers_out']
    ele_merge = e_cut.merge(fixts_by_team, on='team', how='left')
    fixt_copy.rename(columns={'event': 'GW'}, inplace=True)
    fixt_cut = fixt_copy[new_fixt_cols]
    ele_merge_fixt_df = ele_merge.merge(fixt_cut, on='fixture', how='left')
    ele_merge_fixt_df.rename(columns={'team': 'id'}, inplace=True)
    
    ele_merge_fixt_df.loc[ele_merge_fixt_df['team_h'] == ele_merge_fixt_df['id'], 'was_home'] = True
    ele_merge_fixt_df.loc[ele_merge_fixt_df['team_a'] == ele_merge_fixt_df['id'], 'was_home'] = False
    
    ele_merge_fixt_df.loc[ele_merge_fixt_df['was_home'] == True, 'opponent_team'] = ele_merge_fixt_df['team_a']
    ele_merge_fixt_df.loc[ele_merge_fixt_df['was_home'] == False, 'opponent_team'] = ele_merge_fixt_df['team_h']
    
    ele_merge_fixt_df.loc[ele_merge_fixt_df['was_home'] == True, 'oppo_difficulty'] = ele_merge_fixt_df['team_h_difficulty']
    ele_merge_fixt_df.loc[ele_merge_fixt_df['was_home'] == False, 'oppo_difficulty'] = ele_merge_fixt_df['team_a_difficulty']
    
    team_cut = teams_df[t_cols]
    oppo_cut = teams_df[t_cols]
    team_cut.columns = team_cols
    oppo_cut.columns = oppo_cols
    
    
    ele_teams_df = ele_merge_fixt_df.merge(team_cut, on ='id', how='left')
    ele_teams_df = ele_teams_df.merge(oppo_cut, on='opponent_team', how='left')
    ele_teams_df['season'] = get_current_season()
    
    fut_df = ele_teams_df.merge(mr_fixt_row, on='element', how='left')
    
    fut_dummy_df = pd.get_dummies(fut_df, columns=str_cols)
    
    cols_to_add = ['team_Leeds', 'team_Leicester', 'team_Southampton',
                   'oppo_name_Leeds', 'oppo_name_Leicester',
                   'oppo_name_Southampton', 'season_2022/23']
    
    data_to_add = pd.DataFrame(0, index=fut_dummy_df.index, columns=cols_to_add)
    
    
    full_fut_df = pd.concat([fut_dummy_df, data_to_add], axis=1)
    return full_fut_df


fut_df = get_future_df()

X_future = fut_df[x_keys]
future_cut = fut_df[fut_cols]
future_preds = model.predict(X_future).round(1)
future_preds = pd.DataFrame({'xP': future_preds})
future_total = pd.concat([future_cut.reset_index(drop=True),
                          future_preds.reset_index(drop=True)], axis=1)

preds = future_total[['element', 'GW', 'xP']].groupby(['element', 'GW']).sum().reset_index()

preds.to_csv('./data/2023_24_pred_file.csv', index=False)


# need to transform data so it can be run through a model - ChatGPT
# randomise bottom all - most recent gw and use that as the private_test set.
# Build a training and testing pipeline to keep train and test separate - like what Will built at Aviva
# need to build some CI/CD so this happens either automatically or I can simply
# re-train a model, analyse and then upload via a pickle file to GitHub, using the model to predict each GW