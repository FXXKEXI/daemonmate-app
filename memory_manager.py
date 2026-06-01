from hollow_city.memory_store import clear_profile, extract_user_facts, load_profile, recall_layers, save_profile, update_memory_layers
from hollow_city.schemas import EmotionState, RelationshipState


def add_memory(user_id, conversation_text, user_input=None, assistant_response=None):
    profile = load_profile(user_id)
    emotion = EmotionState(**profile.get("emotion", {}))
    relationship = RelationshipState(**profile.get("relationship", {}))
    signal = {"manual": 1, "depth": 1}
    update_memory_layers(
        profile,
        user_input or conversation_text,
        assistant_response or "",
        emotion,
        relationship,
        signal,
    )
    save_profile(user_id, profile)


def _extract_facts(user_text):
    return extract_user_facts(user_text)


def recall_memory(user_id, query, top_k=4):
    profile = load_profile(user_id)
    memories = recall_layers(profile, query, top_k=top_k)
    lines = []

    if memories["semantic_memory"]:
        lines.append("【Semantic Memory：稳定事实】")
        lines.extend(
            f"- {item.get('content', '')} (importance={item.get('importance', '')})"
            for item in memories["semantic_memory"]
        )
    if memories["emotional_memory"]:
        lines.append("【Emotional Memory：情绪模式】")
        lines.extend(
            f"- {item.get('content', '')} (importance={item.get('importance', '')})"
            for item in memories["emotional_memory"]
        )
    if memories["episodic_memory"]:
        lines.append("【Episodic Memory：重要事件】")
        lines.extend(
            f"- {item.get('content', '')} (importance={item.get('importance', '')})"
            for item in memories["episodic_memory"]
        )
    if memories["relationship_memory"]:
        lines.append("【Relationship Memory：关系状态】")
        lines.append(str(memories["relationship_memory"]))
    if memories["recent_interactions"]:
        lines.append("【最近互动】")
        lines.extend(f"- {item.get('user', item.get('content', ''))}" for item in memories["recent_interactions"])

    return "\n".join(lines)


def get_memory_stats(user_id):
    profile = load_profile(user_id)
    layers = profile.get("memory_layers", {})
    return {
        "semantic_memory": len(layers.get("semantic_memory", [])),
        "emotional_memory": len(layers.get("emotional_memory", [])),
        "episodic_memory": len(layers.get("episodic_memory", [])),
        "relationship_memory": 1 if layers.get("relationship_memory") else 0,
        "recent_interactions": len(layers.get("recent_interactions", [])),
    }


def clear_memory(user_id):
    clear_profile(user_id)
    print(f"已清空 {user_id} 的 Hollow City 记忆")
