import html as html_tools

import streamlit as st

from components.character_card import render_character_card
from components.intro_animation import render_intro_animation
from components.matching_result import render_matching_result
from components.resonance_test import render_resonance_test
from components.room_view import render_room_view
from core_engine import chat_with_echo
from hollow_city.characters import get_echo
from hollow_city.memory_store import clear_profile, load_profile, save_profile
from hollow_city.proactive_scheduler import schedule_proactive_interaction
from hollow_city.schemas import EmotionState, RelationshipState, WorldState
from room_state import ROOMS, action_for, get_room_state
from styles.css import get_global_css


VALID_STEPS = {"intro", "resonance_test", "matching_result", "room"}
DEFAULT_SCORES = {"SERAPH": 0, "NOX": 0, "MORI": 0}


def rerun():
    st.rerun()


def escape(value):
    return html_tools.escape(str(value or ""))


def set_step(step):
    st.session_state.current_step = step if step in VALID_STEPS else "intro"
    rerun()


def _query_echo():
    echo = st.query_params.get("echo")
    if isinstance(echo, list):
        echo = echo[0] if echo else None
    echo = str(echo or "").upper()
    return echo if echo in ROOMS else None


def init_state():
    query_echo = _query_echo()

    st.session_state.setdefault("intro_completed", False)
    st.session_state.setdefault("test_completed", False)
    st.session_state.setdefault("selected_character", None)
    st.session_state.setdefault("test_answers", [])
    st.session_state.setdefault("test_index", 0)
    st.session_state.setdefault("character_scores", DEFAULT_SCORES.copy())
    st.session_state.setdefault("match_percentages", DEFAULT_SCORES.copy())
    st.session_state.setdefault("match_result_text", "")
    st.session_state.setdefault("relationship_state", {})
    st.session_state.setdefault("room_state", {})
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("user_name", "Wanderer")
    st.session_state.setdefault("echo_id", None)

    if query_echo:
        st.session_state.selected_character = query_echo
        st.session_state.echo_id = query_echo
        st.session_state.test_completed = True
        st.session_state.intro_completed = True
        st.session_state.current_step = "room"
    elif st.session_state.get("test_completed") and st.session_state.get("selected_character"):
        st.session_state.setdefault("current_step", "room")
    else:
        st.session_state.setdefault("current_step", "intro")

    if st.session_state.current_step not in VALID_STEPS:
        st.session_state.current_step = "intro"

    if st.session_state.current_step == "resonance_test":
        st.session_state.test_completed = False
        st.session_state.selected_character = None
        st.session_state.echo_id = None

    if st.session_state.get("selected_character"):
        st.session_state.echo_id = st.session_state.selected_character


def reset_resonance_test():
    st.session_state.current_step = "resonance_test"
    st.session_state.test_completed = False
    st.session_state.selected_character = None
    st.session_state.echo_id = None
    st.session_state.test_answers = []
    st.session_state.test_index = 0
    st.session_state.character_scores = DEFAULT_SCORES.copy()
    st.session_state.match_percentages = DEFAULT_SCORES.copy()
    st.session_state.match_result_text = ""


def render_intro_page():
    render_intro_animation()
    st.write("")
    if st.button("开始回响测试", type="primary", use_container_width=True):
        st.session_state.intro_completed = True
        reset_resonance_test()
        rerun()


def synchronization(emotion, relationship, profile):
    memory_sync = profile.get("memory_layers", {}).get("relationship_memory", {}).get("synchronization")
    if memory_sync is not None:
        return int(memory_sync)
    return max(0, min(100, int((relationship.intimacy + emotion.trust + emotion.attachment) / 3)))


def render_bubble(role, content, action=None):
    safe_content = escape(content)
    if role == "user":
        st.markdown(f'<div class="bubble-row user"><div class="bubble user">{safe_content}</div></div>', unsafe_allow_html=True)
        return

    action_html = f'<div class="action-line">[{escape(action)}]</div>' if action else ""
    st.markdown(
        f'<div class="bubble-row echo"><div class="bubble echo">{action_html}{safe_content}</div></div>',
        unsafe_allow_html=True,
    )


