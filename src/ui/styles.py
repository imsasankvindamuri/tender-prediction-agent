# src/ui/styles.py

import streamlit as st


def apply_page_config_and_styles():

    st.set_page_config(
        page_title="Tender Analyst",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="auto",
    )

    st.markdown("""
        <style>

        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

        /* ==========================================
           GLOBAL
        ========================================== */

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        .stApp {
            background-color: #0f1117;
            color: #e8e6e0;
        }

        /* ==========================================
           HIDE STREAMLIT DEFAULTS
        ========================================== */

        #MainMenu,
        footer {
            visibility: hidden;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* ==========================================
           SIDEBAR
        ========================================== */

        [data-testid="stSidebar"] {
            background-color: #161820;
            border-right: 1px solid #2a2d38;
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }

        /* Force sidebar toggle visibility */

        button[kind="header"] {
            display: block !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        [data-testid="collapsedControl"] {
            display: flex !important;
            opacity: 1 !important;
            visibility: visible !important;
            background-color: #161820 !important;
            border-radius: 6px !important;
        }

        /* ==========================================
           BRANDING
        ========================================== */

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

        /* ==========================================
           SIDEBAR LABELS
        ========================================== */

        .sidebar-label {
            font-family: 'DM Mono', monospace;
            font-size: 0.62rem;
            color: #5a6072;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
            margin-top: 1.5rem;
        }

        /* ==========================================
           FILE UPLOADER
        ========================================== */

        [data-testid="stFileUploader"] {
            background-color: #1c1f2a !important;
            border: 1px dashed #2e3244 !important;
            border-radius: 8px !important;
            margin-bottom: 1rem;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: #c9a84c !important;
        }

        /* ==========================================
           STATUS BADGES
        ========================================== */

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

        /* ==========================================
           MAIN HEADER
        ========================================== */

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

        /* ==========================================
           CHAT WRAPPER
        ========================================== */

        .chat-wrapper {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            padding-bottom: 1rem;
        }

        /* ==========================================
           USER MESSAGE
        ========================================== */

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

        /* ==========================================
           ASSISTANT MESSAGE
        ========================================== */

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
            background: linear-gradient(
                135deg,
                #c9a84c 0%,
                #9b7a2e 100%
            );
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

        /* ==========================================
           MARKDOWN INSIDE BUBBLES
        ========================================== */

        .msg-assistant .bubble h1,
        .msg-assistant .bubble h2,
        .msg-assistant .bubble h3 {
            font-family: 'DM Serif Display', serif;
            color: #e8e6e0;
            margin-top: 0.8rem;
            margin-bottom: 0.3rem;
        }

        .msg-assistant .bubble h2 {
            font-size: 1rem;
        }

        .msg-assistant .bubble h3 {
            font-size: 0.9rem;
        }

        .msg-assistant .bubble strong {
            color: #c9a84c;
            font-weight: 500;
        }

        .msg-assistant .bubble ul,
        .msg-assistant .bubble ol {
            padding-left: 1.2rem;
            margin: 0.3rem 0;
        }

        .msg-assistant .bubble li {
            margin-bottom: 0.2rem;
        }

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

        /* ==========================================
           EMPTY STATE
        ========================================== */

        .empty-state {
            text-align: center;
            padding: 3rem 1rem;
            color: #3a3f52;
        }

        .empty-state .icon {
            font-size: 2.5rem;
            margin-bottom: 0.75rem;
        }

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

        /* ==========================================
           DIVIDER
        ========================================== */

        .divider {
            border: none;
            border-top: 1px solid #2a2d38;
            margin: 1rem 0;
        }

        /* ==========================================
           CHAT INPUT
        ========================================== */

        [data-testid="stChatInput"] {
            background-color: #161820 !important;
            border: 1px solid #2a2d38 !important;
            border-radius: 12px !important;
        }

        [data-testid="stChatInput"]:focus-within {
            border-color: #c9a84c !important;
            box-shadow:
                0 0 0 2px rgba(201, 168, 76, 0.12)
                !important;
        }

        /* ==========================================
           BUTTONS
        ========================================== */

        .stButton > button {
            background: linear-gradient(
                135deg,
                #c9a84c 0%,
                #9b7a2e 100%
            );

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

        /* ==========================================
           SPINNER
        ========================================== */

        [data-testid="stSpinner"] {
            color: #c9a84c;
        }

        /* ==========================================
           SCROLLBAR
        ========================================== */

        ::-webkit-scrollbar {
            width: 4px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background: #2a2d38;
            border-radius: 2px;
        }

        </style>
    """, unsafe_allow_html=True)
