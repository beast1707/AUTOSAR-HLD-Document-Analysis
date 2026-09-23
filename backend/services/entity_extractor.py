import re
import json
from typing import List, Dict, Any
from backend.services.database import save_entity
from backend.services.llm_service import get_llm
from backend.utils.logging import setup_logger
from langchain_core.prompts import ChatPromptTemplate

logger = setup_logger("entity_extractor")

def rule_based_extraction(text: str) -> dict:
    data = {
        "components": [],
        "interfaces": [],
        "ports": [],
        "signals": [],
        "ecus": [],
        "messages": []
    }
    
    # Broad heuristics/regex for AUTOSAR entities and generic system concepts
    comp_matches = re.findall(r'\b([A-Z][a-zA-Z0-9_]*(?:Component|SWC|Manager|Handler|System|Module|App|Service))\b', text)
    data["components"].extend(comp_matches)
    
    if_matches = re.findall(r'\b([A-Z][a-zA-Z0-9_]*(?:Interface|If|IF|API|Bus|Connection|Link))\b', text)
    data["interfaces"].extend(if_matches)
    
    port_matches = re.findall(r'\b([A-Z][a-zA-Z0-9_]*(?:Port|PPort|RPort|Endpoint|Pin|Node))\b', text)
    data["ports"].extend(port_matches)
    
    sig_matches = re.findall(r'\b([A-Z][a-zA-Z0-9_]*(?:Signal|Data|Event|Trigger|State|Status))\b', text)
    data["signals"].extend(sig_matches)
    
    ecu_matches = re.findall(r'\b([A-Z][a-zA-Z0-9_]*(?:ECU|Controller|Node|Processor|MCU))\b', text)
    data["ecus"].extend(ecu_matches)
    
    msg_matches = re.findall(r'\b([A-Z][a-zA-Z0-9_]*(?:Message|Msg|Frame|Packet|Req|Res))\b', text)
    data["messages"].extend(msg_matches)
    
    # Aggressive fallback if still empty (useful for generic case study documents without strict AUTOSAR syntax)
    if not any(data.values()):
        words = re.findall(r'\b([A-Z][a-zA-Z]+)\b', text)
        if words:
            data['components'].append(words[0] + ' System')
            if len(words) > 1: data['interfaces'].append(words[1] + ' Interface')
            if len(words) > 2: data['signals'].append(words[2] + ' Signal')
    
    # Deduplicate
    for k in data:
        data[k] = list(set(data[k]))
        
    return data

def save_extracted_data(doc_id: str, chunk: Dict[str, Any], data: dict):
    for comp in data.get("components", []):
        save_entity(doc_id, "Component", comp, "Extracted Software Component", chunk["page"])
    for interface in data.get("interfaces", []):
        save_entity(doc_id, "Interface", interface, "Extracted Interface", chunk["page"])
    for port in data.get("ports", []):
        save_entity(doc_id, "Port", port, "Extracted Port", chunk["page"])
    for signal in data.get("signals", []):
        save_entity(doc_id, "Signal", signal, "Extracted Signal", chunk["page"])
    for ecu in data.get("ecus", []):
        save_entity(doc_id, "ECU", ecu, "Extracted ECU", chunk["page"])
    for msg in data.get("messages", []):
        save_entity(doc_id, "Message", msg, "Extracted Network Message", chunk["page"])

def extract_entities(doc_id: str, chunks: List[Dict[str, Any]]):
    logger.info(f"Extracting entities for doc {doc_id}...")
    try:
        llm = get_llm(temperature=0.0)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert Automotive AI. Extract software components, interfaces, ports, signals, ECUs, and network messages from the text. Be lenient and extract general architecture elements if strict AUTOSAR entities are not found. Respond strictly in JSON format: {{\"components\": [], \"interfaces\": [], \"ports\": [], \"signals\": [], \"ecus\": [], \"messages\": []}}. If none, return empty lists."),
            ("user", "{text}")
        ])
        
        chain = prompt | llm
        
        # Process more chunks to guarantee finding entities
        sample_chunks = chunks[:min(10, len(chunks))]
        
        for chunk in sample_chunks:
            data = None
            try:
                response = chain.invoke({"text": chunk["text"]})
                content = response.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                    
                data = json.loads(content.strip())
            except Exception as e:
                logger.warning(f"LLM extraction failed, using rule-based fallback: {e}")
                data = rule_based_extraction(chunk["text"])
                
            if data:
                save_extracted_data(doc_id, chunk, data)
                
        logger.info(f"Finished entity extraction for doc {doc_id}")
    except Exception as e:
        logger.error(f"Entity extraction setup failed: {e}")
        # Even if LLM setup fails entirely, let's use the rule-based extractor
        logger.info("Falling back to rule-based extraction for all sampled chunks")
        sample_chunks = chunks[:min(10, len(chunks))]
        for chunk in sample_chunks:
            data = rule_based_extraction(chunk["text"])
            if data:
                save_extracted_data(doc_id, chunk, data)
