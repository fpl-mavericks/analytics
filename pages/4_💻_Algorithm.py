#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 20:20:45 2022

@author: timyouell
"""

import pandas as pd
import streamlit as st
from fpl_utils.fpl_api_collection import (
    get_bootstrap_data, get_current_gw, get_fixt_dfs, get_league_table,
    remove_moved_players, get_player_id_dict
)
from fpl_utils.fpl_utils import (
    define_sidebar
)

base_url = 'https://fantasy.premierleague.com/api/'

st.set_page_config(page_title='Algorithm', page_icon=':computer:', layout='wide')
define_sidebar()

st.title('Predicted Points Algorithm')
st.write('Gradient Boosting Regressor Algorithm trained on 22/23 historic data and 23/24 data so far.')

crnt_gw = get_current_gw()

preds_df = pd.read_csv('./data/2023_24_pred_file.csv')
preds_df.rename(columns={'xP': 'Pred_Pts'}, inplace=True)

ele_df = remove_moved_players(pd.DataFrame(get_bootstrap_data()['elements']))
ele_types_df = pd.DataFrame(get_bootstrap_data()['element_types'])
events_df = pd.DataFrame(get_bootstrap_data()['events'])
teams_df = pd.DataFrame(get_bootstrap_data()['teams'])


def get_home_away_str_dict():
    new_fdr_df.columns = new_fixt_cols
    result_dict = {}
    for col in new_fdr_df.columns:
        values = list(new_fdr_df[col])
        max_length = new_fixt_df[col].str.len().max()
        if max_length > 7:
            new_fixt_df.loc[new_fixt_df[col].str.len() <= 7, col] = new_fixt_df[col].str.pad(width=max_length+9, side='both', fillchar=' ')
        strings = list(new_fixt_df[col])
        value_dict = {}
        for value, string in zip(values, strings):
            if value not in value_dict:
                value_dict[value] = []
            value_dict[value].append(string)
        result_dict[col] = value_dict
    
    merged_dict = {}
    for k, dict1 in result_dict.items():
        for key, value in dict1.items():
            if key in merged_dict:
                merged_dict[key].extend(value)
            else:
                merged_dict[key] = value
    for k, v in merged_dict.items():
        decoupled_list = list(set(v))
        merged_dict[k] = decoupled_list
    for i in range(1,6):
        if i not in merged_dict:
            merged_dict[i] = []
    return merged_dict


def color_fixtures(val):
    bg_color = 'background-color: '
    font_color = 'color: '
    if val in home_away_dict[1]:
        bg_color += '#147d1b'
    elif val in home_away_dict[2]:
        bg_color += '#00ff78'
    elif val in home_away_dict[3]:
        bg_color += '#eceae6'
    elif val in home_away_dict[4]:
        bg_color += '#ff0057'
        font_color += 'white'
    elif val in home_away_dict[5]:
        bg_color += '#920947'
        font_color += 'white'
    else:
        bg_color += ''
    style = bg_color + '; ' + font_color
    return style


league_df = get_league_table()
player_dict = get_player_id_dict(order_by_col='now_cost', web_name=False)

gw_max = max(events_df['id'])

cols = st.columns([8, 1, 8])
second_cols = st.columns([8,1,8])

gw_slider = cols[0].selectbox('Select GW: ', range(int(crnt_gw), int(gw_max)))
filter_pos = cols[2].multiselect(
        'Filter Position',
        ['GKP', 'DEF', 'MID', 'FWD'],
        ['GKP', 'DEF', 'MID', 'FWD']
    )

price_min = (ele_df['now_cost'].min())/10
price_max = (ele_df['now_cost'].max())/10
slider1, slider2 = second_cols[0].slider('Filter Price: ', price_min, price_max, [price_min, price_max], 0.1, format='£%.1f')

tsb_min = (ele_df['selected_by_percent'].astype(float).min())
tsb_max = (ele_df['selected_by_percent'].astype(float).max())
tsb_slid1, tsb_slid2 = second_cols[2].slider('Filter TSB%: ', tsb_min, tsb_max, [tsb_min, tsb_max], 0.1, format='%.1f')

df = preds_df.loc[preds_df['GW'] == gw_slider]

ele_df['Pos'] = ele_df['element_type'].map(ele_types_df.set_index('id')['singular_name_short'])
ele_df['team'] = ele_df['team'].map(teams_df.set_index('id')['short_name'])
ele_df.rename(columns={'id': 'element',
                       'total_points': 'Pts',
                       'news': 'News',
                       'selected_by_percent': 'TSB%'}, inplace=True)
ele_df['Name'] = ele_df['element'].map(player_dict)
ele_df['Price'] = ele_df['now_cost']/10

team_fdr_df, team_fixt_df, team_ga_df, team_gf_df = get_fixt_dfs()
new_fixt_df = team_fixt_df.loc[:, gw_slider:(gw_slider)]
new_fixt_cols = ['GW' + str(col) for col in new_fixt_df.columns.tolist()]
new_fixt_df.columns = new_fixt_cols
new_fdr_df = team_fdr_df.loc[:, gw_slider:(gw_slider)]

league_df = league_df.join(new_fixt_df).reset_index()
league_cut = league_df.copy()[['team'] + new_fixt_cols]
for col in new_fixt_cols:
    if league_df[col].dtype == 'O':
        max_length = league_df[col].str.len().max()
        if max_length > 7:
            league_df.loc[league_df[col].str.len() <= 7, col] = league_df[col].str.pad(width=max_length+9, side='both', fillchar=' ')
merge_df = ele_df.merge(df, on='element', how='left')

full_df = merge_df.merge(league_cut, on='team', how='left')
full_df.sort_values('Pred_Pts', ascending=False, inplace=True)

full_cut = full_df[['Name', 'Pos', 'TSB%', 'News', 'Pts', 'Price', 'Pred_Pts'] + new_fixt_cols].set_index('Name').copy()
full_cut['TSB%'] = full_cut['TSB%'].astype(float)/100

final_df = full_cut.loc[(full_cut['Price'] <= slider2) &
                        (full_cut['Price'] > slider1) &
                        (full_cut['TSB%'] <= tsb_slid2/100) &
                        (full_cut['TSB%'] > tsb_slid1/100) &
                        (full_cut['Pos'].isin(filter_pos))]

home_away_dict = get_home_away_str_dict()

total_fmt = {'Price': '£{:.1f}', 'Pred_Pts': '{:.1f}', 'TSB%': '{:.1%}'}
st.dataframe(final_df.style.applymap(color_fixtures, subset=new_fixt_cols) \
             .format(total_fmt), height=1000, width=1000)

