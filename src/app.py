import streamlit as st
from pathlib import Path
import tempfile
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage

from utils import extract_pdf_text

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Tender Analyst",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

/* Global reset */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* App background */
.stApp {
    background-color: #0f1117;
    color: #e8e6e0;
}

/* Hide default Streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #161820;
    border-right: 1px solid #2a2d38;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

/* Logo / title */
.brand-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    color: #e8e6e0;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin-bottom: 0.2rem;
}
.brand-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #5a6072;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* Section labels */
.sidebar-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: #5a6072;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    margin-top: 1.5rem;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background-color: #1c1f2a !important;
    border: 1px dashed #2e3244 !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #c9a84c !important;
}

/* Status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    padding: 4px 10px;
    border-radius: 20px;
    margin-top: 0.5rem;
}
.status-ready {
    background: rgba(201, 168, 76, 0.12);
    color: #c9a84c;
    border: 1px solid rgba(201, 168, 76, 0.3);
}
.status-idle {
    background: rgba(90, 96, 114, 0.15);
    color: #5a6072;
    border: 1px solid rgba(90, 96, 114, 0.25);
}

/* Main header */
.main-header {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #e8e6e0;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}
.main-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    color: #5a6072;
    margin-bottom: 2rem;
    font-weight: 300;
}

/* Chat messages */
.chat-wrapper {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding-bottom: 1rem;
}

/* User message */
.msg-user {
    display: flex;
    justify-content: flex-end;
}
.msg-user .bubble {
    background: #1e2235;
    border: 1px solid #2e3244;
    border-radius: 16px 16px 4px 16px;
    padding: 0.75rem 1rem;
    max-width: 75%;
    font-size: 0.88rem;
    color: #c8c6c0;
    line-height: 1.6;
}

