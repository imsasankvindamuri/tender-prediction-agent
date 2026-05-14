# src/core/llm.py
import streamlit as st
from langchain_groq import ChatGroq

from core.config import MODEL, TEMP


@st.cache_resource
def get_llm():
    """Centralized LLM instance"""
    return ChatGroq(model=MODEL, temperature=TEMP)
