# src/ui/sidebar.py
import streamlit as st
import tempfile
import os
from utils import extract_pdf_text
from langchain_core.messages import HumanMessage, AIMessage

from .styles import INITIAL_ANALYSIS_PROMPT, MODEL, TEMP


def render_sidebar():
    from .styles import SYSTEM_PROMPT   # avoid circular import

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

        # Status
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

        st.markdown('<div class="sidebar-label">Actions</div>', unsafe_allow_html=True)

        if st.button("Analyze Tender", disabled=uploaded_file is None, use_container_width=True):
            analyze_tender(uploaded_file)

        if st.session_state.tender_loaded:
            if st.button("Clear & Reset", use_container_width=True):
                reset_app()

        # Footer
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown(
            f'<span style="font-family:\'DM Mono\',monospace;font-size:0.62rem;color:#3a3f52;">'
            f'Model: {MODEL}<br>Temp: {TEMP}</span>',
            unsafe_allow_html=True,
        )


def analyze_tender(uploaded_file):
    llm = get_llm()   # we'll define this below or import

    with st.spinner("Extracting and analyzing…"):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            tender_pages = extract_pdf_text(tmp_path)
            os.unlink(tmp_path)

            tender_text = "\n\n".join(tender_pages)

            # Reset conversation
            from ui.styles import SYSTEM_PROMPT, INITIAL_ANALYSIS_PROMPT
            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

            st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
            st.session_state.chat_history = []

            initial_msg = INITIAL_ANALYSIS_PROMPT.format(tender_text=tender_text)
            st.session_state.messages.append(HumanMessage(content=initial_msg))

            full_response = ""
            for chunk in llm.stream(st.session_state.messages):
                full_response += str(chunk.content or "")

            st.session_state.messages.append(AIMessage(content=full_response))
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": full_response,
            })

            st.session_state.tender_loaded = True
            st.session_state.tender_filename = uploaded_file.name
            st.rerun()

        except Exception as e:
            st.error(f"Failed to process PDF: {e}")


def reset_app():
    from ui.styles import SYSTEM_PROMPT
    from langchain_core.messages import SystemMessage

    st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
    st.session_state.chat_history = []
    st.session_state.tender_loaded = False
    st.session_state.tender_filename = None
    st.rerun()


# Cache LLM
@st.cache_resource
def get_llm():
    from langchain_groq import ChatGroq
    return ChatGroq(model=MODEL, temperature=TEMP)
