from fastapi import APIRouter
from backend.services.database import get_entities

router = APIRouter(prefix="/api/extract", tags=["Extract"])

@router.get("/{doc_id}")
async def get_doc_entities(doc_id: str):
    return get_entities(doc_id)
