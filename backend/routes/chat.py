from fastapi import APIRouter, HTTPException
from backend.models.schemas import MessageRequest, MessageResponse
from backend.services.vector_store import search_chunks
from backend.services.llm_service import get_llm
from backend.services.database import save_chat
from backend.utils.logging import setup_logger
from langchain_core.prompts import ChatPromptTemplate

logger = setup_logger("chat_route")
router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/", response_model=MessageResponse)
async def chat(request: MessageRequest):
    logger.info(f"Chat request for doc {request.document_id}")
    try:
        # Retrieve context
        results = search_chunks(request.question, request.document_id, top_k=5)
        
        if not results:
            return MessageResponse(
                answer="Information not found in uploaded document.",
                confidence=0.0,
                citation_pages=[]
            )
            
        # Sort by page for logical ordering
        results.sort(key=lambda x: x["metadata"].get("page", 0))
        
        merged_chunks = []
        current_chunk = None
        
        for res in results:
            meta = res["metadata"]
            heading = meta.get("heading", "")
            section = meta.get("section", "")
            page = meta.get("page", 0)
            
            if current_chunk is None:
                current_chunk = {
                    "text": res["text"],
                    "pages": {page},
                    "heading": heading,
                    "section": section
                }
            else:
                # If same heading/section, merge them
                if heading == current_chunk["heading"] and section == current_chunk["section"]:
                    current_chunk["text"] += "\n" + res["text"]
                    current_chunk["pages"].add(page)
                else:
                    merged_chunks.append(current_chunk)
                    current_chunk = {
                        "text": res["text"],
                        "pages": {page},
                        "heading": heading,
                        "section": section
                    }
        if current_chunk:
            merged_chunks.append(current_chunk)
            
        context_texts = []
        citation_pages = set()
        for mc in merged_chunks:
            pages_list = sorted(list(mc["pages"]))
            page_str = ", ".join(map(str, pages_list))
            block = f"--- Section: {mc['section']} | Heading: {mc['heading']} | Pages: {page_str} ---\n{mc['text']}"
            context_texts.append(block)
            citation_pages.update(mc["pages"])
            
        context_str = "\n\n".join(context_texts)
        
        # Generate Answer
        llm = get_llm(temperature=0.1)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an Automotive Engineering AI Assistant specializing in AUTOSAR High-Level Design documents. Answer only using supplied document context. Cite page numbers. Mention uncertainty if context is insufficient. Never fabricate AUTOSAR entities.\n\nContext:\n{context}"),
            ("user", "{question}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({
            "context": context_str,
            "question": request.question
        })
        
        answer = response.content
        confidence = 0.9 if "I cannot answer" not in answer and "Information not found" not in answer else 0.1
        
        # Save to history
        save_chat(request.document_id, request.question, answer, str(list(citation_pages)), confidence)
        
        return MessageResponse(
            answer=answer,
            confidence=confidence,
            citation_pages=list(citation_pages)
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
