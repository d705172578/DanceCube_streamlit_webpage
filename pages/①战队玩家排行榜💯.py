import streamlit as st
from data_process import DataAnalysis
import datetime
from utils import get_filename, load_json, get_players_token
import pandas as pd
from run_per_day import save_data
import requests

def display_rank_table(data_analysis):
    
    info = data_analysis.info

    if not info:
        st.error('这一天忘记存储数据啦!换一天看看吧')
        return 
    # 创建一个列表来存储每行的数据
    rows = []

    for player in info:
        # 将玩家信息添加到行列表中
        rows.append({
            '头像': info[player]['HeadimgURL'],
            '头衔': info[player]['MemberTypeText'],
            '玩家名称': info[player]['UserName'],
            '积分总贡献': info[player]['PointTotal'],
            '积分月贡献': info[player]['PointCurMonth'],
            '战力值': info[player]['LvRatio'],
            '金币总贡献':info[player]['GoldTotal'],
            '金币月贡献':info[player]['GoldCurMonth'],
            '上次活跃时间': info[player]['LastAccessText'],
            '上次登录日期': info[player]['LastAccess'],
            '入队时间': info[player]['AddTime']
        })

    # 一次性将行列表转换为DataFrame
    df = pd.DataFrame(rows)
    
    st.data_editor(
        df,
        column_config={"头像": st.column_config.ImageColumn("头像", help="点击玩家头像可以查看大图哦")},
        disabled=df.columns,
        hide_index=True,
        use_container_width=True
    )

def calculate_prizes(juanwang_list, juanwang_id, info):  
    # 1. 获取所有参赛者的积分并排序  
    scores = [(id, info[id]['PointCurMonth']) for id in juanwang_list]  
    scores.sort(key=lambda x: x[1], reverse=True)  # 按积分降序排序  
  
    # 2. 找到卷王的排名  
    juanwang_rank = next((i+1 for i, (id, _) in enumerate(scores) if id == juanwang_id), None)  
  
    # 3. 初始化结果字典，将所有参赛者的奖金设为0  
    prizes = {id: 0 for id in juanwang_list}  
    
    # 4. 计算卷王应得的奖金比例（如果卷王存在）  
    if juanwang_rank:  
        juanwang_prize_percent = 100 / (2 ** (juanwang_rank - 1))  
        juanwang_prize = juanwang_prize_percent if juanwang_prize_percent >= 1 else 0  
        prizes[juanwang_id] = juanwang_prize  
  
        # 5. 如果有超越卷王的人，则按照积分比例分发奖金 
        remaining_prize = 100 - juanwang_prize  
        if remaining_prize > 0 and juanwang_rank > 1:  
            prize_per_person = remaining_prize / (juanwang_rank - 1)  
            total_score = sum([scores[i][1] ** 2 for i in range(juanwang_rank - 1)])
            for i in range(juanwang_rank - 1):  
                prizes[scores[i][0]] = remaining_prize * (scores[i][1] ** 2 / total_score)
  
    # 6. 返回结果  
    return prizes

def display_juanwang_table(data_analysis, juanwang_info):
    info = data_analysis.info
    juanwang_id = juanwang_info['卷王']
    juanwang_list = juanwang_info['参赛者']

    
    if juanwang_id == '0':
        st.write('卷王正在选取中')
        juanwang_prizes = {id: '选取卷王后实时计算' for id in juanwang_list}
    else:
        juanwang_name = info[juanwang_info['卷王']]['UserName']
        st.markdown(f":rainbow[本月卷王：{juanwang_name}]")
        juanwang_prizes = calculate_prizes(juanwang_list, juanwang_id, info)
        for key in juanwang_prizes:
            juanwang_prizes[key] = '%.2f' % juanwang_prizes[key]
        

    rows = []
    if juanwang_list:
        for player in juanwang_list:
            # 将玩家信息添加到行列表中
            rows.append({
                '头像': info[player]['HeadimgURL'],
                '玩家名称': info[player]['UserName'] + ("(本月卷王)" if player == juanwang_id else ""),
                '积分月贡献': info[player]['PointCurMonth'],
                '可获得的奖金': juanwang_prizes[player],
            })
        
        # 一次性将行列表转换为DataFrame
        df = pd.DataFrame(rows)

        sorted_df = df.sort_values(by='积分月贡献', ascending=False)
        st.data_editor(
            sorted_df,
            column_config={"头像": st.column_config.ImageColumn("头像", help="点击玩家头像可以查看大图哦")},
            disabled=df.columns,
            hide_index=True,
            use_container_width=True
        )