/* Assistant message */
.msg-assistant {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 0.6rem;
}
.msg-icon {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    background: linear-gradient(135deg, #c9a84c 0%, #9b7a2e 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    flex-shrink: 0;
    margin-top: 2px;
}
.msg-assistant .bubble {
    background: #161820;
    border: 1px solid #2a2d38;
    border-radius: 4px 16px 16px 16px;
    padding: 0.9rem 1.1rem;
    max-width: 85%;
    font-size: 0.875rem;
    color: #d4d2cc;
    line-height: 1.7;
}

/* Markdown inside bubbles */
.msg-assistant .bubble h1,
.msg-assistant .bubble h2,
.msg-assistant .bubble h3 {
    font-family: 'DM Serif Display', serif;
    color: #e8e6e0;
    margin-top: 0.8rem;
    margin-bottom: 0.3rem;
}
.msg-assistant .bubble h2 { font-size: 1rem; }
.msg-assistant .bubble h3 { font-size: 0.9rem; }
.msg-assistant .bubble strong { color: #c9a84c; font-weight: 500; }
.msg-assistant .bubble ul, .msg-assistant .bubble ol {
    padding-left: 1.2rem;
    margin: 0.3rem 0;
}
.msg-assistant .bubble li { margin-bottom: 0.2rem; }
.msg-assistant .bubble code {
    font-family: 'DM Mono', monospace;
    background: #1e2235;
    padding: 1px 5px;
    border-radius: 4px;
    font-size: 0.8rem;
}
.msg-assistant .bubble hr {
    border-color: #2a2d38;
    margin: 0.6rem 0;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #3a3f52;
}
.empty-state .icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
.empty-state .title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.2rem;
    color: #4a5068;
    margin-bottom: 0.4rem;
}
.empty-state .hint {
    font-size: 0.8rem;
    color: #3a3f52;
    font-weight: 300;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #2a2d38;
    margin: 1rem 0;
}

/* Input area override */
[data-testid="stChatInput"] {
    background-color: #161820 !important;
    border: 1px solid #2a2d38 !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #c9a84c !important;
    box-shadow: 0 0 0 2px rgba(201, 168, 76, 0.12) !important;
}

/* Analyze button */
.stButton > button {
    background: linear-gradient(135deg, #c9a84c 0%, #9b7a2e 100%);
    color: #0f1117;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.85rem;
    padding: 0.5rem 1.2rem;
    width: 100%;
    transition: opacity 0.2s;
}
.stButton > button:hover {
    opacity: 0.85;
    border: none;
}
.stButton > button:disabled {
    background: #2a2d38;
    color: #5a6072;
}

/* Spinner color */
[data-testid="stSpinner"] { color: #c9a84c; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2d38; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────

MODEL = "llama-3.1-8b-instant"
TEMP = 0.0

SYSTEM_PROMPT = """
You are an AI assistant that helps users analyze Indian tender documents.

Your responsibilities:
- Summarize tender documents clearly.
- Extract important information accurately.
- Help users understand requirements, deadlines, costs, and risks.
- Answer questions ONLY using the provided tender context.
- If information is missing, explicitly say so.
- Do not hallucinate details that are not present in the tender.

When summarizing a tender, focus on:
- Tender title
- Tender reference number
- Department/organization
- Scope of work
- Estimated project cost
- EMD/security deposit
- Eligibility criteria
- Important deadlines
- Completion period
- Technical requirements
- Financial requirements
- Risks, penalties, or SLA clauses

Be concise, structured, and professional.
"""

INITIAL_ANALYSIS_PROMPT = """
Here is the tender document context:

{tender_text}

Return the following sections:

1. Critical Information
- Tender reference number
- Important dates
- Submission deadlines
- EMD
- Tender fees

2. Qualification Criteria
- Eligibility requirements
- Financial turnover requirements
- Certifications required
- Prior experience requirements

3. Technical Proposal Requirements
- Technical specifications
- Deliverables
- Timeline expectations

4. SLA and Commercial Terms
- Penalties
- Payment terms
- Commercial clauses
- Risky or unusual conditions

5. Risks and Red Flags
- Missing information
- Strict qualification barriers
- High penalties
- Ambiguous clauses

Only use information explicitly present in the tender. If information is unavailable, state so clearly.
Return the output in structured markdown.
"""

# ── Session state init ────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages: list[BaseMessage] = [
        SystemMessage(content=SYSTEM_PROMPT)
    ]
if "chat_history" not in st.session_state:
    # List of {"role": "user"|"assistant", "content": str}
    st.session_state.chat_history = []
if "tender_loaded" not in st.session_state:
    st.session_state.tender_loaded = False
if "tender_filename" not in st.session_state:
    st.session_state.tender_filename = None

# ── LLM init ──────────────────────────────────────────────────────────────────

load_dotenv()

@st.cache_resource
def get_llm():
    return ChatGroq(model=MODEL, temperature=TEMP)

llm = get_llm()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="brand-title">Tender<br>Analyst</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">AI-Powered Analysis</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Upload Document</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        label="tender_pdf",
        type=["pdf"],
        label_visibility="collapsed",
        help="Upload a tender PDF to begin analysis",
    )

    if st.session_state.tender_loaded and st.session_state.tender_filename:
        st.markdown(
            f'<div class="status-badge status-ready">● {st.session_state.tender_filename}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-badge status-idle">○ No document loaded</div>',
            unsafe_allow_html=True,
        )

    analyze_disabled = uploaded_file is None

    st.markdown('<div class="sidebar-label">Actions</div>', unsafe_allow_html=True)

    if st.button("Analyze Tender", disabled=analyze_disabled, use_container_width=True):
        with st.spinner("Extracting and analyzing…"):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                tender_pages = extract_pdf_text(tmp_path)
                os.unlink(tmp_path)

                tender_text = "\n\n".join(tender_pages)

                # Reset conversation
                st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
                st.session_state.chat_history = []

                # Build initial analysis message
                initial_msg = INITIAL_ANALYSIS_PROMPT.format(tender_text=tender_text)
                st.session_state.messages.append(HumanMessage(content=initial_msg))

                # Stream response
                full_response = ""
                for chunk in llm.stream(st.session_state.messages):
                    full_response += str(chunk.content or "")

                st.session_state.messages.append(AIMessage(content=full_response))

                # Store in visible chat (don't show the giant prompt, just the reply)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": full_response,
                })

                st.session_state.tender_loaded = True
                st.session_state.tender_filename = uploaded_file.name
                st.rerun()

            except Exception as e:
                st.error(f"Failed to process PDF: {e}")

    if st.session_state.tender_loaded:
        if st.button("Clear & Reset", use_container_width=True):
            st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
            st.session_state.chat_history = []
            st.session_state.tender_loaded = False
            st.session_state.tender_filename = None
            st.rerun()

    # Sidebar footer info
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(
        '<span style="font-family:\'DM Mono\',monospace;font-size:0.62rem;color:#3a3f52;">'
        f'Model: {MODEL}<br>Temp: {TEMP}</span>',
        unsafe_allow_html=True,
    )

# ── Main area ─────────────────────────────────────────────────────────────────

st.markdown('<div class="main-header">Tender Analysis</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="main-sub">Upload a tender PDF, run the initial analysis, then ask follow-up questions.</div>',
    unsafe_allow_html=True,
)
st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# Chat display
chat_container = st.container()

with chat_container:
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">📋</div>
            <div class="title">No tender loaded</div>
            <div class="hint">Upload a PDF in the sidebar and click <strong>Analyze Tender</strong> to begin.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="msg-user">
                    <div class="bubble">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Use st.chat_message for proper markdown rendering inside assistant bubbles
                with st.chat_message("assistant", avatar="📋"):
                    st.markdown(msg["content"])

# Chat input (only active when tender is loaded)
if st.session_state.tender_loaded:
    user_input = st.chat_input("Ask a follow-up question about the tender…")

    if user_input:
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.messages.append(HumanMessage(content=user_input))

        # Stream assistant response
        with st.spinner(""):
            full_response = ""
            for chunk in llm.stream(st.session_state.messages):
                full_response += str(chunk.content or "")

        st.session_state.messages.append(AIMessage(content=full_response))
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})
        st.rerun()
else:
    st.chat_input("Upload and analyze a tender to start chatting…", disabled=True)
