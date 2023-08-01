#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 15:26:50 2022

@author: timyouell
"""

import pandas as pd
import requests


base_url = 'https://fantasy.premierleague.com/api/'


def get_bootstrap_data() -> dict:
    """
    Options
    -------
        ['element_stats']
        ['element_types']
        ['elements']
        ['events']
        ['game_settings']
        ['phases']
        ['teams']
        ['total_players']
    """
    resp = requests.get(f'{base_url}bootstrap-static/')
    if resp.status_code != 200:
        raise Exception(f'Response was status code {resp.status_code}')
    else:
        return resp.json()


def get_fixture_data() -> dict:
    resp = requests.get(f'{base_url}fixtures/')
    if resp.status_code != 200:
        raise Exception(f'Response was status code {resp.status_code}')
    else:
        return resp.json()


def get_player_data(player_id) -> dict:
    """
    Options
    -------
        ['fixtures']
        ['history']
        ['history_past']
    """
    resp = requests.get(f'{base_url}element-summary/{player_id}/')
    if resp.status_code != 200:
        raise Exception(f'Response was status code {resp.status_code}')
    else:
        return resp.json()


def get_manager_details(manager_id) -> dict:
    resp = requests.get(f'{base_url}entry/{manager_id}/')
    if resp.status_code != 200:
        raise Exception(f'Response was status code {resp.status_code}')
    else:
        return resp.json()


def get_manager_history_data(manager_id) -> dict:
    resp = requests.get(f'{base_url}entry/{manager_id}/history/')
    if resp.status_code != 200:
        raise Exception(f'Response was status code {resp.status_code}')
    else:
        return resp.json()


def get_manager_team_data(manager_id, gw):
    """
    Options
    -------
        ['active_chip']
        ['automatic_subs']
        ['entry_history']
        ['picks']
    """
    resp = requests.get(f'{base_url}entry/{manager_id}/event/{gw}/picks/')
    if resp.status_code != 200:
        raise Exception(f'Response was status code {resp.status_code}')
    return resp.json()


def get_total_fpl_players():
    return get_bootstrap_data()['total_players']

'''
ele_stats_data = get_bootstrap_data()['element_stats']
ele_types_data = get_bootstrap_data()['element_types']
ele_data = get_bootstrap_data()['elements']
events_data = get_bootstrap_data()['events']
game_settings_data = get_bootstrap_data()['game_settings']
phases_data = get_bootstrap_data()['phases']
teams_data = get_bootstrap_data()['teams']
total_managers = get_bootstrap_data()['total_players']


fixt = pd.DataFrame(get_fixture_data())

tester = get_manager_history_data(657832)

tester = get_manager_details(657832)

ele_df = pd.DataFrame(ele_data)

events_df = pd.DataFrame(events_data)

#keep only required cols


ele_cols = ['web_name', 'chance_of_playing_this_round', 'element_type',
            'event_points', 'form', 'now_cost', 'points_per_game',
            'selected_by_percent', 'team', 'total_points',
            'transfers_in_event', 'transfers_out_event', 'value_form',
            'value_season', 'minutes', 'goals_scored', 'assists',
            'clean_sheets', 'goals_conceded', 'own_goals', 'penalties_saved',
            'penalties_missed', 'yellow_cards', 'red_cards', 'saves', 'bonus',
            'bps', 'influence', 'creativity', 'threat', 'ict_index',
            'influence_rank', 'influence_rank_type', 'creativity_rank',
            'creativity_rank_type', 'threat_rank', 'threat_rank_type',
            'ict_index_rank', 'ict_index_rank_type', 'dreamteam_count']

ele_df = ele_df[ele_cols]

picks_df = get_manager_team_data(9, 4)
'''

# need to do an original data pull to get historic gw_data for every player_id
# shouldn't matter if new player_id's are added via tranfsers etc because it
# should just get added to the big dataset


# get player_id list

def get_player_id_dict(web_name=True) -> dict:
    ele_df = pd.DataFrame(get_bootstrap_data()['elements'])
    teams_df = pd.DataFrame(get_bootstrap_data()['teams'])
    ele_df['team_name'] = ele_df['team'].map(teams_df.set_index('id')['short_name'])
    if web_name == True:
        id_dict = dict(zip(ele_df['id'], ele_df['web_name']))
    else:
        ele_df['full_name'] = ele_df['first_name'] + ' ' + \
            ele_df['second_name'] + ' (' + ele_df['team_name'] + ')'
        id_dict = dict(zip(ele_df['id'], ele_df['full_name']))
    return id_dict


def collate_player_hist() -> pd.DataFrame():
    res = []
    p_dict = get_player_id_dict()
    for p_id, p_name in p_dict.items():
        resp = requests.get('{}element-summary/{}/'.format(base_url, p_id))
        if resp.status_code != 200:
            print('Request to {} data failed'.format(p_name))
            raise Exception(f'Response was status code {resp.status_code}')
        else:
            res.append(resp.json()['history'])
    return pd.DataFrame(res)


# Team, games_played, wins, losses, draws, goals_for, goals_against, GD,
# PTS, Form? [W,W,L,D,W]
def get_league_table():
    fixt_df = pd.DataFrame(get_fixture_data())
    teams_df = pd.DataFrame(get_bootstrap_data()['teams'])
    teams_id_list = teams_df['id'].unique().tolist()
    df_list = []
    for t_id in teams_id_list:
        home_data = fixt_df.copy().loc[fixt_df['team_h'] == t_id]
        away_data = fixt_df.copy().loc[fixt_df['team_a'] == t_id]
        home_data.loc[:, 'was_home'] = True
        away_data.loc[:, 'was_home'] = False
        df = pd.concat([home_data, away_data])
        # df = df.loc[df['finished'] == True]
        df.sort_values('event', inplace=True)
        df.loc[(df['was_home'] == True) &
               (df['team_h_score'] > df['team_a_score']), 'win'] = True
        df.loc[(df['was_home'] == False) &
               (df['team_a_score'] > df['team_h_score']), 'win'] = True
        df.loc[(df['team_h_score'] == df['team_a_score']), 'draw'] = True
        df.loc[(df['was_home'] == True) &
               (df['team_h_score'] < df['team_a_score']), 'loss'] = True
        df.loc[(df['was_home'] == False) &
               (df['team_a_score'] < df['team_h_score']), 'loss'] = True
        df.loc[(df['was_home'] == True), 'gf'] = df['team_h_score']
        df.loc[(df['was_home'] == False), 'gf'] = df['team_a_score']
        df.loc[(df['was_home'] == True), 'ga'] = df['team_a_score']
        df.loc[(df['was_home'] == False), 'ga'] = df['team_h_score']
        df.loc[(df['win'] == True), 'result'] = 'W'
        df.loc[(df['draw'] == True), 'result'] = 'D'
        df.loc[(df['loss'] == True), 'result'] = 'L'
        df.loc[(df['was_home'] == True) &
               (df['team_a_score'] == 0), 'clean_sheet'] = True
        df.loc[(df['was_home'] == False) &
               (df['team_h_score'] == 0), 'clean_sheet'] = True
        ws = len(df.loc[df['win'] == True])
        ds = len(df.loc[df['draw'] == True])
        l_data = {'id': [t_id], 'GP': [len(df)], 'W': [ws], 'D': [ds],
                  'L': [len(df.loc[df['loss'] == True])],
                  'GF': [df['gf'].sum()], 'GA': [df['ga'].sum()],
                  'GD': [df['gf'].sum() - df['ga'].sum()],
                  'CS': [df['clean_sheet'].sum()], 'Pts': [(ws*3) + ds],
                  'Form': [df['result'].tail(5).str.cat(sep='')]}
        df_list.append(pd.DataFrame(l_data))
    league_df = pd.concat(df_list)
    league_df.sort_values(['Pts', 'GD'], ascending=False, inplace=True)
    league_df['team'] = league_df['id'].map(teams_df.set_index('id')['short_name'])
    league_df.drop('id', axis=1, inplace=True)
    league_df.set_index('team', inplace=True)
    league_df['GF'] = league_df['GF'].astype(int)
    league_df['GA'] = league_df['GA'].astype(int)
    league_df['GD'] = league_df['GD'].astype(int)

    league_df['Pts/Game'] = (league_df['Pts']/league_df['GP']).round(2)
    league_df['GF/Game'] = (league_df['GF']/league_df['GP']).round(2)
    league_df['GA/Game'] = (league_df['GA']/league_df['GP']).round(2)
    league_df['CS/Game'] = (league_df['CS']/league_df['GP']).round(2)
    return league_df


def get_current_gw():
    events_df = pd.DataFrame(get_bootstrap_data()['events'])
    current_gw = events_df.loc[events_df['is_next'] == True].reset_index()['id'][0]
    return current_gw


def get_fixture_dfs():
    # doubles??
    fixt_df = pd.DataFrame(get_fixture_data())
    teams_df = pd.DataFrame(get_bootstrap_data()['teams'])
    teams_list = teams_df['short_name'].unique().tolist()
    # don't need to worry about double fixtures just yet!
    fixt_df['team_h'] = fixt_df['team_h'].map(teams_df.set_index('id')['short_name'])
    fixt_df['team_a'] = fixt_df['team_a'].map(teams_df.set_index('id')['short_name'])
    gw_dict = dict(zip(range(1,381),
                       [num for num in range(1, 39) for x in range(10)]))
    fixt_df['event_lock'] = fixt_df['id'].map(gw_dict)
    team_fdr_data = []
    team_fixt_data = []
    for team in teams_list:
        home_data = fixt_df.copy().loc[fixt_df['team_h'] == team]
        away_data = fixt_df.copy().loc[fixt_df['team_a'] == team]
        home_data.loc[:, 'was_home'] = True
        away_data.loc[:, 'was_home'] = False
        df = pd.concat([home_data, away_data])
        df.sort_values('event_lock', inplace=True)
        h_filt = (df['team_h'] == team) & (df['event'].notnull())
        a_filt = (df['team_a'] == team) & (df['event'].notnull())
        df.loc[h_filt, 'next'] = df['team_a'] + ' (H)'
        df.loc[a_filt, 'next'] = df['team_h'] + ' (A)'
        df.loc[df['event'].isnull(), 'next'] = 'BLANK'
        df.loc[h_filt, 'next_fdr'] = df['team_h_difficulty']
        df.loc[a_filt, 'next_fdr'] = df['team_a_difficulty']
        team_fixt_data.append(pd.DataFrame([team] + list(df['next'])).transpose())
        team_fdr_data.append(pd.DataFrame([team] + list(df['next_fdr'])).transpose())
    team_fdr_df = pd.concat(team_fdr_data).set_index(0)
    team_fixt_df = pd.concat(team_fixt_data).set_index(0)
    return team_fdr_df, team_fixt_df
