import streamlit as st
from utils import get_players_token, get_filename
import sys

sys.path.append('../')
from utils import get_players_token, request_url, save_json, update_token, get_qr_code, check_login, load_json, buy_goods, search_music_goods_id, display_player_info
import time
import pandas as pd
from run_per_day import save_data


def get_goodlist(page=0):
    url = 'https://dancedemo.shenghuayule.com/Dance/api/Goods/GetGoodsMusic?page=1&pagesize=10&tag=&language=&orderby=2&ordertype=2&hasShow=false&keyword='
    token = get_players_token(0)
    data = request_url(token, 'get', url)
    save_json('../test.json', data)

def player_maple_info(player_id):
    player_info = load_json(get_filename('/home/NewTeamWeb/json_log'))
    coin_info = load_json('/home/NewTeamWeb/team_info/player_maple.json')
    if player_info:
        st.write(f'玩家: {player_info[player_id]["UserName"]}')
        st.markdown(f'🍁枫叶数🍁: **:red[{coin_info[player_id]}]**', )
    return coin_info, player_info

def buy_songs(coin_info, player_id):
    st.subheader('购买自制谱')
    st.write('请输入想要购买的歌曲id,购买数量,接受id(可以给自己买，也可以送人哦)')
    music_id = st.text_input("输入歌曲id")
    if music_id:
        goods_info = search_music_goods_id(music_id)
        if goods_info == None:
            return
        name = goods_info['GoodsName']
        st.markdown("歌曲名称:")
        st.markdown(name)
        st.write(f"歌曲单价:")
        st.markdown(f"{goods_info['PriceSale']}🍁/{goods_info['ExpireUnitTypeText']}")

    num = st.text_input("输入想要购买的数量")

    if num:
        price = int(num) * int(goods_info['PriceSale'])
        st.write(f"购买需消耗{price}🍁（现在有{coin_info[player_id]}🍁）")
        if price > int(coin_info[player_id]):
            st.error('你买不了这么多哦')
            return
        
    receiverId = st.text_input("输入接收人")
    if receiverId:
        st.write(f"接收人:")
        display_player_info(receiverId, show_maple=False)

    
    if st.button('购买'):
        if music_id != '' and num !='' and receiverId!='':
            if buy_goods(goods_info['GoodsID'], receiverId, num):
                
                coin_info[player_id] -= price
                save_json('/home/NewTeamWeb/team_info/player_maple.json', coin_info)
                st.success(f"购买成功")
                
                time.sleep(0.5)
                st.rerun()
            else:
                st.error('点击太快啦！慢一点！（想要多次购买的话可以在上面修改购买数量哦）')
        else:
            st.error('你输入的信息不全哦')

def buy_gameitem(coin_info, player_id):
    st.subheader('购买游戏道具')
    st.write('当前商品列表')
    rows = []

    goods_info = load_json('/home/NewTeamWeb/team_info/game_item.json')
    
    st.write('通过下表查询商品id,输入购买数量,接受id(可以给自己买，也可以送人哦)')
    goods_id = st.text_input("输入商品id")
    if goods_id:
        if goods_id in goods_info:
            st.markdown(f"**商品名称**: {goods_info[goods_id]['name']}")
            st.markdown(f"**商品单价**: {goods_info[goods_id]['Price']}🍁")
            goods_num = st.text_input("输入想购买的数量")
            if goods_num:
                try:
                    # assert int(goods_num) >= 1
                    price = int(goods_num) * int(goods_info[goods_id]['Price'])
                    if goods_info[goods_id]['IsUnique'] and int(goods_num) > 1:
                        st.error('这个只能购买1个哦')
                    elif price > int(coin_info[player_id]):
                        st.error('你买不了这么多哦')
                    else:
                        st.write(f"购买需消耗{price}🍁（现在有{coin_info[player_id]}🍁）")
                        receiver = st.text_input("请输入接收人")
                        if receiver:
                            st.write(f"接收人:")
                            display_player_info(receiver, show_maple=False, key=2)
                            if st.button('点击这里购买'):
                                if goods_id != '' and goods_num !='' and receiver!='':
                                    if buy_goods(goods_id, receiver, goods_num):
                                        coin_info[player_id] -= price
                                        save_json('/home/NewTeamWeb/team_info/player_maple.json', coin_info)
                                        st.success(f"购买成功")
                                        time.sleep(0.5)
                                        st.rerun()
                                    else:
                                        st.error('点击太快啦！慢一点！（想要多次购买的话可以在上面修改购买数量哦）')
                                else:
                                    st.error('你输入的信息不全哦')
                except Exception as e:
                    st.error(e)
        else:
            st.error('输入的商品id不对哦, 请仔细看看下表')
        
        
    for goods in goods_info:
        # 将玩家信息添加到行列表中
        rows.append({
            '道具': goods_info[goods]['ImgURL'],
            '名称': goods_info[goods]['name'],
            'id': goods,
            '价格': f"{goods_info[goods]['Price']}🍁",
        })

    df = pd.DataFrame(rows)

    st.data_editor(
        df,
        column_config={"道具": st.column_config.ImageColumn("道具", width='small', help="点击道具可以查看大图哦")},
        disabled=df.columns,
        hide_index=True,
        use_container_width=True,
        key='game',
        height=925
    )

def display_team_goods():
    st.subheader('购买游戏道具(点击图片可以查看大图哦)')
    st.write('当前商品列表(购买请私聊队长)')
    rows = []

    goods_info = load_json('/home/NewTeamWeb/team_info/team_item.json')
        
    for goods in goods_info:
        img_url = goods_info[goods]['ImgURL'].replace("app/", "")
        full_img_url = f"http://localhost:8503/{img_url}"
        rows.append({
            '道具': full_img_url,
            '名称': goods,
            '价格': f"{goods_info[goods]['Price']}🍁",
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        column_config={
            "道具": st.column_config.ImageColumn("道具", width='small', help="点击道具可以查看大图哦")
        },
        hide_index=True,
        use_container_width=True,
        height=570,
    )


st.title('战队商城')

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
    player_id = st.session_state['cur_user']


    coin_info, player_info = player_maple_info(player_id)
    tab1, tab2, tab3, tab4, tab5= st.tabs(["自制谱购买", "游戏道具购买", "战队周边", "月卡", "抽奖"])
    with tab1:
        buy_songs(coin_info, player_id)
    
    with tab2:
        buy_gameitem(coin_info, player_id)

    with tab3:
        display_team_goods()

    with tab4:
        st.image('/home/NewTeamWeb/activity_img/yk.png')

    with tab5:
        st.write('正在制作中')

