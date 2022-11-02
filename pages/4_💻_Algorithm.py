#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 20:20:45 2022

@author: timyouell
"""

import streamlit as st
from fpl_utils.fpl_utils import (
    define_sidebar
)

base_url = 'https://fantasy.premierleague.com/api/'

st.set_page_config(page_title='Algorithm', page_icon=':computer:', layout='wide')
define_sidebar()

st.title('Predicted Points Algorithm')
st.write('I am currently in the process of updating the algorithm, please check back soon for updates to this tab.')
st.write('The idea for this page is to select a GW or multiple GWs and view the predicted points for each player.')
