from fastapi import APIRouter
from backend.models.schemas import CompareRequest, CompareResponse
from backend.services.database import get_entities

router = APIRouter(prefix="/api/compare", tags=["Compare"])

@router.post("/", response_model=CompareResponse)
async def compare_documents(request: CompareRequest):
    ents1 = get_entities(request.doc1_id)
    ents2 = get_entities(request.doc2_id)
    
    comp1 = set([e["name"] for e in ents1 if e["type"] == "Component"])
    comp2 = set([e["name"] for e in ents2 if e["type"] == "Component"])
    
    added = list(comp2 - comp1)
    removed = list(comp1 - comp2)
    modified = [] # Simplified
    
    return CompareResponse(
        components_added=added,
        components_removed=removed,
        components_modified=modified
    )
