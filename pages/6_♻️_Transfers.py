#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 20:21:38 2022

@author: timyouell
"""

import streamlit as st
import pandas as pd
from fpl_api_collection import (
    get_bootstrap_data, get_total_fpl_players
)

base_url = 'https://fantasy.premierleague.com/api/'

st.set_page_config(page_title='Transfers', page_icon=':recycle:', layout='wide')

st.sidebar.subheader('About')
st.sidebar.write("""This website is designed to help you analyse and
                 ultimately pick the best Fantasy Premier League Football
                 options for your team.""")
st.sidebar.write('[GitHub](https://github.com/TimYouell15)')

st.title('Transfers')
st.write('Table ordered by most transferred in this GW.')
st.write('Click the %_+/- column to reverse the table and see most transferred out.')

def display_frame(df):
    '''display dataframe with all float columns rounded to 1 decimal place'''
    float_cols = df.select_dtypes(include='float64').columns.values
    st.dataframe(df.style.format(subset=float_cols, formatter='{:.2f}'))

# Most transferred in this GW df
ele_types_data = get_bootstrap_data()['element_types']
ele_types_df = pd.DataFrame(ele_types_data)

teams_data = get_bootstrap_data()['teams']
teams_df = pd.DataFrame(teams_data)

ele_data = get_bootstrap_data()['elements']
ele_df = pd.DataFrame(ele_data)

ele_df['element_type'] = ele_df['element_type'].map(ele_types_df.set_index('id')['singular_name_short'])
ele_df['team'] = ele_df['team'].map(teams_df.set_index('id')['short_name'])

rn_cols = {'web_name': 'Name', 'team': 'Team', 'element_type': 'Pos', 
           'event_points': 'GW_Pts', 'total_points': 'Pts',
           'now_cost': 'Price', 'selected_by_percent': 'TSB%',
           'minutes': 'Mins', 'goals_scored': 'GS', 'assists': 'A',
           'penalties_missed': 'Pen_Miss', 'clean_sheets': 'CS',
           'goals_conceded': 'GC', 'own_goals': 'OG',
           'penalties_saved': 'Pen_Save', 'saves': 'S',
           'yellow_cards': 'YC', 'red_cards': 'RC', 'bonus': 'B', 'bps': 'BPS',
           'value_form': 'Value', 'points_per_game': 'PPG', 'influence': 'I',
           'creativity': 'C', 'threat': 'T', 'ict_index': 'ICT',
           'influence_rank': 'I_Rank', 'creativity_rank': 'C_Rank',
           'threat_rank': 'T_Rank', 'ict_index_rank': 'ICT_Rank',
           'transfers_in_event': 'T_In', 'transfers_out_event': 'T_Out',
           'transfers_in': 'T_In_Total', 'transfers_out': 'T_Out_Total'}
ele_df.rename(columns=rn_cols, inplace=True)
ele_df['Price'] = ele_df['Price']/10

ele_cols = ['Name', 'Team', 'Pos', 'Pts', 'Price', 'TSB%', 'T_In', 'T_Out',
            'T_In_Total', 'T_Out_Total']

ele_df = ele_df[ele_cols]

ele_df['T_+/-'] = ele_df['T_In'] - ele_df['T_Out']

total_mans = get_total_fpl_players()

ele_df['TSB%'] = ele_df['TSB%'].astype(float)/100
ele_df['%_+/-'] = ele_df['T_+/-']/total_mans

ele_df.set_index('Name', inplace=True)
ele_df.sort_values('T_+/-', ascending=False, inplace=True)


st.dataframe(ele_df.style.format({'Price': '£{:.1f}',
                                  'TSB%': '{:.1%}',
                                  '%_+/-': '{:.2%}'}))

#display_frame(ele_df)
#.background_gradient(cmap='Greens')



# Graph of ownership over time for a specific player, two y-axis (transfers in and price?)

