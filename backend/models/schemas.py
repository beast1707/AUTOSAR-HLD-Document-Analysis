from pydantic import BaseModel
from typing import List, Optional

class DocumentResponse(BaseModel):
    id: str
    name: str
    pages: int
    status: str
    created_at: str

class MessageRequest(BaseModel):
    document_id: str
    question: str
    
class MessageResponse(BaseModel):
    answer: str
    confidence: float
    citation_pages: List[int]

class CompareRequest(BaseModel):
    doc1_id: str
    doc2_id: str

class CompareResponse(BaseModel):
    components_added: List[str]
    components_removed: List[str]
    components_modified: List[str]
