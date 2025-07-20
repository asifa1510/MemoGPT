import os
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

MEMORY_DIR ="chatroom_memory"
os.makedirs(MEMORY_DIR, exist_ok= True)

embedding= HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_index_path(chatroom):
    return os.path.join(MEMORY_DIR, f"{chatroom}_index")

def load_vectorstore(chatroom):
    index_path = get_index_path(chatroom)
    if os.path.exists(index_path):
        return FAISS.load_local(index_path, embedding, allow_dangerous_deserialization=True)
    else:
        return FAISS.from_texts(["Hi! I'm MemoGPT. Ask me anything."], embedding)

def save_vectorstore(vectorstore, chatroom):
    vectorstore.save_local(get_index_path(chatroom))

def add_to_memory(text, chatroom):
    vectorstore = load_vectorstore(chatroom)
    vectorstore.add_texts([text])
    save_vectorstore(vectorstore, chatroom)

def get_conversation(query, chatroom):
    vectorstore = load_vectorstore(chatroom)
    docs = vectorstore.similarity_search(query, k=10)
    return [doc.page_content for doc in docs]


def get_chat_history(chatroom):
    history_path = os.path.join(MEMORY_DIR, f"{chatroom}.json")
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_chat_history(chatroom, history):
    history_path = os.path.join(MEMORY_DIR, f"{chatroom}.json")
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def list_chatrooms():
    files = os.listdir(MEMORY_DIR)
    chatrooms = set()
    for f in files:
        if f.endswith(".json"):
            chatrooms.add(f.replace(".json", ""))
        elif "_index" in f:
            chatrooms.add(f.replace("_index", ""))
    return sorted(list(chatrooms))
