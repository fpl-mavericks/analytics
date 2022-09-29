#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 20:20:45 2022

@author: timyouell
"""

import streamlit as st

base_url = 'https://fantasy.premierleague.com/api/'

st.set_page_config(page_title='Algorithm', page_icon=':computer:', layout='wide')


st.sidebar.subheader('About')
st.sidebar.write("""This website is designed to help you analyse and
                 ultimately pick the best Fantasy Premier League Football
                 options for your team.""")
st.sidebar.write('[Github](https://github.com/TimYouell15)')

st.title('Predicted Points Algorithm')
st.write('I am currently in the process of updating the algorithm, please check back soon for updates to this tab.')
st.write('The idea for this page is to select a GW or multiple GWs and view the predicted points for each player.')
