import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import re
import os
import io


# 上传并保存字体文件
def save_uploaded_file(uploaded_file, directory):
    """将上传的字体文件保存到指定目录，并返回保存路径"""
    if uploaded_file is not None:
        # 创建目录（如果不存在的话）
        os.makedirs(directory, exist_ok=True)
        
        # 获取上传文件的原始文件名
        file_name = uploaded_file.name
        file_path = os.path.join(directory, file_name)
        
        # 保存文件，如果文件已存在会覆盖
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    return None


# def contains_chinese(text):
#     """检查文本中是否包含中文字符"""
#     pattern = re.compile(r'[\u4e00-\u9fff\uFF00-\uFFEF\u4E00-\u9FA5]+')
#     return bool(pattern.search(text))

def contains_chinese(text):
    """检查文本中是否包含简体中文字符"""
    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    return bool(pattern.search(text))

def contains_english(text):
    return text in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:'


def add_red_border(img):
    # 创建带有红色边框的新图像
    border_size = 1
    img_with_border = Image.new('RGBA', (img.width + border_size * 2, img.height + border_size * 2), (255, 0, 0, 100))
    img_with_border.paste(img, (border_size, border_size))
    return img_with_border


# def text_draw(draw, x, y, space, info, fill, font_size, chinese_font, english_font, stroke_width, stroke_fill):
#     last_offset = 0
#     for a in info:
#         final_font = chinese_font if not contains_english(a) else english_font
#         if '.otf' in final_font:
#             font = ImageFont.opType(final_font, font_size)
#         else:
#             font = ImageFont.truetype(final_font, font_size)
#         w, h = draw.textsize(a, font=font)
#         draw.text((x+last_offset, y), a, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
#         last_offset += (w+space)

