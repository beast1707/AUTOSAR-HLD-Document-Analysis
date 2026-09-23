from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import csv
import json
from datetime import datetime
from backend.utils.config import settings
from backend.services.database import get_entities, get_db_connection, get_flows
from backend.services.llm_service import get_llm
from backend.utils.logging import setup_logger

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

logger = setup_logger("report_route")
router = APIRouter(prefix="/api/report", tags=["Report"])

def enrich_entities(doc_id: str, entities: list):
    """Enriches entities with correct page numbers and contextual descriptions from chunks."""
    conn = get_db_connection()
    
    enriched = []
    for e in entities:
        # Default fallback
        new_page = e.get("page", 1)
        new_desc = e.get("description", "")
        
        name = e.get("name", "")
        if name:
            # Search chunks for this entity
            # SQLite LIKE is case-insensitive by default
            cursor = conn.execute(
                "SELECT page, text FROM chunks WHERE document_id = ? AND text LIKE ? ORDER BY page ASC",
                (doc_id, f"%{name}%")
            )
            rows = cursor.fetchall()
            
            if rows:
                # Found the entity in chunks! Take the first appearance.
                best_row = rows[0]
                new_page = best_row["page"]
                text = best_row["text"]
                
                # Extract a 250 character window around the mention
                idx = text.lower().find(name.lower())
                if idx != -1:
                    start = max(0, idx - 80)
                    end = min(len(text), idx + len(name) + 170)
                    window = text[start:end].replace('\n', ' ').strip()
                    if start > 0: window = "..." + window
                    if end < len(text): window = window + "..."
                    
                    new_desc = f"{window}"
        
        enriched.append({
            "id": e["id"],
            "document_id": e["document_id"],
            "type": e["type"],
            "name": e["name"],
            "description": new_desc,
            "page": new_page
        })
        
    conn.close()
    return enriched

def get_stats(doc_id: str, entities: list):
    """Calculates summary statistics."""
    stats = {
        "Total Components": 0,
        "Interfaces": 0,
        "Ports": 0,
        "Messages": 0,
        "Functional Flows": 0
    }
    
    for e in entities:
        t = str(e.get("type", "")).lower()
        if "component" in t or t == "swc":
            stats["Total Components"] += 1
        elif "interface" in t:
            stats["Interfaces"] += 1
        elif "port" in t:
            stats["Ports"] += 1
        elif "message" in t or "signal" in t:
            stats["Messages"] += 1
            
    flows = get_flows(doc_id)
    stats["Functional Flows"] = len(flows)
    
    return stats

