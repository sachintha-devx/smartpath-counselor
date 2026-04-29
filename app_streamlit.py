import streamlit as st
import time
import os
from dotenv import load_dotenv

from chatbot import get_response
from db import (
    create_table,
    save_chat,
    load_chat,
    get_all_chat_ids,
    save_chat_session,
    get_chat_titles,
    update_chat_title
)

# 🔥 ENV
load_dotenv()
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

create_table()

st.set_page_config(page_title="SmartPath Counselor", page_icon="🎓")

# 🔥 HEADER
col1, col2 = st.columns([1,6])

with col1:
    st.image("logo.png", width=70)

with col2:
    st.markdown("## 🎓 SmartPath Counselor")

# 🌗 THEME
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

colA, colB = st.columns([6,1])

with colB:
    if st.button("🌙" if st.session_state.theme == "dark" else "☀️"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

# 🎨 STYLE
if st.session_state.theme == "dark":
    st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { background-color: #1E1E1E; color: white; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: black; }
    .stChatMessage { background-color: #F1F1F1; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 🔹 LOAD CHAT
chat_ids = get_all_chat_ids()
chat_titles = get_chat_titles()

if not chat_ids:
    chat_ids = ["Chat 1"]
    save_chat_session("Chat 1", "New Chat")

st.session_state.chat_ids = chat_ids

# 🔥 START WITH NEW CHAT
if "current_chat" not in st.session_state:
    existing_ids = get_all_chat_ids()
    new_chat = f"Chat {len(existing_ids)+1}"
    save_chat_session(new_chat, "New Chat")
    st.session_state.current_chat = new_chat

# 🔹 MEMORY
if "messages" not in st.session_state:
    st.session_state.messages = {}

if "file_text" not in st.session_state:
    st.session_state.file_text = ""

# 🟣 SIDEBAR
with st.sidebar:
    st.image("logo.png", width=120)
    st.header("💬 Chats")

    uploaded_file = st.file_uploader("📎 Upload PDF or TXT", type=["pdf", "txt"])

    if uploaded_file:
        file_text = ""

        if uploaded_file.type == "application/pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    file_text += text
        else:
            file_text = uploaded_file.read().decode("utf-8")

        st.session_state.file_text = file_text
        st.success("✅ File uploaded")

    if st.button("➕ New Chat"):
        new_chat = f"Chat {len(chat_ids)+1}"
        save_chat_session(new_chat, "New Chat")
        st.session_state.current_chat = new_chat
        st.rerun()

    for i, chat in enumerate(chat_ids):
        title = chat_titles.get(chat, chat)
        if st.button(title, key=f"chat_{i}"):
            st.session_state.current_chat = chat
            st.rerun()

# 🔹 LOAD MESSAGES
if st.session_state.current_chat not in st.session_state.messages:
    old_data = load_chat(st.session_state.current_chat)
    st.session_state.messages[st.session_state.current_chat] = [
        {"role": role, "content": content} for role, content in old_data
    ]

messages = st.session_state.messages[st.session_state.current_chat]

# 💬 DISPLAY
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 🧾 INPUT
if prompt := st.chat_input("Ask about ICT courses..."):

    messages.append({"role": "user", "content": prompt})
    save_chat(st.session_state.current_chat, "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    if len(messages) == 1:
        update_chat_title(st.session_state.current_chat, prompt[:30])

    # 🧠 AI
    if st.session_state.file_text:
        prompt = f"{st.session_state.file_text[:3000]}\n\nQ: {prompt}"

    result = get_response(prompt)

    response_text = result.get("text")
    image_url = result.get("image")
    diagram_text = result.get("diagram")

    messages.append({"role": "assistant", "content": response_text})
    save_chat(st.session_state.current_chat, "assistant", response_text)

    # 🤖 DISPLAY RESPONSE
    with st.chat_message("assistant"):

        placeholder = st.empty()
        full_text = ""

        for char in response_text:
            full_text += char
            placeholder.markdown(full_text + "▌")
            time.sleep(0.003)

        placeholder.markdown(full_text)

        # 🖼️ IMAGE
        if image_url:
            try:
                st.image(image_url, caption="🖼️ Visual Explanation", width="stretch")
            except:
                st.warning("⚠️ Image failed")

        # 📊 DIAGRAM
        if diagram_text:
            st.markdown("### 📊 Diagram")
            st.code(diagram_text)

# 📌 FOOTER
st.markdown("""
---
<div style="text-align:center; font-size:14px; color:gray;">
© 2026 Sachintha Anjalo & Saranya | Esoft Metro Campus
</div>
""", unsafe_allow_html=True)