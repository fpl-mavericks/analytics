#!/usr/bin/env python3
"""
@author: timyouell
"""

import pandas as pd
from fpl_utils.fpl_api_collection import (
    get_player_id_dict, get_bootstrap_data, get_player_data
)
import asyncio
import aiohttp
import time
import requests


MAX_CONCURRENT_REQUESTS = 50
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
            return await response.json()


async def main():
    api_urls = get_player_url_list()
    # List of your API URLs
    
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        tasks = [asyncio.create_task(fetch_url(session, url,
                                               semaphore)) for url in api_urls]
        responses = await asyncio.gather(*tasks)
        
    data = []
    for response in responses:
        data.append(response['history'])
        
    flat_data = [item for sublist in data for item in sublist]
    df = pd.DataFrame(flat_data)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    

def collate_player_hist() -> pd.DataFrame():
    start = time.time()
    res = []
    p_dict = get_player_id_dict()
    for p_id, p_name in p_dict.items():
        resp = requests.get('{}element-summary/{}/'.format(base_url, p_id))
        print('Getting ' + p_name + ' data')
        if resp.status_code != 200:
            print('Request to {} data failed'.format(p_name))
            raise Exception(f'Response was status code {resp.status_code}')
        else:
            res.append(resp.json()['history'])
    end = time.time()
    print(end-start)
    return pd.DataFrame(res)


