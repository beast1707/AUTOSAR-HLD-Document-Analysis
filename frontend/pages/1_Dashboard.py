import streamlit as st
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.components.theme import apply_theme

st.set_page_config(page_title="Dashboard", layout="wide")
apply_theme()

st.title("Dashboard")

try:
    response = requests.get("http://localhost:8000/api/documents/")
    if response.status_code == 200:
        docs = response.json()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Documents Uploaded", len(docs))
        
        st.subheader("Recent Documents")
        if docs:
            st.dataframe(docs)
        else:
            st.info("No documents uploaded yet.")
    else:
        st.error("Failed to connect to backend.")
except Exception as e:
    st.error(f"Error connecting to backend: {e}")
