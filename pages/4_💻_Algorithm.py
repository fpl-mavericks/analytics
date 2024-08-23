#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 20:20:45 2022

@author: timyouell
"""

import pandas as pd
import streamlit as st
import sys
sys.path.append('/Users/2279556/Documents/analytics/analytics')

from fpl_utils.fpl_api_collection import (
    get_bootstrap_data, get_current_gw, get_current_season,
    get_fixt_dfs, get_league_table, remove_moved_players,
    get_player_id_dict
)
from fpl_utils.fpl_utils import (
    define_sidebar
)

st.set_page_config(page_title='Algorithm', page_icon=':computer:', layout='wide')
define_sidebar()
st.title('Predicted Points Algorithm')
st.write('Gradient Boosting Regressor Algorithm trained on 22/23 historic and 23/24 FPL data so far.')

crnt_gw = get_current_gw()
crnt_season = get_current_season().replace('/', '_')

preds_df = pd.read_csv(f'./data/{crnt_season}_pred_file.csv')
preds_df.rename(columns={'xP': 'xPts'}, inplace=True)

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
    merged_dict[1.5] = []
    merged_dict[2.5] = []
    merged_dict[3.5] = []
    merged_dict[4.5] = []
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
    if val in home_away_dict[1.5]:
        bg_color += '#0ABE4A'
    elif val in home_away_dict[2]:
        bg_color += '#00ff78'
    elif val in home_away_dict[2.5]:
        bg_color += "#caf4bd"
    elif val in home_away_dict[3]:
        bg_color += '#eceae6'
    elif val in home_away_dict[3.5]:
        bg_color += "#fa8072"
    elif val in home_away_dict[4]:
        bg_color += '#ff0057'
        font_color += 'white'
    elif val in home_away_dict[4.5]:
        bg_color += '#C9054F'
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
team_cols = st.columns([1])
second_cols = st.columns([8,1,8])

gw_slider = cols[0].multiselect('Select GW: ', list(range(int(crnt_gw), int(gw_max+1))), [int(crnt_gw)])
# gw_slider = cols[0].multiselect('Select GW: ', list(range(int(crnt_gw), int(gw_max+1))), [22, 21])

gw_slider = list(sorted(gw_slider))

filter_pos = cols[2].multiselect(
        'Filter Position',
        ['GKP', 'DEF', 'MID', 'FWD'],
        ['GKP', 'DEF', 'MID', 'FWD']
    )

teams_list = teams_df['short_name'].tolist()

filter_team = team_cols[0].multiselect(
        'Filter Team',
        teams_list,
        teams_list
    )

price_min = (ele_df['now_cost'].min())/10
price_max = (ele_df['now_cost'].max())/10
slider1, slider2 = second_cols[0].slider('Filter Price: ', price_min, price_max,
                                         [price_min, price_max], 0.1, format='£%.1f')

tsb_min = (ele_df['selected_by_percent'].astype(float).min())
tsb_max = (ele_df['selected_by_percent'].astype(float).max())
tsb_slid1, tsb_slid2 = second_cols[2].slider('Filter TSB%: ', tsb_min, tsb_max,
                                             [tsb_min, tsb_max], 0.1, format='%.1f')

df = preds_df.loc[preds_df['GW'].isin(gw_slider)]

# For each element, add together xPts for multiple GWs
df.columns.tolist()
df = df[['element', 'xPts']].groupby('element').sum()

ele_df['Pos'] = ele_df['element_type'].map(ele_types_df.set_index('id')['singular_name_short'])
ele_df['team'] = ele_df['team'].map(teams_df.set_index('id')['short_name'])
ele_df.rename(columns={'id': 'element',
                       'total_points': 'Total Pts',
                       'news': 'News',
                       'selected_by_percent': 'TSB%'}, inplace=True)
ele_df['Name'] = ele_df['element'].map(player_dict)
ele_df['Price'] = ele_df['now_cost']/10

team_fdr_df, team_fixt_df, team_ga_df, team_gf_df = get_fixt_dfs()
new_fixt_df = team_fixt_df.loc[:, gw_slider]
new_fdr_df = team_fdr_df.loc[:, gw_slider]
new_fixt_cols = ['GW' + str(col) for col in new_fixt_df.columns.tolist()]
new_fixt_df.columns = new_fixt_cols
new_fdr_df.columns = new_fixt_cols

for col in new_fixt_cols:
    if new_fixt_df[col].dtype == 'O':
        max_length = new_fixt_df[col].str.len().max()
        if max_length > 7:
            new_fixt_df.loc[new_fixt_df[col].str.len() <= 7, col] = new_fixt_df[col].str.pad(width=max_length+9,
                                                                                             side='both',
                                                                                             fillchar=' ')
merge_df = ele_df.merge(df, on='element', how='left')

new_fixt_df.reset_index(inplace=True)
new_fixt_df.rename(columns={0: 'team'}, inplace=True)

crnt_gw_str = 'GW' + str(crnt_gw)

full_df = merge_df.merge(new_fixt_df, on='team', how='left')
full_df.loc[full_df[crnt_gw_str] == 'BLANK', 'xPts'] = 0
full_df.sort_values('xPts', ascending=False, inplace=True)

full_df.rename(columns={'team': 'Team'}, inplace=True)

full_cut = full_df[['Name', 'Pos', 'Team', 'TSB%', 'News',
                    'Total Pts', 'Price', 'xPts'] + new_fixt_cols].set_index('Name').copy()
full_cut['TSB%'] = full_cut['TSB%'].astype(float)/100

final_df = full_cut.loc[(full_cut['Price'] <= slider2) &
                        (full_cut['Price'] > slider1) &
                        (full_cut['TSB%'] <= tsb_slid2/100) &
                        (full_cut['TSB%'] > tsb_slid1/100) &
                        (full_cut['Pos'].isin(filter_pos)) &
                        (full_cut['Team'].isin(filter_team))]

final_df.drop('Team', axis=1, inplace=True)

final_df.to_csv('./data/'+crnt_gw_str+'_preds.csv', index=False)

home_away_dict = get_home_away_str_dict()

total_fmt = {'Price': '£{:.1f}', 'xPts': '{:.1f}', 'TSB%': '{:.1%}'}
st.dataframe(final_df.style.applymap(color_fixtures, subset=new_fixt_cols) \
             .format(total_fmt), height=1000, width=1000)
