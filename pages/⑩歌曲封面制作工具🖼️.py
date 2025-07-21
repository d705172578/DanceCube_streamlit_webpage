import streamlit as st
from PIL import Image
import io

# 页面标题
st.title("歌曲封面制作工具🖼️")

# 上传图像文件
uploaded_file = st.file_uploader("选择一个图像文件", type=["jpg", "png", "jpeg"])

# 背景尺寸
background_width = 700
background_height = 808

if uploaded_file is not None:
    # 读取上传的图像
    image = Image.open(uploaded_file)

    # 获取图像的原始尺寸
    original_width, original_height = image.size

    # 获取最短边，自动调整其为700或808，保持宽高比
    if original_width < original_height:
        new_width = background_width
        new_height = int((original_height / original_width) * new_width)
    else:
        new_height = background_height
        new_width = int((original_width / original_height) * new_height)

    # 初始化图像：根据最短边调整大小
    image_resized = image.resize((new_width, new_height), Image.ANTIALIAS)

    # 获取调整后的图像尺寸
    width, height = image_resized.size
    
    # 数值输入参数
    scale_factor = st.number_input("缩放图像", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

    # 计算缩放后的图像尺寸
    new_width_scaled = int(width * scale_factor)
    new_height_scaled = int(height * scale_factor)

    # 以图像中心为基准缩放
    image_resized_centered = image_resized.resize((new_width_scaled, new_height_scaled), Image.ANTIALIAS)

    # 创建黑色背景
    result = Image.new("RGB", (background_width, background_height), (0, 0, 0))

    # 获取用户输入的左右移动和上下移动的偏移量
    horizontal_offset = st.number_input("左右移动", min_value=-int(background_width / 2), max_value=int(background_width / 2), value=0, step=1)
    vertical_offset = st.number_input("上下移动", min_value=-int(background_height / 2), max_value=int(background_height / 2), value=0, step=1)
    st.caption('温馨提示:你可以手动输入缩放尺寸和左右移动距离，输入框加减号进行微调')

    # 计算图像的左上角坐标，使得图像的中心对齐背景的中心，再加上偏移量
    left = (background_width - image_resized_centered.width) // 2 + horizontal_offset
    top = (background_height - image_resized_centered.height) // 2 + vertical_offset

    # 将缩放后的图像粘贴到黑色背景上
    result.paste(image_resized_centered, (left, top))

    # 设置最大文件大小
    max_size = 300 * 1024  # 300 KB

    # 尝试多次压缩，直到文件大小小于最大值
    quality = 95
    buffer = io.BytesIO()

    # 循环调整质量，直到文件大小小于 300 KB
    while True:
        buffer.seek(0)
        result.save(buffer, format="JPEG", quality=quality)
        size = buffer.tell()
        if size <= max_size or quality <= 10:
            break
        quality -= 5  # 降低质量以压缩文件大小

    buffer.seek(0)

    # 显示最终图像
    st.image(result, caption="调整后的图像", use_column_width=True)

    # 下载按钮
    st.download_button(
        label="下载调整后的图像",
        data=buffer,
        file_name="adjusted_image.jpg",
        mime="image/jpeg"
    )
