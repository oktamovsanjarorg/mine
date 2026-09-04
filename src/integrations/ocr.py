import structlog
import io
from typing import Optional

try:
    from PIL import Image
    import pytesseract
    HAS_PYTESSERACT = True
except ImportError:
    HAS_PYTESSERACT = False

logger = structlog.get_logger(__name__)

class OCRClient:
    """OCR Client using pytesseract."""

    async def extract_text(self, image_bytes: bytes, lang: str = "uzb+eng+rus") -> str:
        if not HAS_PYTESSERACT:
            logger.error("pytesseract or PIL is not installed.")
            return "OCR xizmati hozircha mavjud emas 😢"
        
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Blocking call in async context, in real production wrap in run_in_executor
            text = pytesseract.image_to_string(image, lang=lang)
            return text.strip()
        except Exception as e:
            logger.error("OCR extract_text failed", error=str(e))
            return "Matnni o'qib bo'lmadi 😢"

ocr_client = OCRClient()
