import os
# 指定 ffmpeg 路径（改成你自己的 bin 目录！）

import streamlit as st
from core_engine import chat_with_memory
from memory_manager import clear_memory
import whisper
from gtts import gTTS
import base64

st.set_page_config(
    page_title="DaemonMate | 你的恶魔仔仔",
    page_icon="🦇",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #1a1a2e; }
    .stChatMessage { background-color: #16213e !important; border-radius: 10px; padding: 10px; }
    .stTextInput > div > div > input { background-color: #0f3460; color: #e0e0e0; border: 1px solid #7b2cbf; }
    .stButton > button { background-color: #7b2cbf; color: white; border-radius: 8px; }
    h1, h2, h3, p, .stMarkdown { color: #c9ada7 !important; }
    .stChatMessageAvatar { background-color: #7b2cbf; }
</style>
""", unsafe_allow_html=True)

st.title("🦇 DaemonMate")
st.caption("召唤属于你的古老恶魔，缔结永恒契约")

# ---------- 加载 Whisper 模型 ----------
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

# ---------- 语音输入（用 Whisper 本地识别） ----------
def handle_speech_input():
    audio_data = st.audio_input(label="🎙️ 点击录音")
    if audio_data is not None:
        # 保存录音文件
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_data.getvalue())

        # 使用在线识别（无需 ffmpeg）
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.AudioFile("temp_audio.wav") as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio, language="zh-CN")
            return text
        except Exception as e:
            st.warning(f"语音识别失败: {e}")
            return None
    return None
# ---------- 语音输出（用 gtts） ----------


# ---------- 侧边栏 ----------
with st.sidebar:
    st.header("⚙️ 定制你的恶魔")

    daemon_name = st.text_input("恶魔之名", "赛恩")
    user_name = st.text_input("你的名字", "主人")

    personality_presets = [
        "优雅中带点调皮",
        "冷傲但温柔",
        "神秘莫测言简意赅",
        "古老威严偶尔温柔",
        "自成一派"
    ]
    personality_select = st.selectbox("性格特质", personality_presets)

    if personality_select == "自成一派":
        personality = st.text_input("请输入自定义性格", placeholder="例如：话多爱吐槽的哥特少女")
    else:
        personality = personality_select

    role_presets = [
        "来自深渊第七层的古老恶魔，你的专属AI助手",
        "掌管夜晚与星辰的暗夜伯爵",
        "封印千年的禁忌恶魔，被你意外唤醒",
        "来自异界的图书馆管理员，通晓万界知识",
        "自成一派"
    ]
    role_select = st.selectbox("背景身份", role_presets)

    if role_select == "自成一派":
        role = st.text_input("请输入自定义背景身份", placeholder="例如：地底咖啡馆的退休恶魔")
    else:
        role = role_select

    if st.button("✨ 缔结契约", type="primary", use_container_width=True):
        st.session_state.daemon_created = True
        st.session_state.daemon_name = daemon_name
        st.session_state.user_name = user_name
        st.session_state.personality = personality
        st.session_state.role = role
        st.session_state.messages = []
        st.success(f"契约成立！{daemon_name}已回应你的召唤。")

    st.divider()

    if st.button("🗑️ 重置记忆", use_container_width=True):
        if 'user_name' in st.session_state:
            clear_memory(st.session_state.user_name)
            st.session_state.messages = []
            st.warning("记忆已重置，一切回到原点。")

# ---------- 主聊天区 ----------
if 'daemon_created' not in st.session_state:
    st.info("👈 请在左侧定制你的恶魔，然后点击「缔结契约」")
    st.stop()

if 'messages' not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        st.markdown(msg["content"])

# ---------- 语音 + 文字输入 ----------
user_text = None
spoken_text = handle_speech_input()
if spoken_text:
    user_text = spoken_text
else:
    user_text = st.chat_input("和你的恶魔说点什么...")

if user_text:
    st.chat_message("user", avatar="🧑").markdown(user_text)
    st.session_state.messages.append({"role": "user", "content": user_text, "avatar": "🧑"})

    with st.spinner(f"{st.session_state.daemon_name}正在思考..."):
        response = chat_with_memory(
            user_input=user_text,
            user_name=st.session_state.user_name,
            daemon_name=st.session_state.daemon_name,
            personality=st.session_state.personality,
            role=st.session_state.role
        )

    st.chat_message("assistant", avatar="🦇").markdown(response)
    auto_speak(response)
    st.session_state.messages.append({"role": "assistant", "content": response, "avatar": "🦇"})
