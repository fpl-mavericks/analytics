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
    get_current_season, remove_moved_players, get_player_id_dict
)
from concurrent.futures import ThreadPoolExecutor
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor

str_cols = ['id', 'name', 'strength', 'strength_overall_home',
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

renamed_cols = {'total_points': 'points',
                'minutes': 'mins',
                'goals_scored': 'goals',
                'assists': 'assists',
                'clean_sheets': 'cs',
                'goals_conceded': 'gc',
                'own_goals': 'og',
                'penalties_saved': 'ps',
                'penalties_missed': 'pm',
                'yellow_cards': 'yc',
                'red_cards': 'rc',
                'influence': 'i',
                'creativity': 'c',
                'threat': 't',
                'ict_index': 'ict',
                'starts': 'starts',
                'expected_goals': 'xG',
                'expected_assists': 'xA',
                'expected_goal_involvements': 'xGI',
                'expected_goals_conceded': 'xGC'}

string_cols = ['position', 'team', 'oppo_name', 'was_home', 'season']

x_keys = ['assists_fpf', 'bps_fpf', 'cs_fpf', 'c_fpf', 'xA_fpf', 'xGI_fpf',
          'xG_fpf', 'xGC_fpf', 'gc_fpf', 'goals_fpf', 'ict_fpf',
          'i_fpf', 'mins_fpf', 'og_fpf', 'pm_fpf', 'ps_fpf', 'rc_fpf',
          'saves_fpf', 't_fpf', 'points_fpf', 'prop_mins_fpf', 'ave_points_fpf', 'ave_assists_fpf',
          'ave_goals_fpf', 'ave_cs_fpf','ave_xA_fpf', 'ave_xGI_fpf',
          'ave_xG_fpf', 'ave_bps_fpf','ave_xGC_fpf', 'ave_i_fpf', 'ave_c_fpf',
          'ave_t_fpf', 'ave_ict_fpf','ave_saves_fpf', 'ave_ps_fpf',
          'ave_yc_fpf', 'ave_rc_fpf', 'ave_team_goals_fpf', 'ave_team_xG_fpf',
          'ave_team_xA_fpf', 'transfers_balance', 'transfers_in', 'transfers_out',
          
          'team_str', 'team_str_h', 'team_str_a', 'team_str_att_h',
'team_str_att_a', 'team_str_def_h', 'team_str_def_a', 'oppo_str',
'oppo_str_h', 'oppo_str_a', 'oppo_str_att_h', 'oppo_str_att_a',
'oppo_str_def_h', 'oppo_str_def_a', 'oppo_difficulty',
'position_DEF', 'position_FWD', 'position_GKP', 'position_MID',
'team_Arsenal', 'team_Aston Villa', 'team_Bournemouth',
'team_Brentford', 'team_Brighton', 'team_Burnley', 'team_Chelsea',
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
    with ThreadPoolExecutor(max_workers=50) as executor:
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
    team_cut = teams_df[str_cols]
    oppo_cut = teams_df[str_cols]
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
    team_22_23_cut = teams_22_23[str_cols]
    oppo_22_23_cut = teams_22_23[str_cols]
    team_22_23_cut.columns = team_cols
    oppo_22_23_cut.columns = oppo_cols
    hist_copy = hist_df.copy()
    hist_copy.drop('xP', axis=1, inplace=True)
    hist_t_df = hist_copy.merge(team_22_23_cut, on ='team', how='left')
    hist_t_df = hist_t_df.merge(oppo_22_23_cut, on='opponent_team', how='left')
    hist_t_df = hist_t_df.merge(fixt_22_23_cut, on='fixture', how='left')
    hist_t_df['season'] = '2022/23'
    return hist_t_df

curr_df = get_current_season_df()
hist_df = get_historic_season_df()


def calculate_average_values(df, cols):
    for col in cols:
        df['ave_' + col] = df.groupby('p_id')[col].cumsum() / df['games_avail']
    return df


def get_total_df():
    total_df = pd.concat([hist_df, curr_df])
    total_df.rename(columns=renamed_cols, inplace=True)
    total_df['p_id'] = total_df['season'] + '_' + total_df['element'].astype(str)
    total_df.sort_values(['p_id', 'fixture'], ascending=True, inplace=True)
    
    total_df['games_avail'] = (total_df.groupby('p_id').cumcount() + 1)
    total_df['prop_mins'] = total_df.groupby('p_id')['mins'].apply(lambda x: x.cumsum())/(total_df['games_avail']*90)
    
    cols_to_ave = ['points', 'assists', 'goals', 'cs', 'xA', 'xGI', 'xG',
                   'bps', 'xGC', 'i', 'c', 't', 'ict', 'saves', 'ps', 'yc',
                   'rc', 'mins']
    team_stat_cols = ['goals', 'xG', 'xA']
    team_stat_cols_extra = ['team_' + col for col in team_stat_cols]
    ave_team_stat_cols = ['ave_' + col for col in team_stat_cols_extra]
    ave_cols = ['ave_' + col for col in cols_to_ave]
    t_cols = cols_to_ave + ['gc' , 'og', 'pm', 'prop_mins']
    fpf_cols = [col + '_fpf' for col in (t_cols + ave_cols + ave_team_stat_cols)]
    total_df[t_cols] = total_df[t_cols].apply(pd.to_numeric)
    

    for col in team_stat_cols:
         total_df['team_' + col] = total_df.groupby(['team', 'fixture'])[col].transform('sum')
     
    total_df = calculate_average_values(total_df, cols_to_ave + team_stat_cols_extra)

    fpf_rename_cols = dict(zip((t_cols + ave_cols + ave_team_stat_cols), fpf_cols))
    total_df.rename(columns=fpf_rename_cols, inplace=True)
    total_df['points'] = total_df['points_fpf']
    total_df[fpf_cols] = total_df.groupby('p_id')[fpf_cols].shift(1)
    total_cut = total_df.loc[total_df['points_fpf'].notnull()]
    total_cut.reset_index(inplace=True)
    t_cut = total_cut.copy()
    t_cut.loc[t_cut['was_home'] == True,
              'oppo_difficulty'] = t_cut['team_h_difficulty']
    t_cut.loc[t_cut['was_home'] == False,
              'oppo_difficulty'] = t_cut['team_a_difficulty']
    t_cut['position'].replace('GK', 'GKP', inplace=True)
    t_cut.set_index('index', inplace=True)
    dummy_df = pd.get_dummies(t_cut, columns=string_cols)
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
    curr_cut = curr_df.copy()
    fixt_copy = fixt_df.copy()
    ele_copy = ele_df.copy()
    
    curr_cut.rename(columns=renamed_cols, inplace=True)
    curr_cut['p_id'] = curr_cut['season'] + '_' + curr_cut['element'].astype(str)
    curr_cut.sort_values(['p_id', 'fixture'], ascending=True, inplace=True)
    
    curr_cut['games_avail'] = (curr_cut.groupby('p_id').cumcount() + 1)
    curr_cut['prop_mins'] = curr_cut.groupby('p_id')['mins'].apply(lambda x: x.cumsum())/(curr_cut['games_avail']*90)
    
    cols_to_ave = ['points', 'assists', 'goals', 'cs', 'xA', 'xGI', 'xG',
                   'bps', 'xGC', 'i', 'c', 't', 'ict', 'saves', 'ps', 'yc',
                   'rc', 'mins']
    team_stat_cols = ['goals', 'xG', 'xA']
    team_stat_cols_extra = ['team_' + col for col in team_stat_cols]
    ave_team_stat_cols = ['ave_' + col for col in team_stat_cols_extra]
    ave_cols = ['ave_' + col for col in cols_to_ave]
    t_cols = cols_to_ave + ['gc' , 'og', 'pm', 'prop_mins']
    fpf_cols = [col + '_fpf' for col in (t_cols + ave_cols + ave_team_stat_cols)]
    curr_cut[t_cols] = curr_cut[t_cols].apply(pd.to_numeric)
    
    for col in team_stat_cols:
        curr_cut['team_' + col] = curr_cut.groupby(['team', 'fixture'])[col].transform('sum')
    
    curr_cut = calculate_average_values(curr_cut, cols_to_ave + team_stat_cols_extra)

    fpf_rename_cols = dict(zip((t_cols + ave_cols + ave_team_stat_cols), fpf_cols))
    curr_cut.rename(columns=fpf_rename_cols, inplace=True)
    curr_cut['points'] = curr_cut['points_fpf']
    curr_cut[fpf_cols] = curr_cut.groupby('p_id')[fpf_cols].shift(1)
    
    mr_fixt_df = curr_cut.sort_values('kickoff_time', ascending=False) \
        .groupby('element').head(1)
    # mr_fixt_df.rename(columns=renamed_cols, inplace=True)
    mr_fixt_row = mr_fixt_df[['element'] + fpf_cols]
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
    
    team_cut = teams_df[str_cols]
    oppo_cut = teams_df[str_cols]
    team_cut.columns = team_cols
    oppo_cut.columns = oppo_cols
    
    
    ele_teams_df = ele_merge_fixt_df.merge(team_cut, on ='id', how='left')
    ele_teams_df = ele_teams_df.merge(oppo_cut, on='opponent_team', how='left')
    ele_teams_df['season'] = get_current_season()
    
    fut_df = ele_teams_df.merge(mr_fixt_row, on='element', how='left')
    
    fut_dummy_df = pd.get_dummies(fut_df, columns=string_cols)
    
    cols_to_add = ['team_Leeds', 'team_Leicester', 'team_Southampton',
                   'oppo_name_Leeds', 'oppo_name_Leicester',
                   'oppo_name_Southampton', 'season_2022/23']
    
    data_to_add = pd.DataFrame(0, index=fut_dummy_df.index, columns=cols_to_add)
    
    
    full_fut_df = pd.concat([fut_dummy_df, data_to_add], axis=1)
    full_fut_df = full_fut_df.loc[full_fut_df['points_fpf'].notnull()]
    return full_fut_df


fut_df = get_future_df()

X_future = fut_df[x_keys]
future_cut = fut_df[fut_cols]
future_preds = model.predict(X_future).round(1)
future_preds = pd.DataFrame({'xP': future_preds})
future_total = pd.concat([future_cut.reset_index(drop=True),
                          future_preds.reset_index(drop=True)], axis=1)

preds = future_total[['element', 'GW', 'xP']].groupby(['element', 'GW']).sum().reset_index()


df = preds.loc[preds['GW'] == crnt_gw]
player_dict = get_player_id_dict(order_by_col='now_cost', web_name=False)
ele_df.rename(columns={'id': 'element'}, inplace=True)
ele_df['team'] = ele_df['team'].map(teams_df.set_index('id')['short_name'])
ele_df['Name'] = ele_df['element'].map(player_dict)
merge_df = ele_df.merge(df, on='element', how='left')[['Name', 'GW', 'xP']]


#preds.to_csv('./data/2023_24_pred_file.csv', index=False)
