import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from intent_detector import detect_intent, is_knowledge_mode, requires_web_search
from hollow_city.characters import get_echo
from hollow_city.emotion_engine import update_emotion
from hollow_city.memory_store import load_profile, recall_layers, save_profile, update_memory_layers
from hollow_city.prompt_builder import build_prompt
from hollow_city.relationship_engine import update_relationship
from hollow_city.world_state import update_world
from web_search import web_search


load_dotenv()

MISSING_API_KEY_MESSAGE = "请配置 API Key 后使用 AI 对话功能。"


def _get_secret(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st

        return st.secrets.get(name, "")
    except Exception:
        return ""


def _get_llm():
    api_key = _get_secret("DEEPSEEK_API_KEY")
    if not api_key:
        return None
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )


def _escape_prompt_template_text(text):
    return str(text).replace("{", "{{").replace("}", "}}")


def chat_with_echo(user_input, user_name, echo_id="NOX"):
    profile = load_profile(user_name, echo_id)
    echo = get_echo(profile.get("echo_id", echo_id))
    intent = detect_intent(user_input)
    knowledge_mode = is_knowledge_mode(intent)
    search_context = ""
    if requires_web_search(intent):
        search_context = web_search(user_input, max_results=5)

    emotion, signal, silence_hours = update_emotion(
        profile.get("emotion"),
        user_input,
        profile.get("relationship"),
    )
    relationship = update_relationship(
        profile.get("relationship"),
        emotion,
        signal,
        silence_hours,
    )
    world = update_world(profile.get("world"), emotion, relationship)
    memories = recall_layers(profile, user_input)

    system_prompt = build_prompt(
        echo=echo,
        emotion=emotion,
        relationship=relationship,
        world=world,
        memories=memories,
        user_name=user_name,
        intent=intent,
        knowledge_mode=knowledge_mode,
        search_context=search_context,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", _escape_prompt_template_text(system_prompt)),
        ("user", "{user_input}"),
    ])
    llm = _get_llm()
    if llm is None:
        return {
            "response": MISSING_API_KEY_MESSAGE,
            "has_memory": bool(memories),
            "emotion": emotion.to_dict(),
            "relationship": relationship.to_dict(),
            "world": world.to_dict(),
            "echo": echo.to_dict(),
            "intent": intent,
            "knowledge_mode": knowledge_mode,
            "search_context": search_context,
        }

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"user_input": user_input})

    profile["echo_id"] = echo.echo_id
    profile["emotion"] = emotion.to_dict()
    profile["relationship"] = relationship.to_dict()
    profile["world"] = world.to_dict()
    update_memory_layers(profile, user_input, response, emotion, relationship, signal)
    save_profile(user_name, profile)

    has_memory = any(
        memories.get(layer)
        for layer in ("semantic_memory", "emotional_memory", "episodic_memory", "relationship_memory", "recent_interactions")
    )
    return {
        "response": response,
        "has_memory": has_memory,
        "emotion": emotion.to_dict(),
        "relationship": relationship.to_dict(),
        "world": world.to_dict(),
        "echo": echo.to_dict(),
        "intent": intent,
        "knowledge_mode": knowledge_mode,
        "search_context": search_context,
    }


def chat_with_memory(user_input, user_name, daemon_name=None, personality=None, role=None):
    result = chat_with_echo(user_input=user_input, user_name=user_name, echo_id=daemon_name or "NOX")
    return result["response"], result["has_memory"]
