#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 20:20:43 2022

@author: timyouell

Useful Manager IDs

Tim: 392357
Brookie: 524077
Cam: 1200628
Rosco: 1842899
Ben Youell: 1423578
Matt Childs: 254665
Dhilesh: 2448780
Teebs: 11255
Rank 1 post-GW12: 5409263
"""

import streamlit as st
import altair as alt
import pandas as pd
import requests
from fpl_api_collection import (
    get_bootstrap_data, get_manager_history_data, get_manager_team_data,
    get_manager_details, get_player_data
)




base_url = 'https://fantasy.premierleague.com/api/'

st.set_page_config(page_title='Manager', page_icon=':necktie:', layout='wide')

st.sidebar.subheader('About')
st.sidebar.write("""This website is designed to help you analyse and
                 ultimately pick the best Fantasy Premier League Football
                 options for your team.""")
st.sidebar.write('[GitHub](https://github.com/TimYouell15)')

st.title('Manager')

def get_total_fpl_players():
    base_resp = requests.get(base_url + 'bootstrap-static/')
    return base_resp.json()['total_players']


ele_types_data = get_bootstrap_data()['element_types']
ele_types_df = pd.DataFrame(ele_types_data)

teams_data = get_bootstrap_data()['teams']
teams_df = pd.DataFrame(teams_data)

ele_data = get_bootstrap_data()['elements']
ele_df = pd.DataFrame(ele_data)

ele_df['element_type'] = ele_df['element_type'].map(ele_types_df.set_index('id')['singular_name_short'])
ele_df['team'] = ele_df['team'].map(teams_df.set_index('id')['short_name'])

def chip_converter(name):
    if name == '3xc':
        return 'Triple Captain'
    if name == 'bboost':
        return 'Bench Boost'
    if name == 'freehit':
        return 'Free Hit'
    if name == 'wildcard':
        return 'Wildcard'
    
col1, col2 = st.columns(2)

with col1:
    fpl_id = st.text_input('Please enter your FPL ID:', 392357)
    
    if fpl_id == '':
    	st.write('')
    else:
        try:
            fpl_id = int(fpl_id)
            total_players = get_total_fpl_players()
            if fpl_id <= 0:
                st.write('Please enter a valid FPL ID.')
            elif fpl_id <= total_players:
                manager_data = get_manager_details(fpl_id)
                manager_name = manager_data['player_first_name'] + ' ' + manager_data['player_last_name']
                manager_team = manager_data['name']
                st.write('Displaying FPL 2022/23 Season Data for ' + manager_name + '\'s Team (' + manager_team + ')')
                man_data = get_manager_history_data(fpl_id)
                chips_df = pd.DataFrame(man_data['chips'])
                chips_df['name'] = chips_df['name'].apply(chip_converter)
                chips_df = chips_df[['event', 'name']]
                ave_df = pd.DataFrame(get_bootstrap_data()['events'])[['id', 'average_entry_score']]
                ave_df.columns=['event', 'GW_Average']
                man_gw_hist = pd.DataFrame(man_data['current'])
                man_gw_hist.sort_values('event', ascending=False, inplace=True)
                man_gw_hist = man_gw_hist.merge(chips_df, on='event', how='left')
                man_gw_hist = man_gw_hist.merge(ave_df, on='event', how='left')
                man_gw_hist['name'].fillna('None', inplace=True)
                man_gw_hist.set_index('event', inplace=True)
                rn_cols = {'points': 'GWP', 'total_points': 'OP', 'rank': 'GWR',
                           'overall_rank': 'OR', 'bank': '£', 'value': 'TV',
                           'event_transfers': 'TM', 'event_transfers_cost': 'TC',
                           'points_on_bench': 'PoB', 'name': 'Chip'}
                man_gw_hist.rename(columns=rn_cols, inplace=True)
                man_gw_hist.drop('rank_sort', axis=1, inplace=True)
                man_gw_hist['TV'] = man_gw_hist['TV']/10
                man_gw_hist['£'] = man_gw_hist['£']/10
                man_gw_hist = man_gw_hist[['GW_Average', 'GWP', 'OP', 'GWR', 'OR', '£', 'TV', 'TM', 'TC', 'PoB', 'Chip']]
                st.dataframe(man_gw_hist.style.format({'TV': '£{:.1f}',
                                                       '£': '£{:.1f}'}),
                             width=800, height=560)
            else:
                st.write('FPL ID is too high to be a valid ID. Please try again.')
                st.write('The total number of FPL players is: ' + str(total_players))
        except ValueError:
            st.write('Please enter a valid FPL ID.')

with col2:
    events_df = pd.DataFrame(get_bootstrap_data()['events'])
    complete_df = events_df.loc[events_df['finished'] == True]
    gw_complete_list = sorted(complete_df['id'].tolist(), reverse=True)
    
    fpl_gw = st.selectbox(
        'Team on specific Gameweek', gw_complete_list
        )
    
    if fpl_id == '':
        st.write('')
    else:
        man_picks_data = get_manager_team_data(fpl_id, fpl_gw)
        manager_team_df = pd.DataFrame(man_picks_data['picks'])
        ele_cut = ele_df[['id', 'web_name', 'team', 'element_type']]
        ele_cut.rename(columns={'id': 'element'}, inplace=True)
        manager_team_df = manager_team_df.merge(ele_cut, how='left', on='element')
        # pull gw data for each player
        gw_players_list = manager_team_df['element'].tolist()
        pts_list = []
        for player_id in gw_players_list:
            test = pd.DataFrame(get_player_data(player_id)['history'])
            # fill in blank rounds first
            pl_cols = ['element', 'opponent_team', 'total_points', 'round']
            test_cut = test[pl_cols]
            test_new = test_cut.loc[test_cut['round'] == fpl_gw]
            if len(test_new) == 0:
                test_new = pd.DataFrame([[player_id, 'BLANK', 0, fpl_gw]], columns=pl_cols)
            else:
                test_new = test_new
            pts_list.append(test_new)
        pts_df = pd.concat(pts_list)
        manager_team_df = manager_team_df.merge(pts_df, how='left', on='element')
        manager_team_df.loc[((manager_team_df['multiplier'] == 2) |
                             (manager_team_df['multiplier'] == 3)),
                            'total_points'] = manager_team_df['total_points']*manager_team_df['multiplier']
        manager_team_df.loc[((manager_team_df['is_captain'] == True) &
                             (manager_team_df['multiplier'] == 2)),
                            'web_name'] = manager_team_df['web_name'] + ' (C)'
        manager_team_df.loc[(manager_team_df['multiplier'] == 3),
                            'web_name'] = manager_team_df['web_name'] + ' (TC)'
        manager_team_df.loc[(manager_team_df['is_vice_captain'] == True),
                            'web_name'] = manager_team_df['web_name'] + ' (VC)'
        manager_team_df.loc[manager_team_df['multiplier'] != 0, 'Played'] = True
        manager_team_df['Played'].fillna(False, inplace=True)
        manager_team_df = manager_team_df[['web_name', 'element_type', 'team', 'opponent_team', 'total_points', 'Played']]
        rn_cols = {'element_type': 'Pos', 'team': 'Team', 'opponent_team': 'vs', 'total_points': 'GWP'}
        manager_team_df.rename(columns=rn_cols, inplace=True)
        manager_team_df.set_index('web_name', inplace=True)
        manager_team_df['vs'] = manager_team_df['vs'].map(teams_df.set_index('id')['short_name'])
        manager_team_df['vs'].fillna('BLANK', inplace=True)
        st.dataframe(manager_team_df, height=570)


# line plot of rank over time. Put average score on there too.
# cols: GW, GWPoints, AvePoints

if fpl_id == '':
    st.write('')
else:
    curr_df = pd.DataFrame(get_manager_history_data(fpl_id)['current'])
    man_data = get_manager_details(fpl_id)
    curr_df['Manager'] = man_data['player_first_name'] + ' ' + man_data['player_last_name']
    ave_df = pd.DataFrame(get_bootstrap_data()['events'])[['id', 'average_entry_score']]
    ave_df.columns=['event', 'points']
    ave_df['Manager'] = 'GW Average'
    ave_cut = ave_df.loc[ave_df['event'] <= max(curr_df['event'])]
    concat_df = pd.concat([curr_df, ave_cut])
    c = alt.Chart(concat_df).mark_line().encode(
        x=alt.X('event', axis=alt.Axis(tickMinStep=1, title='GW')),
        y=alt.Y('points', axis=alt.Axis(title='GW Points')),
        color='Manager').properties(
            height=400)
    st.altair_chart(c, use_container_width=True)

def collate_manager_history(fpl_id):
    df = pd.DataFrame(get_manager_history_data(fpl_id)['current'])
    data = get_manager_details(fpl_id)
    df['Manager'] = data['player_first_name'] + ' ' + data['player_last_name']
    return df
    

if fpl_id == '':
    st.write('')
else:
    if 'ID' not in st.session_state:
        st.session_state['ID'] = [fpl_id]
    new_id = st.text_input('Select another FPL ID to compare:', '')
    button = st.button('Add Manager')
    if button and new_id != '':
        st.session_state.ID.append(new_id)
    filter_man = st.multiselect(
        'Manager IDs',
        st.session_state.ID,
        st.session_state.ID,
        key='ID'
    )
    df_list = []
    for fpl_id in filter_man:
        new_df = collate_manager_history(fpl_id)
        df_list.append(new_df)
    total_df = pd.concat(df_list)

    c = alt.Chart(total_df).mark_line().encode(
        x=alt.X('event', axis=alt.Axis(tickMinStep=1, title='GW')),
        y=alt.Y('overall_rank', axis=alt.Axis(title='Overall Rank'), scale=alt.Scale(reverse=True)),
        color='Manager').properties(
            height=700)
    st.altair_chart(c, use_container_width=True)
        

# Historic season ranks