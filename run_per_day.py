import json
from utils import request_url, get_filename, get_players_token, save_json, load_json
import datetime
from glob import glob
import requests


def check_month_last_day(date_str):
    year = int(date_str.split('_')[0])
    feb_day =  '02_29' if year % 400 == 0 or (year % 100 != 0 and year % 4 == 0) else '02_28'
    last_day = ['01_31', feb_day, '03_31', '04_30', '05_31', '06_30', '07_31', '08_31', '09_30', '10_31', '11_30', '12_31']
    for day in last_day:
        if day in date_str:
            return True
    return False

def change_elite(team_info, maple_info, token):
    elite_info = load_json('/home/NewTeamWeb/team_info/second_leader.json')
    team_ids = set(team_info.keys())

    elite_info['formal_elite'] = [
        player for player in elite_info['formal_elite']
        if player['player_id'] in team_ids
    ]

    elite_info['temp_elite'] = [
        pid for pid in elite_info['temp_elite']
        if pid in team_ids
    ]

            
    # 获取所有精英
    all_elite = elite_info['temp_elite'] + [formal_elite['player_id'] for formal_elite in elite_info['formal_elite']]
    
    # 给每个精英结算枫叶
    for player_id in all_elite:
        if player_id not in maple_info:
            maple_info[player_id] = 0
        maple_info[player_id] += int(team_info[player_id]['PointCurMonth'] * 0.1)

    # 去掉近3月内不满足要求的精英
    for formal_elite in elite_info['formal_elite']:
        player_id = formal_elite['player_id']
        formal_elite['recent_3_months_point'] = formal_elite['recent_3_months_point'] + [team_info[player_id]['PointCurMonth']]
        formal_elite['recent_3_months_point'] = formal_elite['recent_3_months_point'][1:]
        if sum(formal_elite['recent_3_months_point']) < 3000:
            url = f'https://dancedemo.shenghuayule.com/Dance/api/Team/OperateTeam?opType=13&receiverId={player_id}'
            request_url(token, 'post', url)

    # 清除不满足条件的流动精英
    remove_list = []
    for player_id in elite_info['temp_elite']:
        if team_info[player_id]['PointCurMonth'] < 25000 and team_info[player_id]['GoldCurMonth'] < 20000:
            url = f'https://dancedemo.shenghuayule.com/Dance/api/Team/OperateTeam?opType=13&receiverId={player_id}'
            request_url(token, 'post', url)
            remove_list.remove(player_id)
    for player_id in remove_list:
        elite_info['temp_elite'].remove(player_id)

    # 增加满足条件的流动精英
    for player_id in team_info:
        if team_info[player_id]['MemberTypeText'] == '普通成员' and (team_info[player_id]['PointCurMonth'] >= 25000 or team_info[player_id]['GoldCurMonth'] >= 20000):
            url = f'https://dancedemo.shenghuayule.com/Dance/api/Team/OperateTeam?opType=12&receiverId={player_id}'
            request_url(token, 'post', url)
            elite_info['temp_elite'].append(player_id)
    
    save_json('/home/NewTeamWeb/team_info/second_leader.json', elite_info)
    