def text_draw(draw, x, y, space, info, fill, font_size, chinese_font, english_font, special_font, stroke_width, stroke_fill):
    last_offset = 0
    for a in info:
        # 1. 首先检查字符是否是英文
        if contains_english(a):
            final_font = english_font
        # 2. 如果不是英文，检查是否是中文字符
        elif contains_chinese(a):
            final_font = chinese_font
        # 3. 如果既不是英文也不是中文，使用特殊字体
        else:
            final_font = special_font

        # 加载字体
        if '.otf' in final_font:
            font = ImageFont.opType(final_font, font_size)
        else:
            font = ImageFont.truetype(final_font, font_size)

        # 获取字体的宽高并绘制文本
        w, h = draw.textsize(a, font=font)
        draw.text((x + last_offset, y), a, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        last_offset += (w + space)


def calculate_offset(info, chinese_font, english_font, font_size):
    img = Image.new('RGBA', (384, 128), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    res_w = 0
    res_h = 0
    for a in info:
        final_font = chinese_font if not contains_english(a) else english_font
        if '.otf' in final_font:
            font = ImageFont.opType(final_font, font_size)
        else:
            font = ImageFont.truetype(final_font, font_size)
        w, h = draw.textsize(a, font=font)
        res_w += w
        res_h = max(res_h, h)
    return 64 - res_h // 2, 192 - res_w // 2


def create_image(composer, 
                    song, 
                    arranger, 
                    composer_size=20, 
                    song_size=24,
                    arranger_size=20, 
                    composer_offset=0,
                    song_offset=0, 
                    arranger_offset=0,
                    composer_offset2=0,
                    song_offset2=0, 
                    arranger_offset2=0,
                    outline_color='#777777', 
                    shadow_blur_radius=2,
                    fill_color='#ffffff',
                    shadow_color='#000000',
                    outline_size=1,
                    shadow_size=1,
                    composer_space=0,
                    song_space=0,
                    arranger_space=0,
                    chinese_font='',
                    english_font='',
                    special_font=''
                    ):

    img = Image.new('RGBA', (384, 128), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制带模糊效果的黑色轮廓
    if shadow_size > 0:
        shadow_size -= 1
        text_draw(draw, composer_offset2, composer_offset, space=composer_space, info=composer, fill=shadow_color, font_size=composer_size, chinese_font=chinese_font, english_font=english_font, special_font=special_font, stroke_width=shadow_size, stroke_fill=shadow_color)
        text_draw(draw, song_offset2, song_offset, space=song_space, info=song, fill=shadow_color, font_size=song_size, chinese_font=chinese_font, english_font=english_font, special_font=special_font, stroke_width=shadow_size, stroke_fill=shadow_color)
        text_draw(draw, arranger_offset2, arranger_offset, space=arranger_space, info=arranger, fill=shadow_color, font_size=arranger_size, chinese_font=chinese_font, english_font=english_font, special_font=special_font, stroke_width=shadow_size, stroke_fill=shadow_color)
    
    img = img.filter(ImageFilter.GaussianBlur(shadow_blur_radius))
    
    draw = ImageDraw.Draw(img)
    
    # 绘制文字
    text_draw(draw, composer_offset2, composer_offset, space=composer_space, info=composer, fill=fill_color, font_size=composer_size, chinese_font=chinese_font, english_font=english_font, special_font=special_font, stroke_width=outline_size, stroke_fill=outline_color)
    text_draw(draw, song_offset2, song_offset, space=song_space, info=song, fill=fill_color, font_size=song_size, chinese_font=chinese_font, english_font=english_font, special_font=special_font, stroke_width=outline_size, stroke_fill=outline_color)
    text_draw(draw, arranger_offset2, arranger_offset, space=arranger_space, info=arranger, fill=fill_color, font_size=arranger_size, chinese_font=chinese_font, english_font=english_font, special_font=special_font, stroke_width=outline_size, stroke_fill=outline_color)
   
    return img


def draw_text(text, font_path, font_size):
    # 创建画布
    img = Image.new('RGBA', (150, 50), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    font = ImageFont.truetype(font_path, font_size)
    
    # 计算文本大小和位置
    text_width, text_height = draw.textsize(text, font=font)
    
    # 绘制文本
    draw.text((0, 0), text, font=font, fill=(255, 0, 0))
    return img

def create_name_list(names, first_name):
    res = list(map(lambda x: x.split('.')[0], names))
    res.remove(first_name)
    return [first_name] + res

def song_display():
    # Streamlit网页布局
    st.title('歌曲信息图像生成器')

    chinese_names = os.listdir('/home/WLFReptilian/chinese_font')
    chinese_name_dict = dict([[i.split('.')[0], i.split('.')[-1]] for i in chinese_names])
    chinese_names = create_name_list(chinese_names, '迷你简粗倩')
    # chinese_names = ['迷你简粗倩'] + list(map(lambda x: x.split('.')[0], chinese_names))

    english_names = os.listdir('/home/WLFReptilian/english_font')
    english_name_dict = dict([[i.split('.')[0], i.split('.')[-1]] for i in english_names])
    english_names = create_name_list(english_names, 'ELEPHANT')
    # english_names = ['ELEPHANT'] + list(map(lambda x: x.split('.')[0], english_names))

    special_names = os.listdir('/home/WLFReptilian/special_font')
    special_name_dict = dict([[i.split('.')[0], i.split('.')[-1]] for i in special_names])
    special_names = create_name_list(special_names, '微软雅黑')
    # special_names = ['微软雅黑'] + list(map(lambda x: x.split('.')[0], special_names))

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["内容设置", "字体设置", "尺寸设置", "特效设置", "偏移设置"])
    
    with tab1:
        composer_name = st.text_input('谱师名称', '在这里输入谱师的名称')
        song_name = st.text_input('歌曲名称', '在这里输入歌曲的名称')
        arranger_name = st.text_input('曲师名称', '在这里输入曲师的名称')
    
    with tab2:
        col1, col2 = st.columns(2)
        chinese_font_path = None
        english_font_path = None
        special_font_path = None
        

        with col1:
            # 文件上传
            chinese_option = st.selectbox('中文字体设置', chinese_names)
            uploaded_chinese_font = st.file_uploader("上传中文字体", type=['ttf', 'otf'], key="chinese_font_uploader")
            # 使用上传的中文字体，如果没有上传则使用默认字体
            if uploaded_chinese_font:
                chinese_font_path = save_uploaded_file(uploaded_chinese_font, '/home/WLFReptilian/chinese_font')
                st.session_state.chinese_font = chinese_font_path
                st.write("中文字体上传成功！")
            else:
                st.session_state.chinese_font = f"/home/WLFReptilian/chinese_font/{chinese_option}.{chinese_name_dict[chinese_option]}"
            st.write('中文字体预览')
            st.image(draw_text('中文字体', st.session_state.chinese_font, 30))

        with col2:
            english_option = st.selectbox('英文文字体设置', english_names)
            uploaded_english_font = st.file_uploader("上传英文字体", type=['ttf', 'otf'], key="english_font_uploader")
            # 使用上传的英文字体，如果没有上传则使用默认字体
            if uploaded_english_font:
                english_font_path = save_uploaded_file(uploaded_english_font, '/home/WLFReptilian/english_font')
                st.session_state.english_font = english_font_path
                st.write("英文字体上传成功！")
            else:
                st.session_state.english_font = f"/home/WLFReptilian/english_font/{english_option}.{english_name_dict[english_option]}"
            st.write('英文字体预览')
            st.image(draw_text('AaBbCc', st.session_state.english_font, 30))

        with st.expander("注:特殊字体(如日文,韩文,特殊符号等)默认使用中文字体,如果中文字体库中没有这个字符,则使用特殊字体,你可以点击这个上传你的特殊字体"):
            # 上传特殊字体
            special_option = st.selectbox('特殊字体设置', special_names)
            uploaded_special_font = st.file_uploader("上传特殊字体(默认为微软雅黑)", type=['ttf', 'otf'], key="special_font_uploader")
            if uploaded_special_font:
                special_font_path = save_uploaded_file(uploaded_special_font, '/home/WLFReptilian/special_font')
                st.session_state.special_font = special_font_path
                st.write("特殊字体上传成功！")
            else:
                st.session_state.special_font = f"/home/WLFReptilian/special_font/{special_option}.{special_name_dict[special_option]}"

    with tab3:
        composer_size = st.slider('谱师名称字体大小', min_value=10, max_value=40, value=20)
        song_size = st.slider('歌曲名称字体大小', min_value=10, max_value=50, value=30)
        arranger_size = st.slider('曲师名称字体大小', min_value=10, max_value=40, value=20)
        composer_space = st.slider('谱师名称字体间距', min_value=-10, max_value=100, value=0)
        song_space = st.slider('歌曲名称字体间距', min_value=-10, max_value=100, value=0)
        arranger_space = st.slider('曲师名称字体间距', min_value=-10, max_value=100, value=0)

    with tab4:
        fill_color = st.color_picker('字体填充颜色', '#ffffff')
        outline_color = st.color_picker('字体轮廓颜色', '#777777')
        shadow_color = st.color_picker('字体阴影颜色', '#000000')
        outline_size = st.slider('轮廓尺寸', min_value=0, max_value=5, value=1)
        shadow_size = st.slider('阴影大小', min_value=0, max_value=5, value=1)
        shadow_blur_radius = st.slider('阴影模糊化', min_value=0, max_value=10, value=2)

    with tab5:
        chinese_font = st.session_state.chinese_font
        english_font = st.session_state.english_font
        composer_offset_value, composer_offset2_value = calculate_offset(composer_name, chinese_font, english_font, composer_size)
        song_offset_value, song_offset2_value = calculate_offset(song_name, chinese_font, english_font, song_size)
        arranger_offset_value, arranger_offset2_value = calculate_offset(arranger_name, chinese_font, english_font, arranger_size)
        composer_offset = st.slider('谱师名称字体垂直偏移', min_value=0, max_value=128, value=10)
        song_offset = st.slider('歌曲名称字体垂直偏移', min_value=0, max_value=128, value=song_offset_value)
        arranger_offset = st.slider('曲师名称字体垂直偏移', min_value=0, max_value=128, value=95)
        composer_offset2 = st.slider('谱师名称字体水平偏移', min_value=0, max_value=384, value=composer_offset2_value)
        song_offset2 = st.slider('歌曲名称字体水平偏移', min_value=0, max_value=384, value=song_offset2_value)
        arranger_offset2 = st.slider('曲师名称字体水平偏移', min_value=0, max_value=384, value=arranger_offset2_value)

    composer_size = int(composer_size)
    song_size = int(song_size)
    arranger_size = int(arranger_size)

    img = create_image(composer_name, 
                        song_name, 
                        arranger_name, 
                        composer_size, 
                        song_size, 
                        arranger_size, 
                        composer_offset,
                        song_offset, 
                        arranger_offset,
                        composer_offset2,
                        song_offset2, 
                        arranger_offset2,  
                        outline_color, 
                        shadow_blur_radius,
                        fill_color,
                        shadow_color,
                        outline_size,
                        shadow_size,
                        composer_space,
                        song_space,
                        arranger_space,
                        st.session_state.chinese_font,
                        st.session_state.english_font,
                        st.session_state.special_font
                        )
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    byte_img = buf.getvalue()

    st.image(img, caption='手机用户可以长按进行保存哦', use_column_width=True)
    
    # 下载按钮
    st.download_button(
        label="下载图像",
        data=byte_img,
        file_name="song_info.png",
        mime="image/png"
    )

song_display()
