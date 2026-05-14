# src/ui/chat.py
import streamlit as st

def render_chat_area():
    st.markdown('<div class="main-header">Tender Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-sub">Upload a tender PDF, run the initial analysis, then ask follow-up questions.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

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
                    with st.chat_message("assistant", avatar="📋"):
                        st.markdown(msg["content"])

    # Chat input
    if st.session_state.tender_loaded:
        user_input = st.chat_input("Ask a follow-up question about the tender…")
        if user_input:
            handle_user_input(user_input)
    else:
        st.chat_input("Upload and analyze a tender to start chatting…", disabled=True)


def handle_user_input(user_input):
    from langchain_core.messages import HumanMessage, AIMessage
    from ui.sidebar import get_llm   # reuse cached LLM

    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.messages.append(HumanMessage(content=user_input))

    with st.spinner(""):
        full_response = ""
        llm = get_llm()
        for chunk in llm.stream(st.session_state.messages):
            full_response += str(chunk.content or "")

    st.session_state.messages.append(AIMessage(content=full_response))
    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
    st.rerun()
