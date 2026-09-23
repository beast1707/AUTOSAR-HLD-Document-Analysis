import streamlit as st
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.components.theme import apply_theme

st.set_page_config(page_title="Document Comparison", layout="wide")
apply_theme()

st.title("Document Comparison")

try:
    docs_res = requests.get("http://localhost:8000/api/documents/")
    docs = docs_res.json()
except:
    docs = []

if len(docs) < 2:
    st.warning("Please upload at least two documents to compare.")
    st.stop()
    
doc_options = {doc["id"]: doc["name"] for doc in docs}

col1, col2 = st.columns(2)
with col1:
    doc1_id = st.selectbox("Version A", options=list(doc_options.keys()), format_func=lambda x: doc_options[x])
with col2:
    doc2_id = st.selectbox("Version B", options=list(doc_options.keys()), format_func=lambda x: doc_options[x])
    
if st.button("Compare"):
    if doc1_id == doc2_id:
        st.error("Please select two different documents.")
    else:
        with st.spinner("Generating comparison report..."):
            try:
                res = requests.post("http://localhost:8000/api/compare/", json={
                    "doc1_id": doc1_id,
                    "doc2_id": doc2_id
                })
                
                if res.status_code == 200:
                    data = res.json()
                    
                    st.subheader("Differences")
                    
                    col_a, col_r, col_m = st.columns(3)
                    with col_a:
                        st.markdown("**Components Added**")
                        for c in data["components_added"]:
                            st.success(c)
                            
                    with col_r:
                        st.markdown("**Components Removed**")
                        for c in data["components_removed"]:
                            st.error(c)
                            
                    with col_m:
                        st.markdown("**Components Modified**")
                        for c in data["components_modified"]:
                            st.warning(c)
                else:
                    st.error("Comparison failed.")
            except Exception as e:
                st.error(f"Error: {e}")
