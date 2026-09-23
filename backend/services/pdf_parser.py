import fitz  # PyMuPDF
from typing import List, Dict, Any
from backend.services.ocr import perform_ocr
from backend.utils.config import settings
from backend.utils.logging import setup_logger

logger = setup_logger("pdf_parser")

def parse_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Parses a PDF and returns a list of dictionaries, one per page.
    Each dict contains: page_number, text, headings, tables (optional).
    """
    try:
        doc = fitz.open(file_path)
        pages_data = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()

            # If text is empty and OCR is enabled, try OCR
            if not text.strip() and settings.OCR_ENABLED:
                logger.info(f"Page {page_num+1} is empty, attempting OCR...")
                pix = page.get_pixmap()
                image_bytes = pix.tobytes("png")
                text = perform_ocr(image_bytes)

            pages_data.append({
                "page_number": page_num + 1,
                "text": text,
                "headings": extract_headings(page),
            })
            
        doc.close()
        return pages_data
    except Exception as e:
        logger.error(f"Failed to parse PDF {file_path}: {e}")
        raise e

def extract_headings(page) -> List[str]:
    # A simple heuristic to extract headings using font size
    headings = []
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if b['type'] == 0:  # text block
            for l in b["lines"]:
                for s in l["spans"]:
                    # Assume text larger than 12pt is a heading
                    if s['size'] > 12:
                        headings.append(s['text'].strip())
    return [h for h in headings if h]
