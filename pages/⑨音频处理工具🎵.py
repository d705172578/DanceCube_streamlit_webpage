import subprocess
import os
import streamlit as st
from pydub import AudioSegment  # 用于处理音频文件
import io

import json
import base64
import struct
import binascii
import streamlit as st
from pydub import AudioSegment
from Crypto.Cipher import AES



def dump_ncm(file_path):
    # 固定的加密解密密钥
    core_key = binascii.a2b_hex("687A4852416D736F356B496E62617857")
    meta_key = binascii.a2b_hex("2331346C6A6B5F215C5D2630553C2728")
    
    # 用于去除填充的函数
    unpad = lambda s: s[0:-(s[-1] if type(s[-1]) == int else ord(s[-1]))]
    
    # 读取文件并检查头部
    f = open(file_path, 'rb')
    header = f.read(8)
    assert binascii.b2a_hex(header) == b'4354454e4644414d'
    f.seek(2, 1)  # 跳过一些字节
    
    # 获取密钥数据并解密
    key_length = struct.unpack('<I', bytes(f.read(4)))[0]
    key_data = f.read(key_length)
    key_data_array = bytearray(key_data)
    for i in range(0, len(key_data_array)): key_data_array[i] ^= 0x64
    key_data = bytes(key_data_array)
    
    cryptor = AES.new(core_key, AES.MODE_ECB)
    key_data = unpad(cryptor.decrypt(key_data))[17:]
    key_length = len(key_data)
    key_box = bytearray(range(256))
    
    c = 0
    last_byte = 0
    key_offset = 0
    for i in range(256):
        swap = key_box[i]
        c = (swap + last_byte + key_data[key_offset]) & 0xff
        key_offset += 1
        if key_offset >= key_length: key_offset = 0
        key_box[i] = key_box[c]
        key_box[c] = swap
        last_byte = c
    
    # 获取音频元数据并解密
    meta_length = struct.unpack('<I', bytes(f.read(4)))[0]
    meta_data = f.read(meta_length)
    meta_data_array = bytearray(meta_data)
    for i in range(0, len(meta_data_array)): meta_data_array[i] ^= 0x63
    meta_data = bytes(meta_data_array)
    meta_data = base64.b64decode(meta_data[22:])
    
    cryptor = AES.new(meta_key, AES.MODE_ECB)
    meta_data = unpad(cryptor.decrypt(meta_data)).decode('utf-8')[6:]
    meta_data = json.loads(meta_data)
    
    # 获取音频文件信息
    crc32 = struct.unpack('<I', bytes(f.read(4)))[0]
    f.seek(5, 1)
    image_size = struct.unpack('<I', bytes(f.read(4)))[0]
    image_data = f.read(image_size)
    
    # 获取音频文件名
    file_name = meta_data['musicName'] + '.' + meta_data['format']
    
    # 创建输出文件路径
    output_file_path = os.path.join(os.path.split(file_path)[0], file_name)
    
    # 解密音频文件内容
    m = open(output_file_path, 'wb')
    while True:
        chunk = bytearray(f.read(0x8000))
        chunk_length = len(chunk)
        if not chunk:
            break
        for i in range(1, chunk_length + 1):
            j = i & 0xff
            chunk[i - 1] ^= key_box[(key_box[j] + key_box[(key_box[j] + j) & 0xff]) & 0xff]
        m.write(chunk)
    m.close()
    f.close()
    return output_file_path


# 页面标题
st.title("音频处理工具🎵")

# 上传音频文件
uploaded_file = st.file_uploader("选择一个音频文件", type=["mp3", "wav", "flac", "ogg", "aac", "ncm"])

