import requests
import json
from datetime import datetime
from glob import glob
from utils import get_players_token
import os
import streamlit as st

st.title('获取官谱封面🖼️')
def get_music_cover(key):
    token = get_players_token(0)
    url = f'https://dancedemo.shenghuayule.com/Dance/api/User/GetMusicRankingNew?musicIndex=0&page=1&pagesize=15&machineRank=false&keyword={key}&isStrict=false'
    
    headers = { 
        "Authorization": token,
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()  # 解析返回的JSON数据
        print('成功获取数据')
        return data
    else:
        print(f"Error: {response.status_code}")


def display_info(data):
    for music_info in data['List']:
        st.markdown(f"**歌曲名称：{music_info['Name']} (ID：{music_info['MusicID']})**")
        st.image(music_info['Cover'].rstrip('/200'))
        st.write('')

key = st.text_input('输入想要查询的歌曲名或者歌曲ID')
if st.button('获取歌曲信息'):
    data = get_music_cover(key)
    display_info(data)
    print(f'有人查询了 {key}')
 