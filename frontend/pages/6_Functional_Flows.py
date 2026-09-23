import streamlit as st
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.components.theme import apply_theme

st.set_page_config(page_title="Functional Flows", layout="wide")
apply_theme()

st.title("Functional Flow Summary")

# Fetch documents
try:
    docs_res = requests.get("http://localhost:8000/api/documents/")
    docs = docs_res.json()
except Exception as e:
    docs = []

if not docs:
    st.warning("Please upload a document first.")
    st.stop()
    
doc_options = {doc["id"]: doc["name"] for doc in docs}
selected_doc_id = st.selectbox("Select Document", options=list(doc_options.keys()), format_func=lambda x: doc_options[x])

st.markdown("---")

if selected_doc_id:
    with st.spinner("Analyzing document and generating functional flows..."):
        try:
            res = requests.get(f"http://localhost:8000/api/flows/{selected_doc_id}")
            if res.status_code == 200:
                flows = res.json()
                if not flows:
                    st.info("No functional flows found in this document.")
                else:
                    st.write(f"### Identified Workflows ({len(flows)})")
                    
                    for flow in flows:
                        with st.expander(f"🔄 **{flow.get('title', 'Unknown Flow')}**", expanded=False):
                            st.markdown(f"**Purpose:** {flow.get('purpose', 'N/A')}")
                            
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.markdown("#### Workflow Steps")
                                steps = flow.get("steps", [])
                                if steps:
                                    for i, step in enumerate(steps, 1):
                                        st.markdown(f"{i}. {step}")
                                else:
                                    st.write("No steps identified.")
                            
                            with col2:
                                st.markdown("#### Components Involved")
                                components = flow.get("components", [])
                                if components:
                                    # Render badges/chips
                                    html = " ".join([f"<span style='background-color:#E5E7EB; color:#374151; padding:2px 8px; border-radius:12px; font-size:0.85em; margin-right:4px; display:inline-block; margin-bottom:4px;'>{c}</span>" for c in components])
                                    st.markdown(html, unsafe_allow_html=True)
                                else:
                                    st.write("None specified")
                                    
                                st.markdown("#### Source Pages")
                                citations = flow.get("citations", [])
                                if citations:
                                    html = " ".join([f"<span style='background-color:#DBEAFE; color:#1E40AF; padding:2px 8px; border-radius:12px; font-size:0.85em; margin-right:4px; display:inline-block; margin-bottom:4px;'>{c}</span>" for c in citations])
                                    st.markdown(html, unsafe_allow_html=True)
                                else:
                                    st.write("N/A")
                                
                                conf = flow.get("confidence", 0.0)
                                color = "green" if conf >= 0.7 else ("orange" if conf >= 0.4 else "red")
                                st.markdown(f"**Confidence:** :{color}[{conf*100:.0f}%]")
                                
            else:
                st.error(f"Failed to fetch functional flows: {res.text}")
        except Exception as e:
            st.error(f"Error communicating with backend: {e}")