def save_data(flag=True):
    file_name = get_filename('/home/NewTeamWeb/json_log')
    lastest_sequence_number, lastest_date = file_name.rstrip('.json').split('-')
    date_str = datetime.datetime.now().strftime('%Y_%m_%d')  # 获取当前日期并格式化
    if lastest_date != date_str:
        sequence_number = int(lastest_sequence_number) + 1
    else:
        sequence_number = int(lastest_sequence_number)

    token = get_players_token(0)
    coin_url = 'https://dancedemo.shenghuayule.com/Dance/api/Team/GetContributionList?teamId=8716&orderby=1'
    team_url = 'https://dancedemo.shenghuayule.com/Dance/api/Team/GetTeamMemberList?teamId=8716&orderby=2&ordertype=0&pagesize=200&getPointCurMonth=true'

    coin_info = request_url(token, 'get', coin_url)
    team_info = request_url(token, 'get', team_url)
    # print(team_info)
    # print('team_info', team_info)
    team_info = {str(info['UserID']): info for info in team_info}
    lastest_team_info = load_json(f'/home/NewTeamWeb/json_log/{lastest_sequence_number}-{lastest_date}.json')

    maple_info = load_json('/home/NewTeamWeb/team_info/player_maple.json')
    for info in coin_info:
        player_id = str(info['UserID'])
        team_info[player_id]['GoldTotal'] = info['GoldTotal']
        team_info[player_id]['GoldCurMonth'] = info['GoldCurMonth']
        
        # 月供金币转枫叶
        if player_id in lastest_team_info:
            
            if player_id not in maple_info:
                maple_info[player_id] = 0

            maple_info[player_id] += info['GoldTotal'] - lastest_team_info[player_id]['GoldTotal']

            # 月卡每日登陆(顺手借用上面的if判断)
            if lastest_team_info[player_id]['IsVIP'] and flag:
                if team_info[player_id]['LastAccessText'] == '今日':
                    maple_info[player_id] += 1000
                    print('player id', player_id, 'maple +1000')
                team_info[player_id]['IsVIP'] = lastest_team_info[player_id]['IsVIP'] - 1
            else:
                team_info[player_id]['IsVIP'] = lastest_team_info[player_id]['IsVIP']
                        
        else:
            maple_info[player_id] = info['GoldTotal']

    
    if flag and check_month_last_day(date_str):
        top_30 = dict(sorted(team_info.items(), key=lambda item: item[1]['PointCurMonth'], reverse=True)[:30])
        print('top_30', top_30)
        for id, prize in zip(top_30, [30000, 25000, 20000, 15000, 10000, 5000, 3000, 2000, 1000, 500] + [300] * 10 + [200] * 10):
            maple_info[id] += prize
        
        # 月底更换精英
        change_elite(team_info, maple_info, token)


    save_json('/home/NewTeamWeb/team_info/player_maple.json', maple_info)
    save_json(f'/home/NewTeamWeb/json_log/{sequence_number}-{date_str}.json', team_info)


    # 更新退队的成员
    print('更新退队成员')
    elite_info = load_json('/home/NewTeamWeb/team_info/second_leader.json')
    team_ids = set(team_info.keys())

    elite_info['formal_elite'] = [
        player for player in elite_info['formal_elite']
        if player['player_id'] in team_ids
    ]

    elite_info['temp_elite'] = [
        pid for pid in elite_info['temp_elite']
        if pid in team_ids
    ]
    print('更新完成')
    save_json('/home/NewTeamWeb/team_info/second_leader.json', elite_info)

    return team_info

def refresh_token():
    token_list = glob('/home/NewTeamWeb/player_tokens_json/*')
    for json_path in token_list:
        data = load_json(json_path)
        json_data = {
            'client_type': 'qrcode',
            'grant_type': 'refresh_token',
            'refresh_token': data['refresh_token']
            }
        url = "https://dancedemo.shenghuayule.com/Dance/token"
        response = requests.post(url=url, data=json_data)
        d = response.json()
        if 'refresh_token' in d:
            save_json(json_path, d)

def calculate_win_times(player_id):
    token = get_players_token(0)
    cnt_win = 0
    cnt_times = 0
    page = 1
    y_list = ['2025']
    date_list = ['01-22', '01-23', '01-24', '01-25', '01-26', '01-27', '01-28', '01-29', '01-30', '01-31', 
                 '02-01', '02-02', '02-03', '02-04', '02-05', '02-06', '02-07', '02-08', '02-09', '02-10', '02-11', '02-12']
    # m_list = ['01', '02']
    # d_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
    while True:
        url = f'https://dancedemo.shenghuayule.com/Dance/api/Match/GetMatchListByUser?matchType=1&page={page}&pageSize=20&userId={player_id}&matchDefineID=2'
        data = request_url(token, 'get', url, hide_print=True)
        page += 1
        if data:
            if data['List'] == []:
                return cnt_win, cnt_times
            for record in data['List']:
                y, m, d = record['EndTime'].split(' ')[0].split('-')
                if y in y_list and f'{m}-{d}' in date_list:
                    cnt_times += 1
                    if record['IsWinner']:
                        cnt_win += 1
                else:
                    return cnt_win, cnt_times
        else:
            return cnt_win, cnt_times
    return cnt_win, cnt_times



if __name__ == '__main__':
    # 这个py文件会每天晚上执行一次，来保存这个数据，不过你手动运行也可以更新今天的数据
    save_data()
    refresh_token()
