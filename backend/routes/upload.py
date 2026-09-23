import os
import uuid
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from backend.utils.config import settings
from backend.utils.logging import setup_logger
from backend.services.database import save_document, update_document_status, save_chunk
from backend.services.pdf_parser import parse_pdf
from backend.services.chunker import chunk_document
from backend.services.vector_store import index_chunks, delete_document_vectors

logger = setup_logger("upload_route")
router = APIRouter(prefix="/api/upload", tags=["Upload"])

def process_document(doc_id: str, file_path: str):
    try:
        update_document_status(doc_id, "parsing")
        pages_data = parse_pdf(file_path)
        
        # update pages count
        pages_count = len(pages_data)
        import sqlite3
        conn = sqlite3.connect(settings.SQLITE_DB_PATH)
        conn.execute("UPDATE documents SET pages = ? WHERE id = ?", (pages_count, doc_id))
        conn.commit()
        conn.close()

        update_document_status(doc_id, "chunking")
        chunks = chunk_document(pages_data)
        
        update_document_status(doc_id, "indexing")
        for chunk in chunks:
            save_chunk(doc_id, chunk["page"], chunk["section"], chunk["heading"], chunk["text"])
            
        index_chunks(chunks, doc_id)
        
        update_document_status(doc_id, "completed")
        logger.info(f"Document {doc_id} processed successfully")
        
        # trigger entity extraction 
        from backend.services.entity_extractor import extract_entities
        extract_entities(doc_id, chunks)

    except Exception as e:
        logger.error(f"Error processing document {doc_id}: {e}")
        update_document_status(doc_id, "failed")

@router.post("/", response_model=dict)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    doc_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_FOLDER, f"{doc_id}_{file.filename}")
    
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
            
        save_document(doc_id, file.filename, 0, "uploaded")
        
        background_tasks.add_task(process_document, doc_id, file_path)
        
        return {"id": doc_id, "message": "Upload successful, processing started."}
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
