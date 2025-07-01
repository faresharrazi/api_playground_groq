import os
import streamlit as st
from llm.groq_llama import stream_llama_chat

LOGO_PATH = "assets/logo.png"

st.set_page_config(page_title="ライブストリームAPI先生", page_icon="🦙")

# Only display the title, no logo or custom HTML
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