import streamlit as st
from components.theme import apply_theme
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(
    page_title="AUTOSAR HLD AI Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()

st.title("AUTOSAR HLD AI Assistant")
st.markdown("### AI-Powered High-Level Design Document Analysis Platform for Automotive Engineering")

st.info("Welcome! Please navigate using the sidebar to upload documents or explore existing architectures.")

st.markdown("""
This platform allows automotive engineers to:
- **Upload AUTOSAR HLD PDFs**
- **Extract Architectural Knowledge**
- **Build a RAG Knowledge Base**
- **Answer Engineering Questions with Citations**
""")
