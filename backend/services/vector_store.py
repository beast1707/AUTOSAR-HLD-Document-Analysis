import chromadb
import re
from typing import List, Dict, Any
from backend.utils.config import settings
from backend.utils.logging import setup_logger
from backend.services.embedding_service import get_embeddings

logger = setup_logger("vector_store")

_chroma_client = None

def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
    return _chroma_client

def get_collection(name: str = "autosar_collection"):
    client = get_chroma_client()
    return client.get_or_create_collection(name=name)

def index_chunks(chunks: List[Dict[str, Any]], doc_id: str):
    logger.info(f"Indexing {len(chunks)} chunks for doc {doc_id}...")
    collection = get_collection()
    embeddings_model = get_embeddings()
    
    ids = []
    texts = []
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_{i}"
        ids.append(chunk_id)
        texts.append(chunk["text"])
        metadatas.append({
            "document_id": doc_id,
            "page": chunk["page"],
            "section": chunk["section"],
            "heading": chunk["heading"]
        })
        
    if texts:
        # Generate embeddings
        embeddings = embeddings_model.embed_documents(texts)
        # Add to chroma
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )
    logger.info(f"Successfully indexed chunks for doc {doc_id}")

def is_toc_chunk(text: str) -> bool:
    """Heuristic to detect Table of Contents chunks."""
    text_lower = text.lower()
    if "table of contents" in text_lower or "contents" in text_lower[:50]:
        # Check if many lines end with numbers or have dot leaders
        lines = text.split('\n')
        number_ending_lines = sum(1 for line in lines if re.search(r'\d+\s*$', line.strip()))
        if number_ending_lines > 2 or text.count("...") > 3 or text.count("") > 3:
            return True
    return False

def search_chunks(query: str, doc_id: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
    collection = get_collection()
    embeddings_model = get_embeddings()
    
    query_embedding = embeddings_model.embed_query(query)
    
    where = None
    if doc_id:
        where = {"document_id": doc_id}
        
    # Over-fetch by 3x to allow filtering and re-ranking
    fetch_k = top_k * 3
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=fetch_k,
        where=where,
        include=["documents", "metadatas", "distances"]
    )
    
    formatted_results = []
    if results and results["documents"] and results["documents"][0]:
        for i in range(len(results["documents"][0])):
            formatted_results.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "score": 1.0 / (1.0 + results["distances"][0][i]) # Convert distance to score
            })
            
    if not formatted_results:
        return []
        
    # Filter TOC chunks
    non_toc_results = [r for r in formatted_results if not is_toc_chunk(r["text"])]
    
    # Only apply TOC filter if we still have results left
    working_results = non_toc_results if non_toc_results else formatted_results
    
    # Heading boost
    query_words = set(re.findall(r'\b\w+\b', query.lower()))
    # Remove common stop words from query for better matching
    stop_words = {"what", "is", "the", "a", "an", "of", "in", "to", "for", "and", "or", "list", "explain", "describe", "how", "does", "work"}
    query_words = query_words - stop_words
    
    if query_words:
        for r in working_results:
            heading = str(r["metadata"].get("heading", "")).lower()
            section = str(r["metadata"].get("section", "")).lower()
            
            heading_words = set(re.findall(r'\b\w+\b', heading + " " + section))
            overlap = query_words.intersection(heading_words)
            
            # If query words appear significantly in heading/section, boost score
            if overlap:
                match_ratio = len(overlap) / len(query_words)
                if match_ratio >= 0.3: # At least partial match
                    r["score"] *= (1.0 + match_ratio) # Up to 100% boost
                
    # Re-sort by boosted score (descending)
    working_results.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top_k
    return working_results[:top_k]

def delete_document_vectors(doc_id: str):
    collection = get_collection()
    collection.delete(where={"document_id": doc_id})
    logger.info(f"Deleted vectors for doc {doc_id}")
