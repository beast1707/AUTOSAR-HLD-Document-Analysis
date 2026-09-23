import pytesseract
from PIL import Image
import io
from backend.utils.logging import setup_logger

logger = setup_logger("ocr")

def perform_ocr(image_bytes: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""