def display_elite_table(data_analysis, elite_info):
    info = data_analysis.info
    formal_elite = elite_info['formal_elite']
    temp_elite = elite_info['temp_elite']
    st.subheader('战队精英队员福利')
    st.caption('1.可获得app中精英队员的头衔')
    st.caption('2.疯狂星期四报名时有5%的概率,获得2点幸运值')
    st.caption('3.使用枫叶兑换战队周边时可享8折优惠')
    st.caption('4.每月月底可领取“积分月供x10%”的枫叶')
    st.write('')
    st.subheader('正式精英列表')
    st.caption('通过S2考核后，可成为正式精英成员，自成为正式精英队员开始后，若有连续3个月的积分月供总和低于3000，则会被取消正式精英成员身份，需要重新考核。')
    rows = []
    if formal_elite:
        for player_info in formal_elite:
            player_id = player_info['player_id']
            # 将玩家信息添加到行列表中
            rows.append({
                '头像': info[player_id]['HeadimgURL'],
                '玩家名称': info[player_id]['UserName'],
                '当前月供积分': info[player_id]['PointCurMonth'],
                '可获得枫叶数': int(int(info[player_id]['PointCurMonth']) * 0.1),
            })
        
        # 一次性将行列表转换为DataFrame
        df = pd.DataFrame(rows)

        sorted_df = df.sort_values(by='当前月供积分', ascending=False)
        st.data_editor(
            sorted_df,
            column_config={"头像": st.column_config.ImageColumn("头像", help="点击玩家头像可以查看大图哦")},
            disabled=df.columns,
            hide_index=True,
            use_container_width=True
        )

    st.subheader('流动精英列表')
    st.caption('当月积分月供超过2w5或金币月供超过2w的队员可以获得流动精英的身份，持续时长为1个月，流动精英队员与正式队员享有相同福利待遇。')
    rows = []
    if temp_elite:
        for player_id in temp_elite:
            # 将玩家信息添加到行列表中
            rows.append({
                '头像': info[player_id]['HeadimgURL'],
                '玩家名称': info[player_id]['UserName'],
                '当前月供积分': info[player_id]['PointCurMonth'],
                '可获得枫叶数': int(int(info[player_id]['PointCurMonth']) * 0.1),
            })
        
        # 一次性将行列表转换为DataFrame
        df = pd.DataFrame(rows)

        sorted_df = df.sort_values(by='当前月供积分', ascending=False)
        st.data_editor(
            sorted_df,
            column_config={"头像": st.column_config.ImageColumn("头像", help="点击玩家头像可以查看大图哦")},
            disabled=df.columns,
            hide_index=True,
            use_container_width=True
        )

st.title('战队玩家排行榜')
tab1, tab2, tab3 = st.tabs(["基本排行榜", "战队精英榜", "卷王排行榜"])

with tab1:
    max_file_name = get_filename('/home/NewTeamWeb/json_log')
    y, m, d = max_file_name.rstrip('.json').split('-')[-1].split('_')
    earliest_day = datetime.date(2024, 4, 24)
    latest_day = datetime.date(int(y), int(m), int(d))

    select_day = st.date_input(
        '在下方可以选择想查看的日期哦',
        value = latest_day,
        min_value = earliest_day,
        max_value = latest_day,
        format = 'YYYY-MM-DD'
    )

    data_analysis = DataAnalysis(select_day)
    display_rank_table(data_analysis)

with tab2:
    save_data(flag=False)
    data_analysis = DataAnalysis()
    elite_info = load_json('/home/NewTeamWeb/team_info/second_leader.json')
    display_elite_table(data_analysis, elite_info)

with tab3:
    save_data(flag=False)
    data_analysis = DataAnalysis()
    juanwang_info = load_json('/home/NewTeamWeb/team_info/juanwang.json')
    display_juanwang_table(data_analysis, juanwang_info)
