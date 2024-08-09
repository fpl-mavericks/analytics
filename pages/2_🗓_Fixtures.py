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
    get_bootstrap_data, get_current_gw, get_fixt_dfs, get_league_table
)
from fpl_utils.fpl_utils import (
    define_sidebar, get_annot_size, map_float_to_color,
    get_text_color_from_hash
)

base_url = 'https://fantasy.premierleague.com/api/'

st.set_page_config(page_title='Fixtures', page_icon=':calendar:', layout='wide')
define_sidebar()
st.title("Premier League Fixtures")

league_df = get_league_table()
team_fdr_df, team_fixt_df, team_ga_df, team_gf_df = get_fixt_dfs()

events_df = pd.DataFrame(get_bootstrap_data()['events'])
gw_min = min(events_df['id'])
gw_max = max(events_df['id'])

ct_gw = get_current_gw()

col1, col2, col3 = st.columns([2,2,2])
with col1:
    select_options = ['Fixture Difficulty Rating (FDR)',
                     'Average Goals Against (GA)',
                     'Average Goals For (GF)']
    select_choice = st.selectbox("Sort fixtures by:", select_options)
with col2:
    radio_options = ['Fixture', 'Statistic']
    radio_choice = st.radio("Toggle fixture or stat:",
                            radio_options,
                            horizontal=True)

slider1, slider2 = st.slider('Gameweek: ', gw_min, gw_max, [int(ct_gw), int(ct_gw+4)], 1)
annot_size = get_annot_size(slider1, slider2)

if select_choice == 'Fixture Difficulty Rating (FDR)':
    st.write('The higher up the heatmap, the \'easier\' (according to the FDRs) the games in the selected GW range.')
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
        sns.heatmap(new_fixt_df,
                    ax=ax,
                    cmap=flatui,
                    annot=False,
                    fmt='',
                    cbar=False,
                    linewidth=1)
        new_fixt_df.fillna(0, inplace=True)
        for i in range(len(annot_df)):
            for j in range(slider2 - slider1+1):
                val = annot_df[slider1 + j][list(annot_df[slider1 + j].keys())[i]]
                g_val = new_fixt_df[slider1 + j][list(new_fixt_df[slider1 + j].keys())[i]]
                if len(val) > 7:
                    fontsize = annot_size/1.5
                else:
                    fontsize = annot_size 
                text_color = 'white' if flatui[int(g_val-2)] == flatui[-1] or flatui[int(g_val-2)] == flatui[-2]  or flatui[int(g_val-2)] == '#147d1b' else 'black'
                plt.text(j + 0.5, i + 0.5, val, ha='center', va='center', fontsize=fontsize, color=text_color)
    else:
        annot_df = new_fixt_df
        sns.heatmap(new_fixt_df, ax=ax, annot=True, fmt='', cmap=flatui,
                    annot_kws={'size': annot_size}, cbar=False, linewidth=1, color='black')

    ax.set_xlabel('Gameweek')
    ax.set_ylabel('Team')
    st.write(fig)
    

