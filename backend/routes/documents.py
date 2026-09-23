from fastapi import APIRouter
from backend.services.database import get_documents, delete_document
from backend.services.vector_store import delete_document_vectors
import os
from backend.utils.config import settings

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.get("/")
async def list_documents():
    return get_documents()

@router.delete("/{doc_id}")
async def delete_doc(doc_id: str):
    delete_document(doc_id)
    delete_document_vectors(doc_id)
    # Also delete the file
    for filename in os.listdir(settings.UPLOAD_FOLDER):
        if filename.startswith(doc_id):
            os.remove(os.path.join(settings.UPLOAD_FOLDER, filename))
    return {"message": "Document deleted successfully"}
