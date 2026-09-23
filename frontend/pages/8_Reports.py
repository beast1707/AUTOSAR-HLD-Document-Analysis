import streamlit as st
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.components.theme import apply_theme

st.set_page_config(page_title="Reports & Export", layout="wide")
apply_theme()

st.title("Reports & Export")

try:
    docs_res = requests.get("http://localhost:8000/api/documents/")
    docs = docs_res.json()
except:
    docs = []

if not docs:
    st.warning("Please upload a document first.")
    st.stop()
    
doc_options = {doc["id"]: doc["name"] for doc in docs}
selected_doc_id = st.selectbox("Select Document", options=list(doc_options.keys()), format_func=lambda x: doc_options[x])

col1, col2 = st.columns(2)

with col1:
    if st.button("Download CSV Report"):
        with st.spinner("Generating CSV..."):
            try:
                res = requests.get(f"http://localhost:8000/api/report/csv/{selected_doc_id}")
                if res.status_code == 200:
                    st.download_button(
                        label="Click to Download CSV",
                        data=res.content,
                        file_name="architecture_report.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Failed to generate CSV.")
            except Exception as e:
                st.error(f"Error: {e}")

with col2:
    if st.button("Download PDF Report"):
        with st.spinner("Generating PDF (this takes a few seconds)..."):
            try:
                res = requests.get(f"http://localhost:8000/api/report/pdf/{selected_doc_id}")
                if res.status_code == 200:
                    st.download_button(
                        label="Click to Download PDF",
                        data=res.content,
                        file_name="architecture_report.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Failed to generate PDF.")
            except Exception as e:
                st.error(f"Error: {e}")
