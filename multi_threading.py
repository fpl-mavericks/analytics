#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 17:35:51 2023

@author: timyouell
"""

import pandas as pd
from fpl_utils.fpl_api_collection import (
    get_player_id_dict, get_bootstrap_data, get_player_data
)
import asyncio
import aiohttp


MAX_CONCURRENT_REQUESTS = 10
base_url = 'https://fantasy.premierleague.com/api/'

def get_player_url_list():
    id_dict = get_player_id_dict()
    url_list = []
    for k, v in id_dict.items():
        url_str = base_url + f'element-summary/{k}/'
        url_list.append(url_str)
    return url_list
    
    
async def fetch_url(session, url, semaphore):
    async with semaphore:
        async with session.get(url) as response:
            return await response.text()

async def main():
    api_urls = get_player_url_list()
    # List of your API URLs
    
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        tasks = [asyncio.create_task(fetch_url(session, url, semaphore)) for url in api_urls]
        responses = await asyncio.gather(*tasks)
        
    data = []
    for response in responses:
        data.append({'response': response})
        df = pd.DataFrame(data)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())