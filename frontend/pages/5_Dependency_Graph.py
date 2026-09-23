import streamlit as st
import requests
import networkx as nx
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.components.theme import apply_theme

st.set_page_config(page_title="Dependency Graph", layout="wide")
apply_theme()

st.title("Dependency Graph")

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

try:
    res = requests.get(f"http://localhost:8000/api/extract/{selected_doc_id}")
    entities = res.json()
    
    components = [e["name"] for e in entities if e["type"] == "Component"]
    interfaces = [e["name"] for e in entities if e["type"] == "Interface"]
    
    if components:
        # Create a simple mock graph since true dependencies require deeper extraction logic
        # For a full implementation, the LLM should extract (Source, Target, Type) tuples
        G = nx.Graph()
        
        for c in components:
            G.add_node(c, type="Component", color="#1D4ED8")
            
        for i in interfaces:
            G.add_node(i, type="Interface", color="#10B981")
            
        # Add random edges for demonstration
        if len(components) > 1 and len(interfaces) > 0:
            for c in components:
                G.add_edge(c, interfaces[0])
                
        pos = nx.spring_layout(G)
        
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')
            
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            node_color.append(G.nodes[node]['color'])
            
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="bottom center",
            marker=dict(
                showscale=False,
                color=node_color,
                size=20,
                line_width=2))
                
        fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
                
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to build dependency graph.")
except Exception as e:
    st.error(f"Error building graph: {e}")
