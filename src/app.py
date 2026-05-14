# src/app.py
import streamlit as st
from dotenv import load_dotenv

from ui.styles import apply_page_config_and_styles
from ui.sidebar import render_sidebar
from ui.chat import render_chat_area


def main():
    load_dotenv()
    apply_page_config_and_styles()

    # Initialize session state (moved here for clarity)
    init_session_state()

    # Render UI
    render_sidebar()
    render_chat_area()


def init_session_state():
    if "messages" not in st.session_state:
        from langchain_core.messages import SystemMessage
        from ui.styles import SYSTEM_PROMPT
        
        st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "tender_loaded" not in st.session_state:
        st.session_state.tender_loaded = False
    if "tender_filename" not in st.session_state:
        st.session_state.tender_filename = None


if __name__ == "__main__":
    main()
