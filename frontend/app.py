import json
import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Food Receipt AI Agent")

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Chat Sessions")

    if st.button("+ New Chat", use_container_width=True):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.rerun()

    sessions = requests.get(f"{backend_url}/api/sessions").json()

    for session in sessions:
        if st.button(session["name"], key=session["session_id"], use_container_width=True):
            st.session_state.session_id = session["session_id"]
            history = requests.get(
                f"{backend_url}/api/sessions/{session['session_id']}/messages"
            ).json()
            st.session_state.messages = history["messages"]
            st.rerun()

    st.divider()
    st.header("Upload Receipt")

    uploaded_file = st.file_uploader("Receipt image", type=["png", "jpg", "jpeg"])

    if uploaded_file and st.button("Upload", use_container_width=True):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

        with st.spinner("Reading receipt..."):
            response = requests.post(f"{backend_url}/api/upload_receipt", files=files)

        st.success(response.json()["text"])

st.title("Food Receipt AI Agent")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask about your receipts...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        answer = ""

        response = requests.post(
            f"{backend_url}/api/chat",
            json={
                "user_input": user_input,
                "session_id": st.session_state.session_id,
            },
            stream=True,
        )

        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue

            event = json.loads(line[len("data: "):])

            if "session_id" in event:
                st.session_state.session_id = event["session_id"]
            elif "answer" in event:
                answer += event["answer"]
                placeholder.write(answer)
            elif "error" in event:
                answer = f"Error: {event['error']}"
                placeholder.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
