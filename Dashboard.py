#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 20:14:22 2022

@author: timyouell
"""


import streamlit as st
import altair as alt
import pandas as pd
import requests
from fpl_utils.fpl_api_collection import (
    get_bootstrap_data
)
from fpl_utils.fpl_utils import (
    define_sidebar
)

base_url = 'https://fantasy.premierleague.com/api/'

st.set_page_config(page_title='FPL Dashboard', page_icon=':soccer:', layout='wide')
st.title('FPL Dashboard')
#st.write('Please check back soon for Fantasy Premier League Football stats, graphs and predictions.')

define_sidebar()


def get_total_fpl_players() -> int:
    '''
    returns an int value of the current total number of fpl teams.
    '''
    base_resp = requests.get(base_url + 'bootstrap-static/')
    return base_resp.json()['total_players']


def display_frame(df):
    '''display dataframe with all float columns rounded to 1 decimal place'''
    float_cols = df.select_dtypes(include='float64').columns.values
    st.dataframe(df.style.format(subset=float_cols, formatter='{:.1f}'))


def get_min_max_vals(df, x_var):
    min_ = (df[x_var].min())
    max_ = (df[x_var].max())
    return min_, max_

ele_types_df = pd.DataFrame(get_bootstrap_data()['element_types'])

teams_df = pd.DataFrame(get_bootstrap_data()['teams'])

ele_df = pd.DataFrame(get_bootstrap_data()['elements'])


ele_df['element_type'] = ele_df['element_type'].map(ele_types_df.set_index('id')['singular_name_short'])
ele_df['team'] = ele_df['team'].map(teams_df.set_index('id')['short_name'])

rn_cols = {'web_name': 'Name', 'team': 'Team', 'element_type': 'Pos', 
           'event_points': 'GW_Pts', 'total_points': 'Pts',
           'selected_by_percent': 'TSB%', 'minutes': 'Mins',
           'goals_scored': 'GS', 'assists': 'A', 'now_cost': 'Price',
           'penalties_missed': 'Pen_Miss', 'clean_sheets': 'CS',
           'goals_conceded': 'GC', 'own_goals': 'OG',
           'penalties_saved': 'Pen_Save', 'saves': 'S',
           'yellow_cards': 'YC', 'red_cards': 'RC', 'bonus': 'B', 'bps': 'BPS',
           'value_form': 'Value', 'points_per_game': 'PPG', 'influence': 'I',
           'creativity': 'C', 'threat': 'T', 'ict_index': 'ICT',
           'influence_rank': 'I_Rank', 'creativity_rank': 'C_Rank',
           'threat_rank': 'T_Rank', 'ict_index_rank': 'ICT_Rank',
           'transfers_in_event': 'T_In', 'transfers_out_event': 'T_Out'}
ele_df.rename(columns=rn_cols, inplace=True)

ele_df.sort_values('Pts', ascending=False, inplace=True)

ele_df['GP'] = (ele_df['Pts'].astype(float)/ele_df['PPG'].astype(float)).round(0)
ele_df['GP'].fillna(0, inplace=True)
ele_df = ele_df.loc[ele_df['GP'] >= 0]
ele_df['GP'] = ele_df['GP'].astype(int)


ele_df['Price'] = ele_df['Price']/10

ele_df['TSB%'].replace('0.0', '0.09', inplace=True)
ele_df['TSB%'] = ele_df['TSB%'].astype(float)/100



st.header('Season Totals')

ele_cols = ['Name', 'Team', 'Pos', 'GW_Pts', 'Pts', 'Price', 'TSB%', 'GP',
            'Mins', 'GS', 'A', 'Pen_Miss', 'CS', 'GC', 'OG', 'Pen_Save', 'S',
            'YC', 'RC', 'B', 'BPS', 'Value', 'PPG', 'I', 'C', 'T', 'ICT',
            'I_Rank', 'C_Rank', 'T_Rank', 'ICT_Rank']
ele_df = ele_df[ele_cols]
indexed_ele_df = ele_df.set_index('Name')
# display_frame(indexed_ele_df)
st.dataframe(indexed_ele_df.style.format({'Price': '£{:.1f}',
                                          'TSB%': '{:.1%}'}))


col1, col2, col3 = st.columns([1,2,3])

with col1:
    scatter_x_var = st.selectbox(
        'X axis variable',
        ['Price', 'Mins', 'TSB%', 'GP']
    )
scatter_lookup = {'GP': 'GP', 'Price': 'Price', 'Mins': 'Mins', 'TSB%': 'TSB%'}

with col2:
    filter_pos = st.multiselect(
        'Filter position type',
        ['GKP', 'DEF', 'MID', 'FWD'],
        ['GKP', 'DEF', 'MID', 'FWD']
    )

min_, max_ = get_min_max_vals(ele_df, scatter_x_var)
if scatter_x_var == 'Price':
    slider1, slider2 = st.slider('Filter ' + scatter_x_var + ': ', min_, max_,
                                 [min_, max_], 0.1, format='£%.1f')
elif scatter_x_var == 'TSB%':
    min_ = min_*100
    max_ = max_*100
    slider1, slider2 = st.slider('Filter ' + scatter_x_var + ': ', min_, max_,
                                 [min_, max_], 0.1, format='%.1f')
else:
    slider1, slider2 = st.slider('Filter ' + scatter_x_var + ': ', min_, max_,
                                 [min_, max_], 1)

st.header('Points per ' + scatter_x_var)
if scatter_x_var == 'TSB%':
    c = alt.Chart(ele_df.loc[ele_df['Pos'].isin(filter_pos) &
                             (ele_df[scatter_x_var] >= slider1/100) &
                             (ele_df[scatter_x_var] <= slider2/100)]).mark_circle(size=75).encode(
        alt.X(scatter_lookup[scatter_x_var], scale=alt.Scale(zero=False)),
        y='Pts',
        color='Pos',
        tooltip=['Name', 'Pts']
    )
else:
    c = alt.Chart(ele_df.loc[ele_df['Pos'].isin(filter_pos) &
                             (ele_df[scatter_x_var] >= slider1) &
                             (ele_df[scatter_x_var] <= slider2)]).mark_circle(size=75).encode(
        alt.X(scatter_lookup[scatter_x_var], scale=alt.Scale(zero=False)),
        y='Pts',
        color='Pos',
        tooltip=['Name', 'Pts']
    )
st.altair_chart(c, use_container_width=True)

var_df = indexed_ele_df.copy()
if scatter_x_var == 'TSB%':
    var_df = var_df.loc[(var_df['Pos'].isin(filter_pos)) &
                        (var_df[scatter_x_var] >= slider1/100) &
                        (var_df[scatter_x_var] <= slider2/100)]
else:
    var_df = var_df.loc[(var_df['Pos'].isin(filter_pos)) &
                        (var_df[scatter_x_var] >= slider1) &
                        (var_df[scatter_x_var] <= slider2)]
per_var = 'Pts/' + scatter_x_var
var_df[per_var] = var_df['Pts'].astype(float)/var_df[scatter_x_var].astype(float)
var_df.sort_values('Pts/' + scatter_x_var, ascending=False, inplace=True)
droppers = ['I', 'C', 'T', 'ICT', 'I_Rank','C_Rank', 'T_Rank', 'ICT_Rank']
var_df.drop(droppers, axis=1, inplace=True)
if per_var == 'Pts/TSB%':
    var_df[per_var] = var_df[per_var]/100
    st.dataframe(var_df.style.format({'Price': '£{:.1f}',
                                      'TSB%': '{:.1%}',
                                      per_var: '{:.2f}'}))
else:
    st.dataframe(var_df.style.format({'Price': '£{:.1f}',
                                      'TSB%': '{:.1%}',
                                      per_var: '{:.3f}'}))
