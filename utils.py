import requests
import json
import os
import re
import datetime
import base64
import streamlit as st
import time


# # 从本地获取指定玩家的token
# def get_players_token(player_id):
#     if not os.path.exists(f'/home/NewTeamWeb/player_tokens/{player_id}.txt'):
#         st.error('去\'个人信息查询页面\'→\'账号信息\'更新一下自己的token再来购买吧')
#     with open(f'/home/NewTeamWeb/player_tokens/{player_id}.txt', 'r') as f:
#         res = f.readline()
#     return res

def get_players_token(player_id):
    if player_id == 0:
        player_id = load_json('/home/NewTeamWeb/team_info/second_leader.json')['cur_leader']
    path = f'/home/NewTeamWeb/player_tokens_json/{player_id}.json'
    if not os.path.exists(path):
        st.error('没有存储你的信息哦，去个人信息页面扫码登录一下再来吧')
    data = load_json(path)
    return 'bearer ' + data['access_token']


# 通过token访问url
def request_url(token, operation, url, hide_print=True):
    headers = {
        "Authorization": token
    }
    response = requests.request(operation, url, headers=headers)

    if not hide_print:
        print('operat', operation, 'url', url, 'token', token)
        print('\n\n\n---response---\n\n\n', response)
    # print('status_code', response.status_code)
    if response.status_code == 200:
        if operation == 'get':
            data = response.json()  # 解析返回的JSON数据
            if not hide_print:
                print('成功获取数据')
            return data
        else:
            return
    else:
        if not hide_print:
            print(f"Error: {response.status_code}")


# 更新某玩家token
def update_token(player_id, new_token):
    # 查找并替换token行
    with open(f'/home/NewTeamWeb/player_tokens/{player_id}.txt', 'w') as file:
        file.write(new_token)
    print('更新token完成')


# 获取指定的文件名称，默认情况下返回序号最大的参数，当指定date的情况下，返回指定日期的文件
def get_filename(path='/home/NewTeamWeb/json_log', date=None):
    max_seq = -1
    max_file_name = None
    
    for file_name in os.listdir(path):
        match = re.match(r'(\d+)-(\d{4})_(\d{2})_(\d{2})\.json', file_name)
        if match:
            seq_number = int(match.group(1))
            file_date = datetime.date(int(match.group(2)), int(match.group(3)), int(match.group(4)))
            
            if date:
                # 如果提供了日期参数，检查文件日期是否与提供的日期匹配
                if date == file_date:
                    return file_name
            else:
                # 否则，更新最大序号和对应的文件名
                if seq_number > max_seq:
                    max_seq = seq_number
                    max_file_name = file_name
    return max_file_name

# 根据path载入json文件
def load_json(path):
    if '/' not in path:
        path = f'/home/NewTeamWeb/json_log/{path}'
    with open(path, 'r') as f:
        data = json.load(f)
    return data