def render_chat_history(character_id, mood):
    st.markdown('<div class="chat-stage">', unsafe_allow_html=True)
    if not st.session_state.messages:
        st.markdown(
            '<div class="proactive">房间里还没有对话。门已经开了，Echo 正在看着你。</div>',
            unsafe_allow_html=True,
        )
    for msg in st.session_state.messages:
        render_bubble(msg["role"], msg["content"], msg.get("action") or action_for(character_id, mood))
    st.markdown("</div>", unsafe_allow_html=True)


def render_room_page():
    character_id = st.session_state.get("selected_character") or st.session_state.get("echo_id")
    if character_id not in ROOMS:
        reset_resonance_test()
        rerun()

    st.session_state.echo_id = character_id
    echo = get_echo(character_id)
    profile = load_profile(st.session_state.user_name, character_id)
    emotion = EmotionState(**profile.get("emotion", {}))
    relationship = RelationshipState(**profile.get("relationship", {}))
    world = WorldState(**profile.get("world", {}))
    room = get_room_state(character_id, emotion.mood, emotion)
    sync = synchronization(emotion, relationship, profile)
    st.session_state.relationship_state = relationship.to_dict()
    st.session_state.room_state = room

    proactive_event = schedule_proactive_interaction(echo, emotion, relationship, world, profile=profile)
    if proactive_event.should_send:
        save_profile(st.session_state.user_name, profile)

    left, right = st.columns([0.34, 0.66], gap="large")
    with left:
        render_character_card(character_id, room, emotion, relationship, sync)
        st.write("")
        if st.button("重新进行回响测试", use_container_width=True):
            reset_resonance_test()
            rerun()
        if st.button("清空这段关系记忆", use_container_width=True):
            clear_profile(st.session_state.user_name)
            st.session_state.messages = []
            rerun()

    with right:
        render_room_view(room)
        if proactive_event.should_send:
            st.markdown(
                f'<div class="proactive">{escape(proactive_event.message)}<br><br><em>{escape(proactive_event.action)}. {escape(proactive_event.room_atmosphere)}</em></div>',
                unsafe_allow_html=True,
            )
        render_chat_history(character_id, emotion.mood)

    user_text = st.chat_input("推开门，说一句真正想说的话。")
    if user_text:
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.spinner(f"{room['name']} 正在听你说完..."):
            try:
                result = chat_with_echo(user_input=user_text, user_name=st.session_state.user_name, echo_id=character_id)
                response = result["response"]
                response_mood = result.get("emotion", {}).get("mood", emotion.mood)
            except Exception as exc:
                response_mood = emotion.mood
                response = f"连接深渊回声时出了点问题：{exc}"
        st.session_state.messages.append(
            {"role": "assistant", "content": response, "action": action_for(character_id, response_mood)}
        )
        rerun()


def render_sidebar():
    with st.sidebar:
        st.markdown("## ECHO ABYSS")
        st.caption("The Hollow City prototype")
        st.session_state.user_name = st.text_input("你的名字", st.session_state.user_name)
        st.markdown(f"**Current step:** `{st.session_state.current_step}`")
        if st.session_state.get("selected_character"):
            st.markdown(f"**Matched Echo:** {st.session_state.selected_character}")
        else:
            st.caption("完成回响共鸣测试后，城市会把你带到对应房间。")

        st.divider()
        st.caption("开发调试")
        if st.button("重新观看开场", use_container_width=True):
            st.session_state.current_step = "intro"
            st.session_state.intro_completed = False
            rerun()

        if st.button("重新进行回响测试", use_container_width=True):
            reset_resonance_test()
            rerun()


st.set_page_config(page_title="ECHO ABYSS / The Hollow City", page_icon="🌙", layout="wide")
st.markdown(get_global_css(), unsafe_allow_html=True)
init_state()
render_sidebar()

if st.session_state.current_step == "intro":
    render_intro_page()
elif st.session_state.current_step == "resonance_test":
    render_resonance_test()
elif st.session_state.current_step == "matching_result":
    render_matching_result()
else:
    render_room_page()
