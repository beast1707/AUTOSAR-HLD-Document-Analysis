from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_document(pages_data: List[Dict[str, Any]], chunk_size: int = 900, chunk_overlap: int = 150) -> List[Dict[str, Any]]:
    """
    Takes parsed pages data and returns a list of chunks with metadata.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = []
    for page in pages_data:
        page_num = page["page_number"]
        text = page["text"]
        headings = page.get("headings", [])
        
        # Simple heuristic: last known heading
        current_heading = headings[0] if headings else "General"

        splits = text_splitter.split_text(text)
        for split in splits:
            if not split.strip():
                continue
            chunks.append({
                "page": page_num,
                "heading": current_heading,
                "section": f"Page {page_num}",
                "text": split
            })
            
    return chunks
