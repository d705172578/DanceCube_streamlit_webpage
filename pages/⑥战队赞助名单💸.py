import streamlit as st
from data_process import DataAnalysis
import datetime
from utils import load_json, get_players_token, save_json
import pandas as pd
import requests
import os

def get_player_headimg(player_id):
    url = f"https://dancedemo.shenghuayule.com/Dance/api/User/GetInfo?userId={player_id}&getNationRank=true"
    token = get_players_token(0)
    headers = { 
        "Authorization": token
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()  # 解析返回的JSON数据
        print('成功获取数据')
        return data['HeadimgURL'], data['UserName']
    else:
        print(f"Error: {response.status_code}")

def display_donate_table(donate_info):
    st.subheader(f"至今为止战队建设支出：{donate_info['4115034']}元 (来自队长个人的赞助)")
    st.markdown(':red[非常感谢大家为大枫树战队的赞助!你给大枫树的每一份帮助，不论是资金，还是资源，或是技术都会被记录在下方(不管你是否为本战队的人)]')
    
    rows = []
    for player in donate_info:
        if player == '4115034':
            continue
        # 将玩家信息添加到行列表中
        if 'head_url' not in donate_info[player]:
            head_url, name = get_player_headimg(player)
            donate_info[player]['head_url'] = head_url
            donate_info[player]['name'] = name
            
        rows.append({
            '头像': donate_info[player]['head_url'],
            '玩家名称': donate_info[player]['name'],
            '捐赠内容': donate_info[player]['donate_items'],
        })
    
    # 一次性将行列表转换为DataFrame
    df = pd.DataFrame(rows)
    st.data_editor(
        df,
        column_config={
            "头像": st.column_config.ImageColumn("头像", help="点击玩家头像可以查看大图哦"), 
            "捐赠内容": st.column_config.ListColumn(
            "捐赠内容",
            help="感谢大家的支持,这些赞助不局限于经济上的,也包括技术或是其他方面的相关帮助",
            width="large",
        ),},
        disabled=df.columns,
        hide_index=True,
        use_container_width=True,
        height=570,
    )
    save_json('/home/NewTeamWeb/team_info/donate.json', donate_info)

donate_info = load_json('/home/NewTeamWeb/team_info/donate.json')
display_donate_table(donate_info)