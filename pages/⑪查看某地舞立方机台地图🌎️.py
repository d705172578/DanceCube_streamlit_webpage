import streamlit as st
import pandas as pd
import requests
from geopy.distance import geodesic
import folium
from folium import IFrame
from streamlit_folium import st_folium
from utils import request_url, get_players_token
import os

# 设置页面标题
st.title("查询舞立方机台位置🌎️")
token = get_players_token(0)

# 设置头像缓存目录
CACHE_DIR = '/home/NewTeamWeb/avatar_cache'

# 创建缓存目录（如果不存在）
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def get_coordinates_baidu(location, ak):
    """
    使用百度地图 API 获取地址的经纬度
    :param location: 地点名称（例如：北京朝阳）
    :param ak: 百度地图 API 的密钥
    :return: 经纬度
    """
    url = f'http://api.map.baidu.com/geocoding/v3/?address={location}&output=json&ak={ak}'
    
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 0:
        lat = data['result']['location']['lat']
        lng = data['result']['location']['lng']
        return lat, lng
    else:
        return False

# 黑色默认图标路径
DEFAULT_ICON_PATH = os.path.join(CACHE_DIR, 'default_black_icon.jpg')

# 缓存用户头像
@st.cache_data
def get_user_avatar(user_id, token):
    """
    获取用户头像 URL并缓存
    :param user_id: 用户ID
    :param token: 用户令牌
    :return: 头像路径
    """
    avatar_path = os.path.join(CACHE_DIR, f"{user_id}.jpg")

    # 如果头像文件已缓存，直接返回路径
    if os.path.exists(avatar_path):
        return avatar_path

    # 如果没有缓存，从 API 请求头像
    user_info = request_url(token, 'get', f'https://dancedemo.shenghuayule.com/Dance/api/User/GetNickname?userId={user_id}')

    # 如果没有获取到头像URL，使用默认黑色图标
    if user_info is None or 'HeadimgURL' not in user_info:
        avatar_url = DEFAULT_ICON_PATH
    else:
        avatar_url = user_info['HeadimgURL']

    # 如果是有效的URL，下载并保存头像
    if avatar_url != DEFAULT_ICON_PATH:
        img_data = requests.get(avatar_url).content
        with open(avatar_path, 'wb') as f:
            f.write(img_data)
    else:
        # 如果是默认黑色图标，直接复制一个黑色图标到缓存
        if not os.path.exists(avatar_path):
            # 创建一个黑色的 30x30 图标（你可以调整大小）
            from PIL import Image
            black_icon = Image.new('RGB', (30, 30), color=(0, 0, 0))
            black_icon.save(avatar_path)

    return avatar_path

place = st.text_input('输入地点名称')
if place:
    ak = 'MliBM31Vp8EuMV8KyUazIq1BNWZLiQVo'
    coordinates = get_coordinates_baidu(place, ak)

    if coordinates:
        # 输入经纬度
        latitude = coordinates[0]
        longitude = coordinates[1]

        # 设置拉杆选择搜索距离范围 (单位：公里)
        max_distance_km = st.slider('选择最大搜索距离（公里）', 0, 100, 20)

        # 使用 st.columns 来并排显示复选框
        col1, col2, col3 = st.columns(3)  # 创建两个列

        with col1:
            display_machine_type_2nd = st.checkbox('显示一/二代机', value=True)
        
        with col2:
            display_machine_type_xiu = st.checkbox('显示秀机', value=True)

        with col3:
            display_offline = st.checkbox('显示离线机台', value=False)

        # 根据复选框的选择设置机台类型
        if display_machine_type_2nd and display_machine_type_xiu:
            display_type = [0, 1]
        elif display_machine_type_2nd:
            display_type = [0]
        elif display_machine_type_xiu:
            display_type = [1]
        else:
            display_type = []

        # 请求机器列表
        url = f'https://dancedemo.shenghuayule.com/Dance/OAuth/GetMachineListByLocation?lng={longitude}&lat={latitude}'
        res = requests.get(url).json()

        # 创建一个以百度地图返回的经纬度为中心的 Folium 地图
        m = folium.Map(location=[latitude, longitude], zoom_start=12)
        # folium.TileLayer('CartoDB positron').add_to(m)
        folium.TileLayer(
            tiles='http://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
            attr='高德地图',
            subdomains=['1', '2', '3', '4']  # 子域名
        ).add_to(m)

        for machine in res:
            machine_lat = machine['Latitude']
            machine_lng = machine['Longitude']
            distance_km = geodesic((latitude, longitude), (machine_lat, machine_lng)).kilometers

            # 如果机台在选择的距离范围内，且符合选择的机台类型，则添加
            if distance_km <= max_distance_km and machine['MachineType'] in display_type:
                if not display_offline and machine['Online'] == False:
                    continue
                usr_id = machine['LightUserID']

                # 获取头像路径
                avatar_path = get_user_avatar(usr_id, token)

                # gaode_url = f"http://uri.amap.com/marker?position={machine_lng},{machine_lat}&name={machine['Address']}&callnative=1"
                gaode_url2 = f'androidamap://navi?sourceApplication=MyApp&lat={machine_lat}&lon={machine_lng}&dev=0&style=2'
                gaode_url3 = f'androidamap://route?sourceApplication=微信&dlat={machine_lat}&dlon={machine_lng}&dname=目标地点&dev=0&t=0'
                # 创建一个带超链接的HTML框
                popup_html = f'''
                <div style="text-align: center;">
                    <a href="{gaode_url2}" target="_blank" style="font-size: 10px; color: purple; text-decoration: none;">导航过去</a>
                </div>
                '''

                popup_html = f'''
                <div style="
                    text-align: center;
                    font-size: 14px;
                    line-height: 1.5;
                    color: black;
                ">
                    <p>导航需要浏览器打开官网</p>
                    <a href="{gaode_url3}" target="_blank" style="
                        color: blue; 
                        text-decoration: none;
                    ">打开缺德地图</a>
                </div>
                '''
                popup = folium.Popup(popup_html, max_width=300)

                folium.Marker(
                    [machine_lat, machine_lng],
                    tooltip=machine['Address'],
                    popup=popup,
                    icon=folium.CustomIcon(icon_image=avatar_path, icon_size=(30, 30))
                ).add_to(m)

        # 在 Streamlit 中展示地图
        with st.spinner('正在加载地图，请稍等...'):
            st_data = st_folium(m, height=500, width=500)
            st.write(f"搜索范围: {max_distance_km} 公里内的机台")
    else:
        st.error('没有找到该位置，可能是描述不清楚，请提供更具体的地址')
