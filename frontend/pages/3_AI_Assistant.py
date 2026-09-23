import streamlit as st
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.components.theme import apply_theme

st.set_page_config(page_title="AI Assistant", layout="wide")
apply_theme()

st.title("AI Assistant")

# Fetch documents
try:
    response = requests.get("http://localhost:8000/api/documents/")
    docs = response.json()
except:
    docs = []

if not docs:
    st.warning("Please upload a document first.")
    st.stop()

doc_options = {doc["id"]: doc["name"] for doc in docs}
selected_doc_id = st.selectbox("Select Document", options=list(doc_options.keys()), format_func=lambda x: doc_options[x])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("citations"):
            st.markdown("---")
            st.caption(f"**Sources:** Pages {', '.join(map(str, message['citations']))} &nbsp;|&nbsp; **Confidence:** {message['confidence']:.2f}")

if prompt := st.chat_input("Ask a question about the architecture..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing document..."):
            try:
                res = requests.post("http://localhost:8000/api/chat/", json={
                    "document_id": selected_doc_id,
                    "question": prompt
                })
                if res.status_code == 200:
                    data = res.json()
                    answer = data["answer"].replace("<br>", "\n")
                    citations = data["citation_pages"]
                    confidence = data["confidence"]
                    
                    st.markdown(answer)
                    if citations:
                        st.markdown("---")
                        st.caption(f"**Sources:** Pages {', '.join(map(str, citations))} &nbsp;|&nbsp; **Confidence:** {confidence:.2f}")
                        
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "citations": citations,
                        "confidence": confidence
                    })
                else:
                    st.error("Failed to get response.")
            except Exception as e:
                st.error(f"Error: {e}")
