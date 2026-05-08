# memory_manager.py
import os
import datetime

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter

CACHE_DIR = "./huggingface_models"

embeddings = HuggingFaceEmbeddings(
    model_name="shibing624/text2vec-base-chinese",
    cache_folder=CACHE_DIR
)

PERSIST_DIR = "./daemon_memory_db"

def get_vector_store():
    if not os.path.exists(PERSIST_DIR):
        os.makedirs(PERSIST_DIR)
    return Chroma(
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR
    )

def add_memory(user_id, conversation_text):
    vector_store = get_vector_store()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30)
    docs = text_splitter.create_documents([conversation_text])
    for doc in docs:
        doc.metadata = {
            "user_id": user_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
    if docs:
        vector_store.add_documents(docs)
        print(f"  📝 记忆已存储 (user: {user_id})")

def recall_memory(user_id, query, top_k=3):
    vector_store = get_vector_store()
    try:
        results = vector_store.similarity_search(query, k=top_k, filter={"user_id": user_id})
        if results:
            memories = [doc.page_content for doc in results]
            return "【以下是你与主人的过往记忆】\n" + "\n".join(f"- {m}" for m in memories)
    except Exception as e:
        print(f"  ⚠️ 记忆检索失败: {e}")
    return ""

def clear_memory(user_id):
    vector_store = get_vector_store()
    try:
        results = vector_store.get(where={"user_id": user_id})
        if results and results["ids"]:
            vector_store.delete(ids=results["ids"])
            print(f"  🗑️ 已清空 {user_id} 的所有记忆")
    except Exception as e:
        print(f"  ⚠️ 清空记忆失败: {e}")
