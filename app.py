import os
import streamlit as st
from llm.groq_llama import stream_llama_chat
import requests
from dotenv import load_dotenv

LOGO_PATH = "assets/logo.png"

# Load .env for development
load_dotenv()
LS_API_KEY = os.getenv("LS_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

st.set_page_config(page_title="ライブストリームAPI先生", page_icon="🦙")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("Settings")
    livestorm_key = st.text_input("Livestorm API Key", value=LS_API_KEY, type="password", disabled=False)
    groq_key = st.text_input("Groq API Key", value=GROQ_API_KEY, type="password", disabled=False)
    ping_result = ""
    if st.button("Ping Livestorm API"):
        url = "https://api.livestorm.co/v1/ping"
        headers = {
            "accept": "application/json",
            "Authorization": livestorm_key
        }
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                ping_result = "Livestorm Connected ✅"
            else:
                ping_result = f"❌ Failed: {resp.status_code} - {resp.text}"
        except Exception as e:
            ping_result = f"❌ Error: {e}"
    if ping_result:
        st.info(ping_result)

# --- MAIN TITLE ---
st.markdown("""
# Livestorm API Sensei
""")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi! I'm your Livestorm API Sensei. How can I help you today?"}
    ]

# Display chat history
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant", avatar=LOGO_PATH).markdown(msg["content"])

# User input
if prompt := st.chat_input("Type your message..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    # Prepare messages for LLM backend
    groq_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state["messages"]
    ]

    response_text = ""
    with st.chat_message("assistant", avatar=LOGO_PATH):
        response_area = st.empty()
        for chunk in stream_llama_chat(groq_messages):
            response_text += chunk
            response_area.markdown(response_text)
    st.session_state["messages"].append({"role": "assistant", "content": response_text}) 