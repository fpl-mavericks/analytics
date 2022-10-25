#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 10:08:16 2022

@author: timyouell
"""

import streamlit as st


def define_sidebar():
    st.sidebar.subheader('About')
    st.sidebar.write("""This website is designed to help you analyse and
                     ultimately pick the best Fantasy Premier League Football
                     options for your team.""")
    st.sidebar.write('[Author](https://www.linkedin.com/in/tim-youell-616731a6)')
    st.sidebar.write('[GitHub](https://github.com/fpl-mavericks/analytics/)')
