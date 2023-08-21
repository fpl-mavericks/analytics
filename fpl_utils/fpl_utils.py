#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 10:08:16 2022

@author: timyouell
"""

import streamlit as st
from fpl_utils.fpl_api_collection import get_total_fpl_players

total_players = get_total_fpl_players()

def define_sidebar():
    st.sidebar.subheader('About')
    st.sidebar.write("""This website is designed to help you analyse and
                     ultimately pick the best Fantasy Premier League Football
                     options for your team.""")
    st.sidebar.write("""Current number of FPL Teams: """ + str('{:,.0f}'.format(total_players)))
    st.sidebar.write('[Author](https://www.linkedin.com/in/tim-youell-616731a6)')
    st.sidebar.write('[GitHub](https://github.com/fpl-mavericks/analytics/)')


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