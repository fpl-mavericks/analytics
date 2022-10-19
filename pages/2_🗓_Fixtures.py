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
from fpl_api_collection import (
    get_bootstrap_data, get_current_gw, get_fixture_dfs
)

base_url = 'https://fantasy.premierleague.com/api/'

st.set_page_config(page_title='Fixtures', page_icon=':calendar:', layout='wide')

st.title("Premier League Fixture List")
st.write('Use the sliders to filter the fixtures down to a specific gameweek range.')
st.write('NB: Final GW before the 2022 Qatar World Cup is GW16.')

st.sidebar.subheader('About')
st.sidebar.write("""This website is designed to help you analyse and
                 ultimately pick the best Fantasy Premier League Football
                 options for your team.""")
st.sidebar.write('[GitHub](https://github.com/TimYouell15)')


def display_frame(df):
    '''display dataframe with all float columns rounded to 1 decimal place'''
    float_cols = df.select_dtypes(include='float64').columns.values
    st.dataframe(df.style.format(subset=float_cols, formatter='{:.1f}'))


team_fdr_df, team_fixt_df = get_fixture_dfs()

events_df = pd.DataFrame(get_bootstrap_data()['events'])
gw_min = min(events_df['id'])
gw_max = max(events_df['id'])


def get_annot_size(sl1, sl2):
    ft_size = sl2 - sl1
    if ft_size >= 24:
        annot_size = 2
    elif (ft_size < 24) & (ft_size >= 16):
        annot_size = 3
    elif (ft_size < 16) & (ft_size >= 12):
        annot_size = 4
    elif (ft_size < 12) & (ft_size >= 9):
        annot_size = 5
    elif (ft_size < 9) & (ft_size >= 7):
        annot_size = 6
    elif (ft_size < 7) & (ft_size >= 5):
        annot_size = 7
    else:
        annot_size = 8
    return annot_size

# [gw_min, gw_max] should be swapped with [current_gw, current_gw+5] for initial showing
ct_gw = get_current_gw()

slider1, slider2 = st.slider('Gameweek: ', gw_min, gw_max, [int(ct_gw), int(ct_gw+4)], 1)
annot_size = get_annot_size(slider1, slider2)


filtered_fixt_df = team_fdr_df.iloc[:, slider1-1: slider2]
filtered_team_df = team_fixt_df.iloc[:, slider1-1: slider2]
new_fixt_df = filtered_fixt_df.copy()
new_fixt_df.loc[:, 'fixt_ave'] = new_fixt_df.mean(axis=1)
new_fixt_df.sort_values('fixt_ave', ascending=True, inplace=True)
new_fixt_df.drop('fixt_ave', axis=1, inplace=True)
new_fixt_df = new_fixt_df.astype(float)
filtered_team_df = filtered_team_df.loc[new_fixt_df.index]

fig, ax = plt.subplots()
#cmap='GnBu', 
flatui = ["#00ff78", "#eceae6", "#ff0057", "#920947"]
sns.heatmap(new_fixt_df, ax=ax, annot=filtered_team_df, fmt='', cmap=flatui, annot_kws={'size': annot_size}, cbar_kws={'label': 'Fixture Difficulty Rating (FDR)'})

ax.set_xlabel('Gameweek')
ax.set_ylabel('Team')
st.write(fig)


def fdr_heatmap(slider1, slider2):
    filtered_fixt_df = team_fdr_df.iloc[:, slider1-1: slider2]
    new_fixt_df = filtered_fixt_df.copy()
    new_fixt_df.loc[:, 'fixt_ave'] = new_fixt_df.mean(axis=1)
    new_fixt_df.sort_values('fixt_ave', ascending=True, inplace=True)
    new_fixt_df.drop('fixt_ave', axis=1, inplace=True)
    fig, ax = plt.subplots()
    sns.heatmap(new_fixt_df, ax=ax, annot=True)
    st.write(fig)
    #return new_fixt_df

