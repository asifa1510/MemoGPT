import streamlit as st
import speech_recognition as sr
from langchain_community.llms import Ollama
from memory import get_chat_history, save_chat_history, list_chatrooms

st.set_page_config(page_title= "MemoGPT" ,layout="wide")
st.title("🧠 MemoGPT- your AI Assistant")

if "chatroom" not in st.session_state:
  st.session_state.chatroom=""
if "messages" not in st.session_state:
  st.session_state.messages=[]
if "input_key_id" not in st.session_state:
  st.session_state.input_key_id= 0

llm= Ollama(model="gemma:2b")

st.sidebar.header("📂 Chatrooms")
chatrooms= list_chatrooms()
selected= st.sidebar.selectbox("Select Chatroom", chatrooms + ["➕ New Chatroom"])

if selected== "➕ New Chatroom":
  new_chat= st.sidebar.text_input("Enter new Chatroom name:")
  if st.sidebar.button("Create") and new_chat:
    st.session_state.chatroom= new_chat
    st.session_state.messages=[]
    save_chat_history(new_chat,[])
    st.rerun()

else:
  if selected!= st.session_state.chatroom:
    st.session_state.chatroom= selected
    st.session_state.messages= get_chat_history(selected)

#UI
st.markdown(f: 💬 Chatroom: `{st.session_state.chatroom}`")
e= st.toggle("🎙️ Enable Voice Input")

chat_placeholder= st.container()
with chat_placeholder:
  for msg in st.session_state.messages:
    if msg["role"]== "user":
      st.markdown(
        f"<div style='text-align:right; background:#dcf8c6; color:#000; padding:10px; border-radius:10px; margin:5px 0; max-width:80%; margin-left:auto;'><b>🧑 You:</b><br>{msg['text']}</div>",
                unsafe_allow_html=True)
    else:
      st.markdown(
                f"<div style='text-align:left; background:#222; color:#eee; padding:10px; border-radius:10px; margin:5px 0; max-width:80%;'><b>🤖 MemoGPT:</b><br>{msg['text']}</div>",
                unsafe_allow_html=True)

#INPUT
col1,col2 = st.columns([8,2])
with col1:
  user_message= st.text_input("💬 Type your message", key=f"user_input_{st.session_state.input_key_id}")
with col2:
  send_clicked = st.button("📤 Send")

if voice_mode and st.button("🎙️ Speak Now"):  
  recognizer= sr.Recognizer()
  with sr.Microphone() as source:
    st.info("Listening...")
    audio= recognizer.listen(source)

  try:
    user_message= recognizer.recognize_google(audio)
    st.success(f"🗣️ You said: {user_message}")
    send_clicked= True
  except sr.UnknownValueError:
    st.error("Could'nt understand audio")
    user_message= ""
    send_clicked= False

if send_clicked and user_message.strip()!= "":
  user_message = user_message.strip()
  st.session_state.messages.append({"role": "user", "text": user_message})
  prompt = "\n".join([f"{m['role'].capitalize()}: {m['text']}" for m in st.session_state.messages]) + "\nAI:"
    try:
        response = llm(prompt)
    except Exception as e:
        st.error(f"LLM Error: {e}")
        response = "⚠️ Failed to generate response."

    st.session_state.messages.append({"role": "ai", "text": response})
    save_chat_history(st.session_state.chatroom, st.session_state.messages)

    st.session_state.input_key_id += 1
    st.rerun()

if st.button("🗑️ Clear Chatroom"):
    st.session_state.messages = []
    save_chat_history(st.session_state.chatroom, [])
    st.success("Chatroom cleared!")
    st.rerun()

  
    




