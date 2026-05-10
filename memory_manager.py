import json, os, datetime

MEMORY_DIR = "./memory_data"

def _get_user_file(user_id):
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)
    return os.path.join(MEMORY_DIR, f"{user_id}.json")

def _load_memories(user_id):
    file_path = _get_user_file(user_id)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def _save_memories(user_id, memories):
    file_path = _get_user_file(user_id)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)

def add_memory(user_id, conversation_text):
    memories = _load_memories(user_id)
    memories.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "content": conversation_text
    })
    if len(memories) > 200:
        memories = memories[-200:]
    _save_memories(user_id, memories)

def recall_memory(user_id, query, top_k=3):
    memories = _load_memories(user_id)
    if not memories:
        return ""
    keywords = query.lower().split()
    scored = []
    for mem in memories:
        content = mem["content"].lower()
        score = sum(1 for kw in keywords if kw in content)
        if score > 0:
            scored.append((score, mem))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]
    if top:
        result = "【以下是你与主人的过往记忆】\n"
        for _, mem in top:
            result += f"- {mem['content']}\n"
        return result
    return ""

def clear_memory(user_id):
    file_path = _get_user_file(user_id)
    if os.path.exists(file_path):
        os.remove(file_path)
