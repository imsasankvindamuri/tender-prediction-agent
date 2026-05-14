# src/ui/sidebar.py
import traceback
import streamlit as st
import tempfile
import os
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from core.config import INITIAL_ANALYSIS_PROMPT, MODEL, TEMP, SYSTEM_PROMPT
from core.utils import reset_session


def render_sidebar():

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

def reset_app():
    reset_session()
