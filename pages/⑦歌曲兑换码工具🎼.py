import streamlit as st
from data_process import DataAnalysis
import datetime
from utils import get_qr_code, check_login, request_url, search_music_goods_id
import pandas as pd
import requests
import os

st.title('歌曲兑换码工具')
st.write('目前只能使用批量生成兑换码的功能，其他功能正在开发中')

def get_player_name(player_id):
    url = f"https://dancedemo.shenghuayule.com/Dance/api/User/GetNickname?userID={player_id}"
    headers = { 
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()  # 解析返回的JSON数据
        return data['UserName']
    else:
        st.error('出错了，请联系队长解决')
        print(f"Error: {response.status_code}")


def generate_music_code():
    generate_limit = int(request_url(st.session_state['cur_token'], 'get', url="https://dancedemo.shenghuayule.com/Dance/api/MusicData/GetCodeRemainTimes")['Remain'])
    st.write(f'剩余可生成数量：{generate_limit}首')
    music_id = st.text_input('输入歌曲id')
    generate_num = st.text_input('输入生成数量')
    
    if st.button('生成'):
        if int(generate_num) <= generate_limit:
            music_info = search_music_goods_id(music_id)
            print(music_info['OwnerID'], st.session_state['cur_user'])
            if str(music_info['OwnerID']) == st.session_state['cur_user']:
                res = []
                for i in range(int(generate_num)):
                    res.append(request_url(st.session_state['cur_token'], 'get', url=f"https://dancedemo.shenghuayule.com/Dance/api/MusicData/GetMusicCode?musicId={music_id}")['Code'])
                print('ok')
                st.write(f"歌曲名称:{music_info['GoodsName']}")
                level_info = [i['MusicLevel'] for i in music_info['LevelList']]
                level_info = list(map(lambda x: '无' if x == -1 else str(x), level_info))
                st.write(f"等级信息:{'/'.join(level_info)}")
                for c in res:
                    st.write(str(c))
            else:
                st.error(f"ID:{music_id}, 歌曲名称:{music_info['GoodsName']}, 这个不是你的歌哦")
        else:
            st.error(f'生成数量超过今日上限（{generate_limit}首）了哦')

def generate_family_code():
    pass

def generate_one_code():
    pass

def use_music_code(music_code):
    pass

def display_music_info(token):
    url = 'https://dancedemo.shenghuayule.com/Dance/api/MusicData/GetMyPublishMusic'
    headers = { 
        # 'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
        "Authorization": token
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()  # 解析返回的JSON数据
    else:
        st.error('获取谱面信息出错了，请联系队长')
        print(f"Error: {response.status_code}")
        return



if 'cur_user' not in st.session_state:
    st.write('请先扫描下方二维码登录')
    if 'qr_url' not in st.session_state:
        qr_url, qr_id = get_qr_code() # You need to set this from somewhere
        st.session_state['qr_url'] = qr_url
        st.session_state['qr_id'] = qr_id
    else:
        qr_url = st.session_state['qr_url']
        qr_id = st.session_state['qr_id']
    st.image(qr_url)

    if st.button('登录'):
        token = check_login(qr_id)
        if token and 'access_token' in token:
            st.session_state['cur_token'] = f"bearer {token['access_token']}"
            st.session_state['cur_user'] = str(token['userId'])
        else:
            st.error('没有获取到token,要先扫码后,再进行操作哦')
else:
    st.markdown(':rainbow[**欢迎回来~(迪拉熊语气)**]')
    player_id = st.session_state['cur_user']
    st.write(f'玩家：{get_player_name(player_id)}')
    tab1, tab2 = st.tabs(["使用兑换码", "生成兑换码"])
    with tab1:
        music_code = st.text_input('输入兑换码')
        if st.button('兑换'):
            res = use_music_code(music_code)

    with tab2:
        choice = st.selectbox('选择生成内容', ['批量生成兑换码', '生成谱师全家桶', '生成可多次使用的兑换码'])
        
        
        if choice == '批量生成兑换码':
            text_output = generate_music_code()
        if choice == '生成谱师全家桶':
            text_output = generate_family_code()
        if choice == '生成可多次使用的兑换码':
            text_output = generate_one_code()
        
        display_music_info(st.session_state['cur_token'])