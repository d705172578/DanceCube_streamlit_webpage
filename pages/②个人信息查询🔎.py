import streamlit as st
from utils import get_qr_code, check_login, load_json, save_json, update_token, display_player_info, check_player_id
from run_per_day import save_data
import time
import requests

st.title('玩家信息查询')

def display_rank_plot():
    pass

if 'cur_user' not in st.session_state:
    if 'qr_url' not in st.session_state:
        qr_url, qr_id = get_qr_code() # You need to set this from somewhere
        st.session_state['qr_url'] = qr_url
        st.session_state['qr_id'] = qr_id
    else:
        qr_url = st.session_state['qr_url']
        qr_id = st.session_state['qr_id']
    st.write('手机用户长按下方二维码图片，然后扫描登录，显示登录成功后，后退到这个网页中再点击登录就好了')
    st.image(qr_url)

    if st.button('登录'):
        token = check_login(qr_id)
        if 'access_token' in token:
            
            team_info = save_data(flag=False)
            if str(token['userId']) in team_info:
                st.session_state['cur_user'] = str(token['userId'])
                update_token(st.session_state['cur_user'], f"bearer {token['access_token']}")
                st.rerun()
            else:
                st.error('只有本战队玩家才可以使用哦')
        else:
            st.error('没有获取到token,要先扫码后,再进行操作哦')
else:
    st.markdown(':rainbow[**欢迎回来~(迪拉熊语气)**]')
    player_id = st.session_state['cur_user']
    tab1, tab2, tab3 = st.tabs(["基础信息", "战力信息", "活动信息"])

    with tab1:
        display_player_info(player_id)
    
    with tab2:
        st.write('正在制作中')

    with tab3:
        st.write('目前还没有活动哦')



