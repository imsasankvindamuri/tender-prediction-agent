# src/ui/sidebar.py

import streamlit as st
from core.config import MODEL, TEMP
from core.utils import reset_session


def render_sidebar():

    with st.sidebar:

        st.markdown(
            '<div class="brand-title">Tender<br>Analyst</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="brand-sub">AI-Powered Analysis</div>',
            unsafe_allow_html=True
        )

        # =========================
        # STATUS
        # =========================

        st.markdown(
            '<div class="sidebar-label">Status</div>',
            unsafe_allow_html=True
        )

        if st.session_state.tender_loaded:

            st.markdown(
                f'''
                <div class="status-badge status-ready">
                ● {st.session_state.tender_filename}
                </div>
                ''',
                unsafe_allow_html=True,
            )

            extraction = st.session_state.get("extraction_result")

            if extraction:

                meta = extraction.get("metadata", {})

                st.caption(
                    f"""
                    Pages: {meta.get('page_count', '?')}
                    
                    Tables: {meta.get('table_count', '?')}
                    """
                )

        else:

            st.markdown(
                '''
                <div class="status-badge status-idle">
                ○ No document loaded
                </div>
                ''',
                unsafe_allow_html=True,
            )

        # =========================
        # ACTIONS
        # =========================

        st.markdown(
            '<div class="sidebar-label">Actions</div>',
            unsafe_allow_html=True
        )

        if st.button(
            "🔄 Reset Session",
            use_container_width=True
        ):

            reset_session()
            st.rerun()

        # =========================
        # FOOTER
        # =========================

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <span style="
                font-family:'DM Mono',monospace;
                font-size:0.62rem;
                color:#3a3f52;
            ">
            Model: {MODEL}<br>
            Temp: {TEMP}
            </span>
            """,
            unsafe_allow_html=True,
        )
