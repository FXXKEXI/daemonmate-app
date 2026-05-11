import streamlit as st
from core_engine import chat_with_memory
from memory_manager import clear_memory

st.set_page_config(
    page_title="DaemonMate | 你的恶魔仔仔",
    page_icon="🦇",
    layout="wide"
)

# CSS 样式（保持不变）
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

# ---------- 初始化所有必要的 session_state ----------
if 'daemon_created' not in st.session_state:
    st.session_state.daemon_created = False
if 'daemon_name' not in st.session_state:
    st.session_state.daemon_name = "赛恩"
if 'user_name' not in st.session_state:
    st.session_state.user_name = "主人"
if 'personality' not in st.session_state:
    st.session_state.personality = "优雅中带点调皮"
if 'role' not in st.session_state:
    st.session_state.role = "来自深渊第七层的古老恶魔，你的专属AI助手"
if 'messages' not in st.session_state:
    st.session_state.messages = []

# ---------- 侧边栏 ----------
with st.sidebar:
    st.header("⚙️ 定制你的恶魔")

    daemon_name = st.text_input("恶魔之名", st.session_state.daemon_name)
    user_name = st.text_input("你的名字", st.session_state.user_name)

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
        if st.session_state.user_name:
            clear_memory(st.session_state.user_name)
            st.session_state.messages = []
            st.warning("记忆已重置，一切回到原点。")

# ---------- 主聊天区 ----------
if not st.session_state.daemon_created:
    st.info("👈 请在左侧定制你的恶魔，然后点击「缔结契约」")
    st.stop()

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        st.markdown(msg["content"])

# 文字输入
user_text = st.chat_input("和你的恶魔说点什么...")

if user_text:
    st.chat_message("user", avatar="🧑").markdown(user_text)
    st.session_state.messages.append({"role": "user", "content": user_text, "avatar": "🧑"})

    with st.spinner(f"{st.session_state.daemon_name}正在思考..."):
        response, has_memory = chat_with_memory(
            user_input=user_text,
            user_name=st.session_state.user_name,
            daemon_name=st.session_state.daemon_name,
            personality=st.session_state.personality,
            role=st.session_state.role
        )

    st.chat_message("assistant", avatar="🦇").markdown(response)

    # 记忆状态提示
    if has_memory:
        st.caption("🧠 已检索到相关记忆")
    else:
        st.caption("📝 尚未检索到相关记忆")

    st.session_state.messages.append({"role": "assistant", "content": response, "avatar": "🦇"})