if uploaded_file is not None:
    st.write("已上传文件:", uploaded_file.name)
    
    # 如果是 .ncm 格式，解密它
    if uploaded_file.name.endswith(".ncm"):
        temp_file_path = f"temp_{uploaded_file.name}"
    
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(uploaded_file.getvalue())
        st.write("检测到 `.ncm` 文件，正在自动解密...")
        decrypted_path = dump_ncm(temp_file_path)

        if decrypted_path:
            st.write(f"解密成功: {decrypted_path}")
            audio = AudioSegment.from_file(decrypted_path)
        else:
            st.error("解密失败，请检查文件格式。")
            audio = None
        
        # 删除临时文件
        os.remove(temp_file_path)
        if os.path.exists(decrypted_path):
            os.remove(decrypted_path)
    else:
        # 如果是其他格式，直接读取
        audio_data = uploaded_file.read()
        audio = AudioSegment.from_file(io.BytesIO(audio_data))

    if audio:
        # 以下是你原先的处理音频的功能
        tab1, tab2, tab3, tab4 = st.tabs(["音频转换", "音频裁剪", "音频变速", "音量调整"])

        # 音频格式转换功能
        with tab1:
            st.header("音频格式转换")
            
            format_choice = st.selectbox(
                "选择转换后的音频格式",
                ["mp3", "wav", "flac", "ogg", "aac"]
            )

            if st.button("转换"):
                # 将音频转换为所选格式
                output_buffer = io.BytesIO()
                audio.export(output_buffer, format=format_choice)

                # 生成新的文件名（去除原文件的扩展名，添加新的扩展名）
                original_filename = uploaded_file.name
                file_name_without_ext = original_filename.rsplit(".", 1)[0]  # 去除文件扩展名
                new_file_name = f"{file_name_without_ext}_converted.{format_choice}"

                # 生成下载链接
                st.write(f"转换成功！以下是您的 {format_choice} 格式音频文件：")

                # 将音频文件保存为下载链接
                output_buffer.seek(0)
                st.download_button(
                    label="下载转换后的音频",
                    data=output_buffer,
                    file_name=new_file_name,  # 使用动态生成的文件名
                    mime=f"audio/{format_choice}"
                )

        # 音频裁剪功能
        with tab2:
            st.header("音频裁剪")
            
            # 显示音频的时长（秒）
            audio_duration = len(audio) / 1000  # 转换为秒
            st.write(f"音频时长：{audio_duration:.2f}秒")

            start_time = st.number_input("开始时间 (秒)", min_value=0.0, max_value=audio_duration, value=0.0, step=0.1)
            end_time = st.number_input("结束时间 (秒)", min_value=start_time, max_value=audio_duration, value=audio_duration, step=0.1)

            if st.button("裁剪并下载"):
                # 裁剪音频
                start_ms = int(start_time * 1000)  # 转换为毫秒
                end_ms = int(end_time * 1000)  # 转换为毫秒
                cropped_audio = audio[start_ms:end_ms]

                # 将裁剪后的音频转换为mp3格式（可以根据需要修改格式）
                output_buffer = io.BytesIO()
                cropped_audio.export(output_buffer, format="mp3")

                # 生成新的文件名（去除原文件的扩展名，添加新的扩展名）
                original_filename = uploaded_file.name
                file_name_without_ext = original_filename.rsplit(".", 1)[0]  # 去除文件扩展名
                new_file_name = f"{file_name_without_ext}_cropped.mp3"

                # 生成下载链接
                st.write(f"裁剪成功！点击下方按钮下载裁剪后的音频文件：")

                # 将音频文件保存为下载链接
                output_buffer.seek(0)
                st.download_button(
                    label="下载裁剪后的音频",
                    data=output_buffer,
                    file_name=new_file_name,
                    mime="audio/mp3"
                )

        # 音频变速功能
        with tab3:
            st.header("音频变速")
            
            speed_factor = st.slider(
                "选择音频变速倍数",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.1,
                help="设置变速因子，1.0表示原速，<1.0表示减慢，>1.0表示加速"
            )

            if st.button("变速并下载"):
                st.write(f"变速需要一些时间(大约半分钟)，请稍等...")

                # 调整音频速度
                sped_audio = audio.speedup(playback_speed=speed_factor)

                # 将变速后的音频转换为mp3格式（可以根据需要修改格式）
                output_buffer = io.BytesIO()
                sped_audio.export(output_buffer, format="mp3")

                # 生成新的文件名（去除原文件的扩展名，添加新的扩展名）
                original_filename = uploaded_file.name
                file_name_without_ext = original_filename.rsplit(".", 1)[0]  # 去除文件扩展名
                new_file_name = f"{file_name_without_ext}_sped_{speed_factor}x.mp3"

                # 生成下载链接
                st.write(f"变速成功！点击下方按钮下载变速后的音频文件：")

                # 将音频文件保存为下载链接
                output_buffer.seek(0)
                st.download_button(
                    label="下载变速后的音频",
                    data=output_buffer,
                    file_name=new_file_name,
                    mime="audio/mp3"
                )

        # 音量调整功能
        with tab4:
            st.header("音量调整")

            # 显示当前音量增益
            gain = st.slider(
                "选择音量增益 (dB)",
                min_value=-20.0,
                max_value=20.0,
                value=0.0,
                step=1.0,
                help="调整音频的音量，负值表示降低音量，正值表示提高音量"
            )

            if st.button("调整音量并下载"):
                st.write(f"调整音量需要一些时间，请稍等...")

                # 调整音量
                adjusted_audio = audio + gain  # +或-可以调整音量，单位为dB

                # 将调整后的音频转换为mp3格式（可以根据需要修改格式）
                output_buffer = io.BytesIO()
                adjusted_audio.export(output_buffer, format="mp3")

                # 生成新的文件名（去除原文件的扩展名，添加新的扩展名）
                original_filename = uploaded_file.name
                file_name_without_ext = original_filename.rsplit(".", 1)[0]  # 去除文件扩展名
                new_file_name = f"{file_name_without_ext}_adjusted_{gain}dB.mp3"

                # 生成下载链接
                st.write(f"音量调整成功！点击下方按钮下载调整后的音频文件：")

                # 将音频文件保存为下载链接
                output_buffer.seek(0)
                st.download_button(
                    label="下载调整后的音频",
                    data=output_buffer,
                    file_name=new_file_name,
                    mime="audio/mp3"
                )
