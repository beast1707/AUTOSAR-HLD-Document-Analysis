import json
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.services.database import get_db_connection, save_flow, get_flows
from backend.services.llm_service import get_llm
from langchain_core.prompts import ChatPromptTemplate
from backend.utils.logging import setup_logger

logger = setup_logger("flows_route")
router = APIRouter(prefix="/api/flows", tags=["Flows"])

def get_chunks(doc_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM chunks WHERE document_id = ? ORDER BY page ASC LIMIT 30", (doc_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def deduplicate_and_merge_flows(flows: List[Dict]) -> List[Dict]:
    """Merge flows with similar titles to prevent duplicates from adjacent pages."""
    unique_flows = {}
    for flow in flows:
        title = flow.get("title", "").strip().lower()
        if title not in unique_flows:
            unique_flows[title] = flow
        else:
            # Merge citations
            existing = set(unique_flows[title].get("citations", []))
            new_cites = set(flow.get("citations", []))
            unique_flows[title]["citations"] = list(existing | new_cites)
            
            # Merge components
            existing_comp = set(unique_flows[title].get("components", []))
            new_comp = set(flow.get("components", []))
            unique_flows[title]["components"] = list(existing_comp | new_comp)
    
    return list(unique_flows.values())

@router.get("/{doc_id}")
async def get_functional_flows(doc_id: str):
    try:
        # Check if already generated
        existing_flows = get_flows(doc_id)
        if existing_flows:
            logger.info(f"Returning {len(existing_flows)} cached flows for doc {doc_id}")
            # Need to parse json strings back to lists for frontend
            for flow in existing_flows:
                flow["steps"] = json.loads(flow["steps"])
                flow["components"] = json.loads(flow["components"])
                flow["citations"] = json.loads(flow["citations"])
            return existing_flows
            
        logger.info(f"Generating new flows for doc {doc_id}")
        chunks = get_chunks(doc_id)
        if not chunks:
            raise HTTPException(status_code=404, detail="Document chunks not found")
            
        llm = get_llm(temperature=0.0) # 0.0 for strict RAG extraction
        
        system_prompt = """You are an expert Automotive Systems AI analyzing an engineering document.
Identify all distinct architectural or functional workflows described in the text. 
Do not generate generic placeholder workflows. Extract EXACT workflows mentioned (e.g. 'AUTOSAR HLD Document Analysis Pipeline', 'Diagnostic Test Scenario Generation Pipeline').

Merge chunks that belong to the same workflow instead of creating duplicate flows.

You MUST return STRICT, VALID JSON ONLY. Do not wrap in markdown blocks. No explanations, no preamble. Just the JSON object.
The response must be a JSON object with a single key 'flows', containing a list of flow objects.
Each flow object must have:
- 'title' (string): Title of the specific workflow.
- 'purpose' (string): 2-3 lines describing the actual purpose found in the text.
- 'steps' (list of strings): 5-10 ordered steps extracted from the document describing how this workflow operates.
- 'components' (list of strings): Specific components/technologies involved (e.g., FastAPI, LangChain, ChromaDB, Groq, SQLite, PyMuPDF, etc. when applicable).
- 'citations' (list of strings): Source pages (e.g. ['Page 2', 'Page 3']).
- 'confidence' (float): Confidence score between 0.0 and 1.0.

Example:
{{"flows": [{{"title": "Data Ingestion Pipeline", "purpose": "Extracts text from PDFs...", "steps": ["1. User uploads PDF", "2. Parse using PyMuPDF"], "components": ["FastAPI", "PyMuPDF"], "citations": ["Page 5"], "confidence": 0.95}}]}}
"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{text}")
        ])
        
        chain = prompt | llm
        
        # Combine text clearly for the LLM
        combined_text = "\n\n".join([f"--- Page {c['page']} ---\n{c['text']}" for c in chunks])
        combined_text = combined_text[:20000] # Fit in standard context window
        
        data = None
        try:
            response = chain.invoke({"text": combined_text})
            content = response.content.strip()
            
            logger.info(f"Raw LLM Response:\n{content}")
            
            if not content:
                raise ValueError("LLM returned an empty response.")
                
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            content = content.strip()
            if not content:
                raise ValueError("Parsed JSON block is empty.")
                
            # Strip anything before first { and after last }
            if "{" in content:
                content = content[content.find("{"):]
            if "}" in content:
                content = content[:content.rfind("}")+1]
                
            data = json.loads(content)
        except Exception as e:
            logger.error(f"LLM generation/parsing failed: {e}")
            # Graceful fallback
            if 'response' in locals() and response.content.strip():
                raw_lines = [line.strip() for line in response.content.strip().split('\n') if line.strip() and len(line.strip()) > 5]
                data = {
                    "flows": [{
                        "title": "Extracted Architectural Workflows (Unformatted)",
                        "purpose": "The AI extracted workflows but failed to format them correctly as JSON. Raw summary provided below.",
                        "steps": raw_lines[:10],
                        "components": ["Various (Unparsed)"],
                        "citations": ["Multiple (Unparsed)"],
                        "confidence": 0.4
                    }]
                }
            else:
                data = {
                    "flows": [{
                        "title": "Fallback Workflow",
                        "purpose": "System generated fallback due to AI failure.",
                        "steps": ["Analyze document", "Extract entities", "Build pipelines"],
                        "components": ["System Engine"],
                        "citations": ["General Analysis"],
                        "confidence": 0.1
                    }]
                }
            
        flows_list = data.get("flows", []) if data else []
        
        if not flows_list:
            logger.warning("No flows extracted. Returning empty list.")
            return []
            
        # Deduplicate
        flows_list = deduplicate_and_merge_flows(flows_list)
            
        # Save to DB
        for f in flows_list:
            save_flow(
                doc_id=doc_id,
                title=f.get("title", "Unknown Flow"),
                purpose=f.get("purpose", ""),
                steps=json.dumps(f.get("steps", [])),
                components=json.dumps(f.get("components", [])),
                citations=json.dumps(f.get("citations", [])),
                confidence=float(f.get("confidence", 0.8))
            )
            
        # Refetch from DB to ensure format is identical
        new_flows = get_flows(doc_id)
        for flow in new_flows:
            flow["steps"] = json.loads(flow["steps"])
            flow["components"] = json.loads(flow["components"])
            flow["citations"] = json.loads(flow["citations"])
        return new_flows
        
    except Exception as e:
        logger.error(f"Error in get_functional_flows: {e}")
        raise HTTPException(status_code=500, detail=str(e))
