# src/ui/chat.py

import traceback
from langchain_core.messages import SystemMessage
import streamlit as st


from core.config import SYSTEM_PROMPT
from core.utils import reset_session


def analyze_tender(uploaded_file):
    """Main analysis pipeline: Extract → Ingest → Structured Analysis"""
    
    # === 1. Extraction with Docling ===
    with st.spinner("Extracting document with Docling..."):
        try:
            from core.extract import extract_tender_document
            extraction_result = extract_tender_document(uploaded_file)

            if not extraction_result.get("success"):
                st.error(f"Extraction failed: {extraction_result.get('error')}")
                return

            st.success(f"Extracted {extraction_result['metadata']['page_count']} pages "
                      f"({extraction_result['metadata']['table_count']} tables)")

        except Exception as e:
            st.error(f"Extraction error: {e}")
            st.code(traceback.format_exc())
            return

    # === 2. RAG Ingestion ===
    with st.spinner("Building vector store..."):
        try:
            from core.rag import TenderRAG
            
            if "rag" not in st.session_state:
                st.session_state.rag = TenderRAG()

            tender_id = uploaded_file.name.replace(".", "_").replace(" ", "_").lower()
            
            st.session_state.rag.ingest_document(extraction_result, tender_id)

            st.session_state.tender_loaded = True
            st.session_state.tender_filename = uploaded_file.name
            st.session_state.tender_id = tender_id
            st.session_state.extraction_result = extraction_result

        except Exception as e:
            st.error(f"Vector store error: {e}")
            st.code(traceback.format_exc())
            return

    # === 3. Structured Analysis using Analyzer ===
    with st.spinner("Generating structured tender analysis..."):
        try:
            from core.analyzer import TenderAnalyzer
            from langchain_core.messages import AIMessage

            # Initialize analyzer
            analyzer = TenderAnalyzer(st.session_state.rag)

            # Generate full report
            full_report = analyzer.generate_full_analysis()

            # Reset conversation
            st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
            st.session_state.chat_history = []

            # Store the analysis
            st.session_state.messages.append(AIMessage(content=full_report))
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": full_report,
            })

            st.success("✅ Initial structured analysis complete!")
            st.rerun()

        except Exception as e:
            st.error(f"Analysis generation failed: {e}")
            st.code(traceback.format_exc())

def reset_app():
    reset_session()

def render_chat_area():

    st.markdown(
        '<div class="main-header">Tender Analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div class="main-sub">
        Upload a tender PDF, run analysis,
        then ask follow-up questions.
        </div>
        ''',
        unsafe_allow_html=True,
    )

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ==========================================
    # UPLOAD AREA
    # ==========================================

    if not st.session_state.tender_loaded:

        with st.container():

            st.markdown("### Upload Tender Document")

            uploaded_file = st.file_uploader(
                "Upload Tender PDF",
                type=["pdf"],
                label_visibility="collapsed"
            )

            if uploaded_file:

                st.info(
                    f"Loaded: {uploaded_file.name}"
                )

                if st.button(
                    "Analyze Tender",
                    use_container_width=True
                ):

                    analyze_tender(uploaded_file)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        st.markdown("""
        <div class="empty-state">
            <div class="icon">📋</div>
            <div class="title">
                No tender loaded
            </div>
            <div class="hint">
                Upload a PDF to begin analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

        return

    # ==========================================
    # CHAT HISTORY
    # ==========================================

    for msg in st.session_state.chat_history:

        if msg["role"] == "user":

            st.markdown(f"""
            <div class="msg-user">
                <div class="bubble">
                {msg["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:

            with st.chat_message(
                "assistant",
                avatar="📋"
            ):

                st.markdown(msg["content"])

    # ==========================================
    # CHAT INPUT
    # ==========================================

    user_input = st.chat_input(
        "Ask a follow-up question..."
    )

    if user_input:

        handle_user_input(user_input)


def handle_user_input(user_input):

    from langchain_core.messages import (
        HumanMessage,
        AIMessage,
        SystemMessage,
    )

    from core.llm import get_llm
    from core.config import SYSTEM_PROMPT

    # ==========================================
    # STORE USER MESSAGE
    # ==========================================

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    # ==========================================
    # RETRIEVAL
    # ==========================================

    with st.spinner("Searching tender..."):

        docs = st.session_state.rag.retrieve(
            user_input,
            k=8
        )

        all_context = []

        for doc in docs:

            page = doc.metadata.get(
                "page",
                "N/A"
            )

            chunk_id = doc.metadata.get(
                "chunk_id",
                "?"
            )

            doc_type = doc.metadata.get(
                "type",
                "text"
            )

            all_context.append(
                f"""
[PAGE: {page}]
[CHUNK: {chunk_id}]
[TYPE: {doc_type}]

{doc.page_content}
"""
            )

        context = "\n\n---\n\n".join(
            all_context
        )

    # ==========================================
    # GROUNDED QUERY
    # ==========================================

    grounded_query = f"""
Answer the following question
using ONLY the provided tender context.

If information is missing,
say:
"Not explicitly mentioned."

CONTEXT:
{context}

QUESTION:
{user_input}

RULES:
- Do NOT hallucinate.
- Do NOT infer missing requirements.
- Use direct quotes where possible.
- Cite section/page references when available.
- Be concise and professional.
"""

    # ==========================================
    # MESSAGE STACK
    # ==========================================

    messages_for_llm = [
        SystemMessage(content=SYSTEM_PROMPT)
    ]

    for msg in st.session_state.chat_history[-5:-1]:

        if msg["role"] == "user":

            messages_for_llm.append(
                HumanMessage(
                    content=msg["content"]
                )
            )

        else:

            messages_for_llm.append(
                AIMessage(
                    content=msg["content"]
                )
            )

    messages_for_llm.append(
        HumanMessage(content=grounded_query)
    )

    # ==========================================
    # LLM CALL
    # ==========================================

    with st.spinner("Thinking..."):

        llm = get_llm()

        response = llm.invoke(
            messages_for_llm
        )

        full_response = str(
            response.content
        )

    # ==========================================
    # STORE RESPONSE
    # ==========================================

    st.session_state.messages.append(
        HumanMessage(content=user_input)
    )

    st.session_state.messages.append(
        AIMessage(content=full_response)
    )

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": full_response,
    })

    st.rerun()