elif select_choice == 'Average Goals Against (GA)':
    st.write('The higher up the heatmap, based on historic averages, the higher chance of scoring in the selected GW range.')
    filtered_team_df = team_fixt_df.iloc[:, slider1-1: slider2]
    filtered_ga_df = team_ga_df.iloc[:, slider1-1:slider2]
    ga_fixt_df = filtered_ga_df.copy()
    ga_fixt_df.loc[:, 'fixt_ave'] = ga_fixt_df.mean(axis=1)
    ga_fixt_df.sort_values('fixt_ave', ascending=False, inplace=True)
    ga_fixt_df.drop('fixt_ave', axis=1, inplace=True)
    ga_fixt_df = ga_fixt_df.astype(float)
    filtered_team_df_ga = filtered_team_df.loc[ga_fixt_df.index]
    
    fig, ax = plt.subplots()
    flatui_rev = ["#147d1b", "#00ff78", "#caf4bd", "#eceae6", "#fa8072", "#ff0057",
              "#920947"][::-1]
    if radio_choice == 'Fixture':
        annot_df = filtered_team_df_ga
        sns.heatmap(ga_fixt_df,
                    ax=ax,
                    cmap=flatui_rev,
                    annot=False,
                    fmt='',
                    cbar=False,
                    linewidth=1)
        for i in range(len(annot_df)):
            for j in range(slider2 - slider1+1):
                val = annot_df[slider1 + j][list(annot_df[slider1 + j].keys())[i]]
                g_val = ga_fixt_df[slider1 + j][list(ga_fixt_df[slider1 + j].keys())[i]]
                if len(val) > 7:
                    fontsize = annot_size/1.5
                else:
                    fontsize = annot_size
                hash_color = map_float_to_color(g_val, flatui_rev, ga_fixt_df.min().min(), ga_fixt_df.max().max())
                text_color = get_text_color_from_hash(hash_color)
                plt.text(j + 0.5, i + 0.5, val, ha='center', va='center', fontsize=fontsize, color=text_color)
    else:
        annot_df = ga_fixt_df
        sns.heatmap(annot_df, ax=ax, annot=True, fmt='', cmap=flatui_rev,
                    annot_kws={'size': annot_size}, cbar=False, linewidth=1, color='black')
    ax.set_xlabel('Gameweek')
    ax.set_ylabel('Team')
    st.write(fig)

elif select_choice == 'Average Goals For (GF)':
    st.write('The higher up the heatmap, based on historic averages, the higher chance of keeping a clean sheet in the selected GW range.')
    filtered_team_df = team_fixt_df.iloc[:, slider1-1: slider2]
    filtered_gf_df = team_gf_df.iloc[:, slider1-1:slider2]
    gf_fixt_df = filtered_gf_df.copy()
    gf_fixt_df.loc[:, 'fixt_ave'] = gf_fixt_df.mean(axis=1)
    gf_fixt_df.sort_values('fixt_ave', ascending=True, inplace=True)
    gf_fixt_df.drop('fixt_ave', axis=1, inplace=True)
    gf_fixt_df = gf_fixt_df.astype(float)
    filtered_team_df_gf = filtered_team_df.loc[gf_fixt_df.index]
    
    fig, ax = plt.subplots()
    flatui = ["#147d1b", "#00ff78", "#caf4bd", "#eceae6", "#fa8072", "#ff0057",
              "#920947"]
    if radio_choice == 'Fixture':
        annot_df = filtered_team_df_gf
        sns.heatmap(gf_fixt_df,
                    ax=ax,
                    cmap=flatui,
                    annot=False,
                    fmt='',
                    cbar=False,
                    linewidth=1)
        for i in range(len(annot_df)):
            for j in range(slider2 - slider1+1):
                val = annot_df[slider1 + j][list(annot_df[slider1 + j].keys())[i]]
                g_val = gf_fixt_df[slider1 + j][list(gf_fixt_df[slider1 + j].keys())[i]]
                if len(val) > 7:
                    fontsize = annot_size/1.5
                else:
                    fontsize = annot_size
                hash_color = map_float_to_color(g_val, flatui, gf_fixt_df.min().min(), gf_fixt_df.max().max())
                text_color = get_text_color_from_hash(hash_color)
                plt.text(j + 0.5, i + 0.5, val, ha='center', va='center', fontsize=fontsize, color=text_color)
    else:
        annot_df = gf_fixt_df
        sns.heatmap(annot_df, ax=ax, annot=True, fmt='', cmap=flatui,
                    annot_kws={'size': annot_size}, cbar=False, linewidth=1, color='black')
    ax.set_xlabel('Gameweek')
    ax.set_ylabel('Team')
    st.write(fig)

print(new_fixt_df)
