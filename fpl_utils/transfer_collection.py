#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 09:17:16 2022

@author: timyouellservian
"""

import pandas as pd
from fpl_api_collection import (
    get_bootstrap_data, get_player_id_dict, get_player_data,
    get_total_fpl_players
)

base_url = 'https://fantasy.premierleague.com/api/'
    

def get_ele_df():
    ele_data = get_bootstrap_data()['elements']
    ele_df = pd.DataFrame(ele_data)
    
    teams_data = get_bootstrap_data()['teams']
    teams_df = pd.DataFrame(teams_data)
    ele_df['team'] = ele_df['team'].map(teams_df.set_index('id')['short_name'])

    ele_df['full_name'] = ele_df['first_name'] + ' ' + ele_df['second_name'] + ' (' + ele_df['team'] + ')'

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
                'T_In_Total', 'T_Out_Total', 'full_name']
    ele_df = ele_df[ele_cols]
    ele_df['T_+/-'] = ele_df['T_In'] - ele_df['T_Out']
    ele_df['TSB%'] = ele_df['TSB%'].astype(float)/100
    total_mans = get_total_fpl_players()
    ele_df['%_+/-'] = ele_df['T_+/-']/total_mans
    ele_df.set_index('Name', inplace=True)
    ele_df.sort_values('T_+/-', ascending=False, inplace=True)
    return ele_df


def collate_tran_df_from_name(ele_df, player_name):
    player_df = ele_df.loc[ele_df['full_name'] == player_name]
    full_player_dict = get_player_id_dict(web_name=False)
    p_id = [k for k, v in full_player_dict.items() if v == player_name]
    p_data = get_player_data(str(p_id[0]))
    p_df = pd.DataFrame(p_data['history'])
    col_rn_dict = {'round': 'GW', 'value': 'Price',
                   'selected': 'SB', 'transfers_in': 'Tran_In',
                   'transfers_out': 'Tran_Out'}
    p_df.rename(columns=col_rn_dict, inplace=True)
    p_df = p_df[['GW', 'Price', 'SB', 'Tran_In', 'Tran_Out']]
    p_df['Price'] = p_df['Price']/10
    new_df = pd.DataFrame({'GW': [(p_df['GW'].max() + 1)],
                           'Price': [player_df['Price'][0]],
                           'Tran_In': [player_df['T_In'][0]],
                           'Tran_Out': [player_df['T_Out'][0]],
                           'SB': [p_df['SB'].iloc[-1] + player_df['T_In'][0] - player_df['T_Out'][0]]})
    p_df = pd.concat([p_df, new_df])
    p_df.set_index('GW', inplace=True)
    return p_df


def get_hist_prices_df():
    ele_df = get_ele_df()
    ordered_names = ele_df['full_name'].tolist()
    df_list = []
    for name in ordered_names:
            p_hist_df = collate_tran_df_from_name(ele_df, name)
            sp = p_hist_df['Price'].iloc[0]
            np = p_hist_df['Price'].iloc[-1]
            new_df = pd.DataFrame({'Player': [name],
                                    'Start_Price': [sp],
                                    'Now_Price': [np],
                                    'Price_+/-': [np - sp]})
            df_list.append(new_df)
    total_df = pd.concat(df_list)
    total_df.sort_values('Price_+/-', ascending=False, inplace=True)
    total_df.set_index('Player', inplace=True)
    return total_df


def write_data():
    prices_df = get_hist_prices_df()
    prices_df['Start_Price'] = prices_df['Start_Price'].map('{:,.1f}'.format)
    prices_df['Now_Price'] = prices_df['Now_Price'].map('{:,.1f}'.format)
    prices_df['Price_+/-'] = prices_df['Price_+/-'].map('{:,.1f}'.format)
    prices_df.to_csv('./data/player_prices.csv', index=True)


def main():
    write_data()
    print('Data Written!')
    

if __name__ == "__main__":
    main()
    
    