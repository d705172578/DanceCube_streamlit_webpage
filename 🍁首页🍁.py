import streamlit as st
from utils import request_url, get_players_token, load_json, login
from data_process import DataAnalysis
import time

import pandas as pd
st.set_page_config(page_title="大枫树网", page_icon="🍁", layout="wide")

token = get_players_token(0)
coin_url = 'https://dancedemo.shenghuayule.com/Dance/api/Team/GetContributionList'
data = request_url(token, 'get', coin_url)

if not data:
    st.error('如果你看到这条信息，请联系队长更新token哦')

st.title('🍁大枫树战队官网🍁')

st.write('欢迎来到大枫树战队官网👋！')
st.write('战队官网新版本上线啦🥳\~')
st.write('点击左上角\'>\'就可以打开导航栏哦🧭\~')
st.write('下面让我来为大家介绍一下各个页面吧😉！')


st.write('')
st.subheader('①战队玩家信息表💯')
st.write('战队玩家信息表会展示该玩家在战队中的信息哦,包括积分和金币的总共与月供,战力值,上次活跃和登录时间以及入队时间')
st.markdown('**功能介绍**')
st.write('1.该表格每日会更新,你可以选择查看任意一天的表格信息')
st.write('2.通过点击表头可以对该列顺序进行排列')
st.write('3.表格右上角包含下载,搜索以及全屏的功能')
st.write('· 下载的文件是csv格式')
st.write('· 通过在搜索框输入内容可以在表格中展示出满足条件的单元格')
st.write('· 全屏可以更方便的查看该表格的信息')

st.write('')
st.subheader('②玩家信息查询🔎')
st.write('玩家信息查询可以通过输入玩家id号来查询某一玩家的信息哦')
st.markdown('**功能介绍**')
st.write('1.可以查看玩家的基本信息：头像、昵称、战队头衔、战力值、积分贡献信息、金币贡献信息、枫叶数等')
st.write('2.可以查看玩家的战力变化情况折线图')
st.write('3.可以查看玩家的活跃情况分布图')
st.write('4.可以查看玩家的能力面板(正在制作中)')


st.write('')
st.subheader('③战队商城🏬')
st.write('你可以在这里使用自己的枫叶来购买东西哦')
st.write('注:需要通过艾鲁获取自己的token,来查询自己的账户信息(仅用于确认本人操作)')
st.markdown('**功能介绍**')
st.write('1.你可以通过使用枫叶购买或赠送指定自制谱(仅限本战队队员)')
st.write('2.你可以通过使用枫叶购买游戏道具，如皮肤、奖励歌曲以及8速、9速等')
st.write('3.你可以通过使用枫叶兑换战队周边，如手套，吧唧，短袖，口罩，吉祥物娃娃')
st.write('**枫叶获得方式**')
st.write('1.玩家捐献的金币会在次日1:1转换为枫叶')
st.write('2.你可以通过参与战队活动来获得枫叶哦')
st.write('3.你可以通过购买月卡,每日签到都可以获得枫叶哦')

st.write('')
st.subheader('④战队活动记录📝')
st.write('这个页面记录了战队每次活动的内容，你可以在这里回顾战队举办的活动情况')

st.write('')
st.subheader('⑤歌曲标题制作工具♪')
st.write('这个页面可以供谱师大大们使用来制作歌曲标题图')

st.write('')
st.subheader('队长设置🔧')
st.write('这个页面仅队长可以使用，主要用于页面更新以及玩家信息的设置等')