# 保存json文件
def save_json(json_path, data):
    with open(json_path, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def is_team_member(player_id, data):
    for info in data:
        if player_id == info['UserID']:
            return True
   
    return False 

# 玩家登录使用
def login():
    token = get_players_token(0)
    coin_url = 'https://dancedemo.shenghuayule.com/Dance/api/Team/GetContributionList?orderby=1'
    data = request_url(token, 'get', coin_url)

    if not data:
        st.error('如果你看到这条信息，请联系队长更新token哦')
    else:
        st.write(f"请输入你的账号和密码")
        player_id = st.text_input("游戏ID")
        player_password = st.text_input("密码")
        password_dict = load_json('/home/NewTeamWeb/team_info/player_password.json')

        if st.button("登录"):
            if is_team_member(int(player_id), data):
                if player_id not in password_dict or password_dict[player_id] == "":
                    st.warning('记得去个人信息查询页面中给自己设置一个密码哦~')
                    time.sleep(0.5)
                    st.session_state['cur_user'] = player_id
                    st.rerun()
                else:
                    if password_dict[player_id] == player_password:
                        st.success('登录成功')
                        time.sleep(0.5)
                        st.session_state['cur_user'] = player_id
                        st.rerun()
                    else:
                        st.error('输入用户名或密码错误哦')
            else:
                st.error('需要本战队玩家才能登录哦')


def display_player_info(player_id, show_maple=True, key=1):
    from streamlit_card import card
    from data_process import DataAnalysis
    data_analysis = DataAnalysis()
    player_maple = load_json('/home/NewTeamWeb/team_info/player_maple.json')
    
    if player_id in data_analysis.info:
        player_info = data_analysis.info[player_id]
        if player_id not in player_maple:
            player_maple[player_id] = 0
            save_json('/home/NewTeamWeb/team_info/player_maple.json', player_maple)
        res = card(
            title="基本信息",
            text=[
                f"玩家名称: {player_info['UserName']}",
                f"总贡献: {player_info['PointTotal']}",
                f"当月贡献: {player_info['PointCurMonth']}",
                f"战力值: {player_info['LvRatio']}",
                f"头衔: {player_info['MemberTypeText']}",
                f"🍁枫叶数🍁: {player_maple[player_id]}" if show_maple else "",
                f"月卡剩余天数: {player_info['IsVIP']}天" if player_info['IsVIP'] else ""
            ],

            image=player_info['HeadimgURL'],
            styles={
                "card": {
                    "align-items": "left",  # Center align items vertically
                    "width": "200px",  # Width of the card
                    "height": "200px",  # Height of the card
                    "border-radius": "10px",
                    "box-shadow": "0 1px 0px rgba(0,0,0,0.1)",
                },

                "text": {
                    "font-family": "Arial, sans-serif",  # Customizable font
                    "font-size": "10px",  # Size of the text
                    "margin-left": "0px",  # Margin between the image and the text
                    "text-align": "left" 
                }
            },

            key=key
        )
    else:
        st.error('这个人不在战队哦,如果是刚加入战队的成员,需要等到今晚11点系统更新信息以后才能看到哦')


def buy_goods(goods_id, receiverId, num_buy):
    token = get_players_token(0)
    headers = {
        "Authorization": token
    }
    url = f'https://dancedemo.shenghuayule.com/Dance/api/Goods/BuyGoods?goodsId={goods_id}&payType=5&receiverId={receiverId}&amount={num_buy}'
    print('url', url)
    response = requests.request('post', url, headers=headers)
    print('\n\n----------\n\n', response.json())
    return response.status_code == 200


def search_music_goods_id(music_id):

    token = get_players_token(0)

    if int(music_id) > 20000:
        st.error('输入的歌曲id不对')
        return

    headers = {
        "Authorization": token
    }
    url = f'https://dancedemo.shenghuayule.com/Dance/api/Goods/GetGoodsMusic?page=1&pagesize=10&tag=&language=&orderby=1&ordertype=1&keyword={music_id}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()  # 解析返回的JSON数据
    else:
        st.error('token过期了呢，联系队长更新一下token吧')
        return
    
    if data['List'] == []:
        st.error('没有找到这首歌哦')
        return
    return data['List'][0]



def check_player_id(token, player_id):
    headers = {"Authorization": token}
    url = f'https://dancedemo.shenghuayule.com/Dance/api/User/GetAccountInfo?userId={player_id}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()  # 解析返回的JSON数据
        return str(data['UserID']) == player_id
    else:
        return False

def get_qr_code():
    # 发送GET请求以获取二维码信息
    response = requests.get("https://dancedemo.shenghuayule.com/Dance/api/Common/GetQrCode")
    if response.status_code == 200:
        # 解析响应中的数据
        qr_data = response.json()
        qr_url = qr_data['QrcodeUrl']  # 从响应中获取二维码URL
        qr_id = qr_data['ID']  # 从响应中获取二维码的ID，用作qr_token
        print('qr_data', qr_data)
        return qr_url, qr_id
    else:
        st.error("Failed to retrieve QR code.")
        return None, None
    
def check_login(qr_id):
    url = "https://dancedemo.shenghuayule.com/Dance/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Origin": "https://danceweb.shenghuayule.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://danceweb.shenghuayule.com/",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    data = {
        "client_type": "qrcode",
        "grant_type": "client_credentials",
        "client_id": qr_id
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        result = response.json()
        save_json(f"/home/NewTeamWeb/player_tokens_json/{result['userId']}.json", result)
        print('save_token_json', result['userId'])
    else:
        print('出错了',response.json())
        return None
    return result


if __name__ == '__main__':
    token = get_players_token(0)
    print(get_filename('/home/NewTeamWeb/json_log', date=datetime.date(2024,4,24)))