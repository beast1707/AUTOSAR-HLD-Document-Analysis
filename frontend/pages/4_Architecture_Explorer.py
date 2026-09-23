import streamlit as st
import requests
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.components.theme import apply_theme

st.set_page_config(page_title="Architecture Explorer", layout="wide")
apply_theme()

st.title("Architecture Explorer")

try:
    docs_res = requests.get("http://localhost:8000/api/documents/")
    docs = docs_res.json()
except:
    docs = []

if not docs:
    st.warning("Please upload a document first.")
    st.stop()
    
doc_options = {doc["id"]: doc["name"] for doc in docs}
selected_doc_id = st.selectbox("Select Document to Explore", options=list(doc_options.keys()), format_func=lambda x: doc_options[x])

try:
    res = requests.get(f"http://localhost:8000/api/extract/{selected_doc_id}")
    entities = res.json()
    
    if entities:
        df = pd.DataFrame(entities)
        
        tab1, tab2, tab3, tab4 = st.tabs(["Components", "Interfaces", "Ports", "Signals"])
        
        with tab1:
            comp_df = df[df["type"] == "Component"]
            st.dataframe(comp_df[["name", "description", "page"]], use_container_width=True)
            
        with tab2:
            int_df = df[df["type"] == "Interface"]
            st.dataframe(int_df[["name", "description", "page"]], use_container_width=True)
            
        with tab3:
            port_df = df[df["type"] == "Port"]
            st.dataframe(port_df[["name", "description", "page"]], use_container_width=True)
            
        with tab4:
            sig_df = df[df["type"] == "Signal"]
            st.dataframe(sig_df[["name", "description", "page"]], use_container_width=True)
    else:
        st.info("No entities extracted yet. Processing might still be ongoing.")
        
except Exception as e:
    st.error(f"Error fetching entities: {e}")
