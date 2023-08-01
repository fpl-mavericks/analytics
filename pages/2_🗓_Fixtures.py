#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 20:18:57 2022

@author: timyouell
"""

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from fpl_utils.fpl_api_collection import (
    get_bootstrap_data, get_current_gw, get_fixture_dfs, get_league_table
)
from fpl_utils.fpl_utils import (
    define_sidebar, get_annot_size
)

base_url = 'https://fantasy.premierleague.com/api/'

st.set_page_config(page_title='Fixtures', page_icon=':calendar:', layout='wide')
define_sidebar()

st.title("Premier League Fixtures")
st.write('Use the sliders to filter the fixtures down to a specific gameweek range.')


league_df = get_league_table()
team_fdr_df, team_fixt_df = get_fixture_dfs()

events_df = pd.DataFrame(get_bootstrap_data()['events'])
gw_min = min(events_df['id'])
gw_max = max(events_df['id'])

# [gw_min, gw_max] should be swapped with [current_gw, current_gw+5] for initial showing
ct_gw = get_current_gw()

col1, col2, col3 = st.columns([2,2,2])
with col1:
    select_options = ['Fixture Difficulty Rating (FDR)',
                     'Average Goals Against (GA)',
                     'Average Goals For (GF)']
    select_choice = st.selectbox("Sort fixtures by", select_options)
with col2:
    radio_options = ['Fixture', 'Statistic']
    radio_choice = st.radio("Toggle fixture or statistic (FDR/GA/GF)",
                            radio_options,
                            horizontal=True)

slider1, slider2 = st.slider('Gameweek: ', gw_min, gw_max, [int(ct_gw), int(ct_gw+4)], 1)
annot_size = get_annot_size(slider1, slider2)

if select_choice == 'Fixture Difficulty Rating (FDR)':
    filtered_fixt_df = team_fdr_df.iloc[:, slider1-1: slider2]
    filtered_team_df = team_fixt_df.iloc[:, slider1-1: slider2]
    new_fixt_df = filtered_fixt_df.copy()
    new_fixt_df.loc[:, 'fixt_ave'] = new_fixt_df.mean(axis=1)
    new_fixt_df.sort_values('fixt_ave', ascending=True, inplace=True)
    new_fixt_df.drop('fixt_ave', axis=1, inplace=True)
    new_fixt_df = new_fixt_df.astype(float)
    filtered_team_df = filtered_team_df.loc[new_fixt_df.index]
    
    fig, ax = plt.subplots()
    if new_fixt_df[slider1].nunique() == 4:
        flatui = ["#00ff78", "#eceae6", "#ff0057", "#920947"]
    else:
        flatui = ["#147d1b", "#00ff78", "#eceae6", "#ff0057", "#920947"]
    if radio_choice == 'Fixture':
        annot_df = filtered_team_df
    else:
        annot_df = new_fixt_df # .astype(int)
    sns.heatmap(new_fixt_df,
                ax=ax,
                annot=annot_df,
                fmt='',
                cmap=flatui,
                annot_kws={'size': annot_size},
                cbar=False,
                linewidth=1)
    
    ax.set_xlabel('Gameweek')
    ax.set_ylabel('Team')
    st.write(fig)

elif select_choice == 'Average Goals Against (GA)':
    st.write('The higher up the heatmap, the higher chance of scoring in the selected GW range.')
    filtered_team_df = team_fixt_df.iloc[:, slider1-1: slider2]
    team_ga_df = team_fixt_df.copy()
    for col in team_fixt_df.columns.tolist():
        team_ga_df[col] = team_fixt_df[col].astype(str).str[:3].map(league_df['GA/Game'])
    
    filtered_ga_df = team_ga_df.iloc[:, slider1-1:slider2]
    ga_fixt_df = filtered_ga_df.copy()
    ga_fixt_df.loc[:, 'fixt_ave'] = ga_fixt_df.mean(axis=1)
    ga_fixt_df.sort_values('fixt_ave', ascending=False, inplace=True)
    ga_fixt_df.drop('fixt_ave', axis=1, inplace=True)
    ga_fixt_df = ga_fixt_df.astype(float)
    filtered_team_df_ga = filtered_team_df.loc[ga_fixt_df.index]
    
    fig, ax = plt.subplots()
    flatui_rev = ["#147d1b", "#00ff78", "#caf4bd", "#eceae6", "#fa8072",
                  "#ff0057", "#920947"][::-1]
    if radio_choice == 'Fixture':
        annot_df = filtered_team_df_ga
    else:
        annot_df = ga_fixt_df
    sns.heatmap(ga_fixt_df, ax=ax, annot=annot_df, fmt='', cmap=flatui_rev,
                annot_kws={'size': annot_size}, cbar=False, linewidth=1)
    # "RdBu"
    ax.set_xlabel('Gameweek')
    ax.set_ylabel('Team')
    st.write(fig)

elif select_choice == 'Average Goals For (GF)':
    st.write('The higher up the plot, the higher chance of not conceeding in the selected GW range.')
    filtered_team_df = team_fixt_df.iloc[:, slider1-1: slider2]
    team_gf_df = team_fixt_df.copy()
    for col in team_fixt_df.columns.tolist():
        team_gf_df[col] = team_fixt_df[col].astype(str).str[:3].map(league_df['GF/Game'])
    
    filtered_gf_df = team_gf_df.iloc[:, slider1-1:slider2]
    gf_fixt_df = filtered_gf_df.copy()
    gf_fixt_df.loc[:, 'fixt_ave'] = gf_fixt_df.mean(axis=1)
    gf_fixt_df.sort_values('fixt_ave', ascending=True, inplace=True)
    gf_fixt_df.drop('fixt_ave', axis=1, inplace=True)
    gf_fixt_df = gf_fixt_df.astype(float)
    filtered_team_df_gf = filtered_team_df.loc[gf_fixt_df.index]
    flatui = ["#147d1b", "#00ff78", "#caf4bd", "#eceae6", "#fa8072", "#ff0057",
              "#920947"]
    if radio_choice == 'Fixture':
        annot_df = filtered_team_df_gf
    else:
        annot_df = gf_fixt_df
    fig, ax = plt.subplots()
    sns.heatmap(gf_fixt_df, ax=ax, annot=annot_df, fmt='', cmap=flatui,
                annot_kws={'size': annot_size}, cbar=False, linewidth=1)
    
    ax.set_xlabel('Gameweek')
    ax.set_ylabel('Team')
    st.write(fig)
    
#updated
