import uuid
from datetime import datetime, timezone
from typing import Optional

import requests

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Data Analyst AI Agent", layout="wide", initial_sidebar_state="collapsed"
)

# --- Enhanced Styles ---
st.markdown(
    """
    <style>
    :root {
        --primary: #16a34a;
        --primary-dark: #15803d;
        --bg: #f8fafc;
        --card: #ffffff;
        --text: #0f172a;
        --text-muted: #64748b;
        --border: #e2e8f0;
        --success: #e6ffed;
        --error: #fee2e2;
    }

    * { box-sizing: border-box; }
    .stApp { background: var(--bg); }

    /* Remove Streamlit top menu/header whitespace and adjust app padding */
    header[data-testid="stHeader"] { display: none; }
    /* Streamlit may add a top padding to the main block; remove it */
    .css-18e3th9, .main, .block-container { padding-top: 0rem !important; margin-top: 0rem !important; }

    /* Header */
    .header-container {
        background: linear-gradient(135deg, #0f9d58 0%, #16a34a 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(15, 157, 88, 0.15);
    }
    .header-title { font-size: 28px; font-weight: 700; margin: 0; }
    .header-subtitle { font-size: 14px; opacity: 0.9; margin: 4px 0 0 0; }

    /* Sidebar & History */
    .sidebar-section { display: flex; flex-direction: column; background: var(--card); border-radius: 10px; padding: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .sidebar-title { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.8; }

    /* Scrollable recent chats list - keeps New Chat and title fixed */
    .recent-chats-list {
        flex: 1 1 auto !important;
        max-height: calc(100vh - 220px) !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        padding-right: 6px !important;
        margin-top: 6px !important;
    }
    .recent-chats-list::-webkit-scrollbar { width: 6px; }
    .recent-chats-list::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

    .new-chat-btn {
        width: 100%;
        padding: 10px;
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-bottom: 12px;
    }
    .new-chat-btn:hover { background: var(--primary-dark); transform: translateY(-2px); box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3); }

    /* Session row container - remove all spacing */
    .session-row {
        display: flex;
        gap: 6px;
        align-items: center;
        margin: 0 !important;
        padding: 0 !important;
        margin-bottom: 1px !important;
    }

    .session-item {
        flex: 1;
        padding: 0;
        background: transparent;
        border-radius: 0;
        margin: 0;
        cursor: pointer;
        border-left: 0;
        transition: all 0.12s ease;
        font-size: 12px;
        color: var(--text);
        word-break: break-word;
    }

    /* Hide any small empty rounded container Streamlit sometimes injects above buttons */
    .sidebar-section .stButton>div[role="button"]:empty, .sidebar-section .stButton>button:empty { display: none !important; }
    .sidebar-section > div[role="presentation"] { display: none !important; }
    .sidebar-section > div[aria-hidden="true"] { display: none !important; }
    .sidebar-section > div.css-1kidpj5 { display: none !important; }
    
    /* Remove all Streamlit-generated spacing */
    .sidebar-section > div { 
        margin: 0 !important; 
        padding: 0 !important; 
        gap: 0 !important;
    }
    
    .sidebar-section .stButton { 
        margin: 0 !important; 
        padding: 0 !important;
    }

    .session-item:hover { background: transparent; border-left: 0; }
    .session-item.active { background: var(--success); border-left: 0; font-weight: 500; }

    /* Session preview button wrapper */
    .session-item-wrapper {
        margin: 0 !important;
        padding: 0 !important;
        width: 100%;
    }

    .session-item-wrapper .stButton {
        margin: 0 !important;
        padding: 0 !important;
        width: 100%;
    }

    /* Compact preview button */
    .session-item-wrapper .stButton>button {
        background: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        padding: 5px 8px !important;
        text-align: left !important;
        font-weight: 400 !important;
        color: var(--text-muted) !important;
        box-shadow: none !important;
        width: 100% !important;
        white-space: normal !important;
        line-height: 1.2 !important;
        margin: 0 !important;
        display: block !important;
        font-size: 11px !important;
        height: auto !important;
        min-height: 32px !important;
    }

    .session-item-wrapper .stButton>button:hover {
        background: #fafafa !important;
        border-color: #d4d4d4 !important;
    }

    /* Compact delete button */
    .session-delete-btn {
        margin: 0 !important;
        padding: 0 !important;
    }

    .session-delete-btn .stButton {
        margin: 0 !important;
        padding: 0 !important;
    }

    .session-delete-btn .stButton>button {
        background: transparent !important;
        border: none !important;
        padding: 2px !important;
        width: 28px !important;
        height: 28px !important;
        min-height: 28px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: none !important;
        margin: 0 !important;
        font-size: 14px !important;
    }

    .session-delete-btn .stButton>button:hover {
        background: #fee2e2 !important;
        border-radius: 4px !important;
    }

    /* Chat Area */
    .chat-container { background: transparent; padding: 0; }

    .message-wrapper { display: flex; margin-bottom: 12px; width: 100%; }
    .message-wrapper.user { justify-content: flex-end; }
    .message-wrapper.assistant { justify-content: flex-start; }

    .message {
        padding: 12px 16px;
        border-radius: 12px;
        display: inline-block;
        min-width: 48px;
        white-space: normal;
        overflow-wrap: anywhere;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        font-size: 14px;
        line-height: 1.5;
    }

    .message.user { 
        background: var(--primary); 
        color: white; 
        border-radius: 16px 16px 4px 16px;
        max-width: 75%;
    }

    .message.assistant { 
        background: var(--card); 
        color: var(--text); 
        border: 1px solid var(--border); 
        border-radius: 16px 16px 16px 4px;
        width: fit-content;
        max-width: calc(100% - 20px);
    }

    .message-time { font-size: 11px; opacity: 0.7; margin-top: 4px; }

    /* Table styling inside messages */
    .message table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
    }

    .message table td,
    .message table th {
        padding: 6px 8px;
        border: 1px solid rgba(0,0,0,0.1);
        text-align: left;
    }

    .message table th {
        background: rgba(0,0,0,0.05);
        font-weight: 600;
    }

    /* Scrollable content for very wide tables */
    .message {
        overflow-x: auto;
    }

    /* Input Area */
    .input-container { border-top: 1px solid var(--border); padding-top: 16px; margin-top: 20px; }
    .input-wrapper { display: flex; gap: 10px; align-items: flex-end; }
    textarea { border: 1px solid var(--border) !important; border-radius: 10px !important; resize: vertical; }
    .send-button { background: var(--primary); color: white; padding: 10px 20px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s ease; }
    .send-button:hover { background: var(--primary-dark); transform: translateY(-1px); }
    .send-button:disabled { opacity: 0.5; cursor: not-allowed; }
    .input-container .stButton>button, .input-container .stButton>div[role="button"] { white-space: nowrap !important; min-width: 60px !important; }
    textarea[aria-label] { max-width: 100% !important; }
    textarea { min-height: 80px !important; }
    
    /* Send button styling */
    .input-container .stButton>button[title="↑"],
    .input-container .stButton>div[role="button"][title="↑"],
    .input-container .stButton>button[aria-label="↑"],
    .input-container .stButton>div[role="button"][aria-label="↑"] {
        background: linear-gradient(135deg, #0f9d58 0%, #16a34a 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        width: 56px !important;
        height: 56px !important;
        padding: 0 !important;
        border: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 28px !important;
        font-weight: 900 !important;
        box-shadow: 0 8px 20px rgba(15,157,88,0.18) !important;
        transition: all 0.16s ease !important;
        line-height: 1 !important;
    }

    .input-container .stButton>button[title="↑"]:hover,
    .input-container .stButton>div[role="button"][title="↑"]:hover,
    .input-container .stButton>button[aria-label="↑"]:hover,
    .input-container .stButton>div[role="button"][aria-label="↑"]:hover {
        background: linear-gradient(135deg, #0f9d58 0%, #15803d 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 28px rgba(15,157,88,0.28) !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--primary); }

    /* Reduce large bottom whitespace so page ends at the chat input */
    html, body, .stApp {
        height: auto !important;
        min-height: 0 !important;
    }

    /* Remove padding/margin and min-height Streamlit may add */
    .main, .block-container, .css-18e3th9 {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
        min-height: 0 !important;
    }

    /* Make chat container flush with bottom */
    .chat-container { padding-bottom: 0 !important; margin-bottom: 0 !important; }

    /* Hide Streamlit footer which reserves vertical space */
    footer[data-testid="stFooter"], footer {
        display: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# --- API Configuration ---
try:
    DEFAULT_API = st.secrets.get(
        "CHAT_API_URL", "https://excel-chatbot-rag.vercel.app/chat"
    )
except Exception:
    DEFAULT_API = "https://excel-chatbot-rag.vercel.app/chat"

# --- Session State ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.history = []
    st.session_state.api_url = DEFAULT_API
    # ensure sessions key exists for compatibility with older code
    if "sessions" not in st.session_state:
        st.session_state.sessions = []


def normalize_api_url(url: str) -> str:
    if not url:
        return url
    u = url.strip()
    if "#" in u:
        u = u.split("#")[0]
    if u.endswith("/docs"):
        u = u[:-5]
    if u.endswith("/docs/"):
        u = u[:-6]
    if not u.endswith("/chat"):
        u = u.rstrip("/") + "/chat"
    return u


st.session_state.api_url = normalize_api_url(st.session_state.api_url)


# --- Helper Functions ---
def add_message(role: str, content: Optional[str]):
    safe_content = content or ""
    st.session_state.history.append(
        {
            "role": role,
            "content": safe_content,
            "ts": datetime.now(timezone.utc).strftime("%H:%M"),
        }
    )


def start_new_session():
    # start a fresh session by resetting the session id and clearing history
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.history = []
def safe_rerun():
    """Call whichever rerun function is available across Streamlit versions.

    Uses getattr and a try/except around the call to avoid raising AttributeError
    if a stub or proxy weirdly exposes the name but the call fails.
    """
    for name in ("rerun", "experimental_rerun", "_rerun"):
        fn = getattr(st, name, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                # swallow errors from rerun implementations and continue trying
                try:
                    # last resort: ignore any exception
                    return None
                except Exception:
                    return None
    return None


def send_message(message: str) -> Optional[str]:
    try:
        payload = {
            "message": message.strip(),
            "stream": False,
            "session_id": st.session_state.session_id,
        }
        cookies = {"agent_session_id": st.session_state.session_id}
        response = requests.post(
            st.session_state.api_url, json=payload, timeout=120, cookies=cookies
        )

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                return data.get("agent_reply") or data.get("message")
            return str(data)
        else:
            return f"⚠️ API Error {response.status_code}: {response.text}"
    except requests.Timeout:
        return "⏱️ Request timeout. Please try again."
    except requests.ConnectionError:
        return (
            "❌ Cannot connect to API. Check the URL and ensure the server is running."
        )
    except Exception as e:
        return f"❌ Error: {str(e)}"
    


# --- Main Layout ---
st.markdown(
    "<div class='header-container'><h1 class='header-title'>📊 Data Analyst AI Agent</h1><p class='header-subtitle'>Ask questions about your tables</p></div>",
    unsafe_allow_html=True,
)

col_sidebar, col_main = st.columns([0.22, 0.78], gap="large")

# --- Left Sidebar ---
with col_sidebar:
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)

    if st.button("➕ New Chat", key="new_chat_btn", use_container_width=True):
        start_new_session()

    # Recent chats removed for a simplified UI
    st.markdown(
        "<div style='color: var(--text-muted); font-size: 13px; text-align: center; padding: 12px 0;'>Recent chats are disabled in this UI.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# --- Main Chat Area ---
with col_main:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    messages_container = st.container()

    with messages_container:
        if not st.session_state.history:
            st.markdown(
                "<div style='text-align: center; padding: 60px 20px; color: var(--text-muted);'>"
                "<div style='font-size: 48px; margin-bottom: 12px;'>💬</div>"
                "<div style='font-size: 16px; font-weight: 600; margin-bottom: 6px;'>Start a conversation</div>"
                "<div style='font-size: 13px;'>Ask questions about your data and get instant answers</div>"
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            for msg in st.session_state.history:
                role_class = "user" if msg["role"] == "user" else "assistant"
                st.markdown(
                    f"<div class='message-wrapper {role_class}'>"
                    f"<div><div class='message {role_class}'>{msg['content']}</div>"
                    f"<div class='message-time'>{msg['ts']}</div></div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)

    # Input Area
    st.markdown("<div class='input-container'>", unsafe_allow_html=True)

    with st.form(key="chat_form", clear_on_submit=True):
        col_input, col_send = st.columns([0.9, 0.1])

        with col_input:
            user_input = st.text_area(
                "Message",
                placeholder="Type your question here...",
                height=80,
                label_visibility="collapsed",
            )

        with col_send:
            st.write("")
            st.write("")
            send_btn = st.form_submit_button("↑", use_container_width=True)

        if send_btn and user_input.strip():
            add_message("user", user_input.strip())

            with st.spinner("Thinking..."):
                response = send_message(user_input.strip())
                add_message("assistant", response)

                safe_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# Inject JS to make Enter key submit the chat form
components.html(
    """
        <script>
        (function() {
            function bindSubmitOnEnter() {
                document.querySelectorAll('form').forEach(function(form){
                    if (form.__enterBound) return;
                    var textarea = form.querySelector('textarea');
                    var submit = form.querySelector('button[type="submit"]');
                    if (!textarea || !submit) return;
                    form.__enterBound = true;
                    textarea.addEventListener('keydown', function(e){
                        if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey && !e.altKey) {
                            e.preventDefault();
                            submit.click();
                        }
                    });
                });
            }
            bindSubmitOnEnter();
            var mo = new MutationObserver(function(){ bindSubmitOnEnter(); });
            mo.observe(document.body, { childList: true, subtree: true });
            
            // Recent chats removed: no additional DOM adjustments required
        })();
        </script>
        """,
    height=0,
)