
import streamlit as st
from langchain_core.messages import SystemMessage
from core.config import SYSTEM_PROMPT

def init_session_state():
    """Initialize or reset session state variables."""
    if "messages" not in st.session_state or st.session_state.get("_reset", False):
        st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
        st.session_state.chat_history = []
        st.session_state.tender_loaded = False
        st.session_state.tender_filename = None
        st.session_state.tender_id = None
        st.session_state.extraction_result = None
        if "_reset" in st.session_state:
            del st.session_state["_reset"]

def reset_session():
    """Set reset flag and rerun to trigger fresh initialization."""
    st.session_state._reset = True
    st.rerun()
