#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 13:58:07 2022

@author: timyouellservian
"""

import pandas as pd
import requests
import time

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


# url_list = ['{}element-summary/{}/'.format(base_url, player_id) for 
#             player_id, player_name in id_dict.items()]