def get_document_name(doc_id: str) -> str:
    conn = get_db_connection()
    cursor = conn.execute("SELECT name FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()
    return row["name"] if row else "Unknown Document"

@router.get("/csv/{doc_id}")
async def get_csv_report(doc_id: str):
    try:
        entities = get_entities(doc_id)
        if not entities:
            raise HTTPException(status_code=404, detail="No entities found for this document")
            
        enriched_entities = enrich_entities(doc_id, entities)
        stats = get_stats(doc_id, enriched_entities)
            
        report_path = os.path.join(settings.REPORT_FOLDER, f"{doc_id}_report.csv")
        with open(report_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write Stats
            writer.writerow(["--- SUMMARY STATISTICS ---"])
            for k, v in stats.items():
                writer.writerow([k, v])
            writer.writerow([])
            
            # Write Entities
            writer.writerow(["--- EXTRACTED ENTITIES ---"])
            dict_writer = csv.DictWriter(f, fieldnames=["id", "document_id", "type", "name", "description", "page"])
            dict_writer.writeheader()
            for e in enriched_entities:
                dict_writer.writerow(e)
                
        return FileResponse(path=report_path, filename="architecture_report.csv", media_type="text/csv")
    except Exception as e:
        logger.error(f"CSV Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pdf/{doc_id}")
async def get_pdf_report(doc_id: str):
    try:
        doc_name = get_document_name(doc_id)
        entities = get_entities(doc_id)
        flows = get_flows(doc_id)
        
        if not entities and not flows:
            raise HTTPException(status_code=404, detail="No extracted data found for this document")
            
        enriched_entities = enrich_entities(doc_id, entities)
        stats = get_stats(doc_id, enriched_entities)
        
        # Call LLM for overarching summaries
        llm = get_llm(temperature=0.2)
        flows_text = "\\n".join([f"- {f['title']}: {f['purpose']}" for f in flows[:5]])
        prompt = f"""Based on these extracted workflows from an AUTOSAR Architecture Document:
{flows_text}

Provide two concise paragraphs:
1. "Architecture Summary": A 3 sentence summary of the overarching system architecture.
2. "Dependency Summary": A 3 sentence summary of how the components depend on each other.

Return exactly like this:
Architecture Summary: <text>
Dependency Summary: <text>
"""
        try:
            llm_res = llm.invoke(prompt).content
            arch_sum = llm_res.split("Dependency Summary:")[0].replace("Architecture Summary:", "").strip()
            dep_sum = llm_res.split("Dependency Summary:")[-1].strip()
        except:
            arch_sum = "Could not generate Architecture Summary."
            dep_sum = "Could not generate Dependency Summary."
            
        report_path = os.path.join(settings.REPORT_FOLDER, f"{doc_id}_report.pdf")
        
        # Build PDF
        doc = SimpleDocTemplate(report_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = styles['Title']
        h1 = styles['Heading1']
        h2 = styles['Heading2']
        body = styles['Normal']
        
        # Title
        elements.append(Paragraph("AUTOSAR Architecture Report", title_style))
        elements.append(Paragraph(f"Document: {doc_name}", h2))
        elements.append(Paragraph(f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body))
        elements.append(Spacer(1, 20))
        
        # Summaries
        elements.append(Paragraph("Architecture Summary", h1))
        elements.append(Paragraph(arch_sum, body))
        elements.append(Spacer(1, 10))
        
        elements.append(Paragraph("Dependency Summary", h1))
        elements.append(Paragraph(dep_sum, body))
        elements.append(Spacer(1, 20))
        
        # Stats
        elements.append(Paragraph("Summary Statistics", h1))
        stat_data = [["Metric", "Count"]]
        for k, v in stats.items():
            stat_data.append([k, str(v)])
            
        stat_table = Table(stat_data, colWidths=[200, 100])
        stat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#DBEAFE")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.silver),
        ]))
        elements.append(stat_table)
        elements.append(Spacer(1, 20))
        
        # Flows
        elements.append(Paragraph("Functional Flows", h1))
        if flows:
            for f in flows:
                elements.append(Paragraph(f"<b>{f['title']}</b>", h2))
                elements.append(Paragraph(f"Purpose: {f['purpose']}", body))
                elements.append(Spacer(1, 5))
        else:
            elements.append(Paragraph("No flows extracted.", body))
        elements.append(Spacer(1, 20))
            
        # Entities Table
        elements.append(Paragraph("Extracted Entities", h1))
        ent_data = [["Name", "Type", "Page", "Context"]]
        
        for e in enriched_entities[:50]: # Limit to 50 so PDF doesn't explode
            # Truncate context for table
            desc = e['description'][:100] + '...' if len(e['description']) > 100 else e['description']
            ent_data.append([e['name'], e['type'], str(e['page']), desc])
            
        ent_table = Table(ent_data, colWidths=[120, 80, 40, 260])
        ent_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#DBEAFE")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.silver),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(ent_table)
        
        if len(enriched_entities) > 50:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"...and {len(enriched_entities) - 50} more entities available in CSV.", body))
            
        doc.build(elements)
        
        return FileResponse(path=report_path, filename="architecture_report.pdf", media_type="application/pdf")
        
    except Exception as e:
        logger.error(f"PDF Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
