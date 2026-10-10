
import json
import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Food Receipt AI Agent",
    layout="wide",
)

# styling
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 6rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.15);
    }

    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: 0.65rem 0 !important;
    }

    [data-testid="stChatMessageContent"] {
        background: transparent !important;
    }

    [data-testid="stChatInput"] {
        border-radius: 14px;
    }

    div[data-testid="stButton"] > button {
        border: none;
        background: transparent;
        text-align: left;
        border-radius: 8px;
        transition: background 0.15s ease;
    }

    div[data-testid="stButton"] > button:hover {
        background: rgba(128, 128, 128, 0.12);
    }

    .app-subtitle {
        color: var(--text-color);
        opacity: 0.65;
        font-size: 0.95rem;
        margin-top: -0.6rem;
        margin-bottom: 2rem;
    }

    .sidebar-label {
        font-size: 0.8rem;
        font-weight: 600;
        opacity: 0.65;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# sidebar
with st.sidebar:
    st.markdown("## Food Receipt AI")
    st.caption("Your personal food expense assistant")

    if st.button("+ New Chat", use_container_width=True):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        '<p class="sidebar-label">Recent conversations</p>',
        unsafe_allow_html=True,
    )

    with st.container(height=280):
        sessions = requests.get(
            f"{backend_url}/api/sessions"
        ).json()

        for session in sessions:
            if st.button(
                session["name"],
                key=session["session_id"],
                use_container_width=True,
            ):
                st.session_state.session_id = session["session_id"]

                history = requests.get(
                    f"{backend_url}/api/sessions/"
                    f"{session['session_id']}/messages"
                ).json()

                st.session_state.messages = history["messages"]
                st.rerun()

    st.divider()

    st.markdown("### Upload Receipt")

    uploaded_file = st.file_uploader(
        "Receipt image",
        type=["png", "jpg", "jpeg"],
    )

    if uploaded_file and st.button(
        "Upload",
        use_container_width=True,
    ):
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type,
            )
        }

        try:
            with st.spinner("Reading receipt..."):
                response = requests.post(
                    f"{backend_url}/api/upload_receipt",
                    files=files,
                    timeout=180,
                )

            response.raise_for_status()

            result = response.json()
            st.success("Receipt processed successfully.")
            st.write(result["text"])

        except requests.exceptions.HTTPError:
            st.error(
                f"Upload failed: HTTP {response.status_code}"
            )
            st.code(response.text or "Empty response")

        except requests.exceptions.JSONDecodeError:
            st.error("Backend did not return valid JSON.")
            st.code(response.text or "Empty response")

        except requests.exceptions.RequestException as exc:
            st.error(f"Request failed: {exc}")


# main chat
st.title("Food Receipt AI Agent")

st.markdown(
    '<p class="app-subtitle">'
    'Ask questions about your receipts and food expenses.'
    '</p>',
    unsafe_allow_html=True,
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask about your receipts...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

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

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
