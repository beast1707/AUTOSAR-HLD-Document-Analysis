import streamlit as st
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.components.theme import apply_theme

st.set_page_config(page_title="Document Upload", layout="wide")
apply_theme()

st.title("Document Upload")
st.markdown("Upload AUTOSAR HLD PDF documents here.")

uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

if st.button("Upload & Index"):
    if uploaded_files:
        for file in uploaded_files:
            st.write(f"Uploading {file.name}...")
            files = {"file": (file.name, file, "application/pdf")}
            try:
                response = requests.post("http://localhost:8000/api/upload/", files=files)
                if response.status_code == 200:
                    st.success(f"Successfully uploaded {file.name}. Indexing in background.")
                else:
                    st.error(f"Failed to upload {file.name}: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please select at least one file.")
        
st.divider()
st.subheader("Manage Documents")
try:
    response = requests.get("http://localhost:8000/api/documents/")
    if response.status_code == 200:
        docs = response.json()
        for doc in docs:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{doc['name']}** (Status: {doc['status']})")
            with col2:
                if st.button("Delete", key=doc['id']):
                    requests.delete(f"http://localhost:8000/api/documents/{doc['id']}")
                    st.rerun()
except Exception as e:
    st.error(f"Error: {e}")
