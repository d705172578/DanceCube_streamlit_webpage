import streamlit as st
from utils import update_token, load_json, request_url, get_players_token, save_json, display_player_info, get_filename, get_qr_code, check_login
import pandas as pd
import requests
import time
import random

key = st.text_input("请输入队长密钥", type='password')

def qrcode_token():
    if 'qr_url' not in st.session_state:
        qr_url, qr_id = get_qr_code() # You need to set this from somewhere
        st.session_state['qr_url'] = qr_url
        st.session_state['qr_id'] = qr_id
    else:
        qr_url = st.session_state['qr_url']
        qr_id = st.session_state['qr_id']
    # st.write('qrurl')
    # st.write(qr_url)
    st.image(qr_url)

    if st.button('更新'):
        token = check_login(qr_id)
        if 'access_token' in token:
            # print('token', token)
            update_token(0, 'bearer ' + token['access_token'])
            st.success('更新成功')


if key:
    if key == '输入自己的密码':
        file_name = get_filename()
        team_info = load_json(file_name)
        donate_info = load_json('/home/NewTeamWeb/team_info/donate.json')
        qrcode_token()
        player_id = st.text_input("请输入玩家id")
        if player_id:
            
            num = st.text_input('修改玩家的枫叶数')
            coin_info = load_json('/home/NewTeamWeb/team_info/player_maple.json')
            if st.button('修改枫叶'):
                if '+' in num or '-' in num:
                    coin_info[player_id] += int(num)
                else:
                    coin_info[player_id] = int(num)
                save_json('/home/NewTeamWeb/team_info/player_maple.json', coin_info)
                st.success('修改成功')

            if st.button('他充钱了'):
                
                team_info[player_id]['IsVIP'] = int(team_info[player_id]['IsVIP']) + 31     # int(False) = 0
                if player_id not in donate_info:
                    donate_info[player_id] = {'donate_items':[]}
                if player_id != '4115034':
                    for i, k in enumerate(donate_info[player_id]['donate_items']):
                        if '元' in k:
                            rmb_origin = float(k.rstrip('元'))
                            donate_info[player_id]['donate_items'][i] = '%.2f元' % (rmb_origin + 9.9)
                            break
                    else:
                        donate_info[player_id]['donate_items'] += ['%.2f元' % 9.9]
                save_json(f'/home/NewTeamWeb/json_log/{file_name}', team_info)
                st.success('收到')

            display_player_info(player_id)
        
        juanwang_add = st.text_input('输入卷王参赛者')
        juanwang_info = load_json('/home/NewTeamWeb/team_info/juanwang.json')
        
        if st.button('添加卷王参赛者'):
            if juanwang_add:
                if juanwang_add in team_info:
                    juanwang_info['参赛者'].append(juanwang_add)
                    if juanwang_add != '4115034':
                        for i, k in enumerate(donate_info[juanwang_add]['donate_items']):
                            if '元' in k:
                                rmb_origin = float(k.rstrip('元'))
                                donate_info[juanwang_add]['donate_items'][i] = '%.2f元' % (rmb_origin + 3)
                                break
                        else:
                            donate_info[juanwang_add]['donate_items'] += ['%.2f元' % 3]

                    st.success('添加成功')
                    save_json('/home/NewTeamWeb/team_info/juanwang.json', juanwang_info)
                else:
                    st.error('队伍中没有这个人')
            else:
                st.error('还没有输入信息')

        if st.button('卷王抽取'):
            juanwang_info['卷王'] = random.choice(juanwang_info['参赛者'])
            st.success(f"抽取完成，本月卷王:{team_info[juanwang_info['卷王']]['UserName']}")
            save_json('/home/NewTeamWeb/team_info/juanwang.json', juanwang_info)

        if st.button('重置卷王排行榜'):
            juanwang_info = {
                "卷王": "0",
                "参赛者": []
            }
            save_json('/home/NewTeamWeb/team_info/juanwang.json', juanwang_info)

        st.write('输入内容 id,赞助内容，假如赞助内容是金额，输入多少多少元，如果是其他东西，可以把所有赞助内容用+连接')
        zanzhu = st.text_input('输入赞助者, 赞助金额')
        
        if st.button('确认赞助'):
            player, money = zanzhu.split(',')
            # money = float(money)
            
            if player not in donate_info:
                donate_info[player] = {'donate_items':[]}
            if player == '4115034':
                donate_info[player] += float(money.rstrip('元'))
            else:
                if '元' in money:
                    rmb = float(money.rstrip('元'))
                    for i, k in enumerate(donate_info[player]['donate_items']):
                        if '元' in k:
                            rmb_origin = float(k.rstrip('元'))
                            donate_info[player]['donate_items'][i] = '%.2f元' % (rmb_origin + rmb)
                            break
                    else:
                        donate_info[player]['donate_items'] += ['%.2f元' % rmb]
                else:
                    donate_info[player]['donate_items'] += money.split('+')
            save_json('/home/NewTeamWeb/team_info/donate.json', donate_info)
            st.success('设置成功')



    elif key == '其他人的密钥':
        second_leader = load_json('/home/NewTeamWeb/team_info/second_leader.json')
        
        inp = st.text_input('输入自己的id')
        if inp:
            if inp in second_leader['white_list']:
                if inp not in second_leader['cur_list']:
                    give = inp
                    remove = second_leader['cur_list'].pop(0)
                    second_leader['cur_list'].append(give)
                    print('give', give, 'remove', remove, 'curlist', second_leader['cur_list'])
                    url1 = f'https://dancedemo.shenghuayule.com/Dance/api/Team/OperateTeam?opType=8&receiverId={remove}'
                    url2 = f'https://dancedemo.shenghuayule.com/Dance/api/Team/OperateTeam?opType=7&receiverId={give}'
                    url3 = f'https://dancedemo.shenghuayule.com/Dance/api/Team/OperateTeam?opType=12&receiverId={remove}'
                    leader_token = get_players_token(0)
                    request_url(leader_token, 'post', url1) # 摘副队
                    request_url(leader_token, 'post', url2) # 给副队
                    if remove not in ['543471']:
                        request_url(leader_token, 'post', url3) # 给精英
                    print('seconde', second_leader)
                    save_json('/home/NewTeamWeb/team_info/second_leader.json', second_leader)
                    st.success('修改成功')
                else:
                    st.error('你已经是副队啦！')
            else:
                st.error('只能给副队白名单的人哦')

        st.subheader('当前副队:')
        for i in second_leader['cur_list']:
            display_player_info(i, key=i)
    else:
        st.error('这个只能队长用哦')

