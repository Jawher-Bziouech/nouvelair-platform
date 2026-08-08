"""
OCR helpers for scanned PDFs (pages that are images, not selectable text).

Strategy:
  1. Prefer local Tesseract if installed (optional; needs Pillow + Tesseract)
  2. Else use Gemini vision with the existing free API key (default on this setup)
  3. Cap pages to keep indexing reasonably fast / within free quotas

Page rendering uses PyMuPDF only (no Pillow required for the Gemini path).
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OCR_DPI,
    OCR_ENABLED,
    OCR_MAX_PAGES,
    TESSERACT_CMD,
)

logger = logging.getLogger(__name__)


def _configure_tesseract() -> bool:
    try:
        import pytesseract  # noqa: F401
        from PIL import Image  # noqa: F401
    except ImportError:
        return False

    import pytesseract as pt

    if TESSERACT_CMD:
        pt.pytesseract.tesseract_cmd = TESSERACT_CMD
    try:
        pt.get_tesseract_version()
        return True
    except Exception:
        return False


def _ocr_page_tesseract(png_bytes: bytes) -> str:
    import io

    import pytesseract
    from PIL import Image

    image = Image.open(io.BytesIO(png_bytes))
    return pytesseract.image_to_string(image, lang="fra+eng") or ""


def _ocr_page_gemini(png_bytes: bytes) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = (
        "Extract ALL readable text from this document page. "
        "Keep the original language (usually French). "
        "Return plain text only, no markdown, no commentary."
    )
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=png_bytes, mime_type="image/png"),
            prompt,
        ],
    )
    return (getattr(response, "text", None) or "").strip()


def ocr_pdf(path: Path, *, max_pages: int = OCR_MAX_PAGES, dpi: int = OCR_DPI) -> str:
    """
    Render PDF pages to images and OCR them.
    Returns concatenated text, or "" if OCR is unavailable/disabled.
    """
    if not OCR_ENABLED:
        return ""

    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise RuntimeError("pymupdf is required for OCR of scanned PDFs") from exc

    use_tesseract = _configure_tesseract()
    use_gemini = bool(GEMINI_API_KEY)

    if not use_tesseract and not use_gemini:
        logger.warning(
            "OCR skipped for %s: set GEMINI_API_KEY (or install Tesseract+Pillow)",
            path.name,
        )
        return ""

    engine = "tesseract" if use_tesseract else "gemini"
    logger.info("OCR %s with %s (max %s pages)", path.name, engine, max_pages)

    parts: list[str] = []
    with fitz.open(path) as doc:
        page_count = min(len(doc), max_pages)
        for i in range(page_count):
            page = doc[i]
            pix = page.get_pixmap(dpi=dpi)
            png_bytes = pix.tobytes("png")
            text = ""
            try:
                if use_tesseract:
                    text = _ocr_page_tesseract(png_bytes)
                else:
                    text = _ocr_page_gemini(png_bytes)
            except Exception as exc:
                logger.warning("OCR failed on %s page %s: %s", path.name, i + 1, exc)
                continue

            text = (text or "").strip()
            if text:
                parts.append(text)

    return "\n\n".join(parts).strip()
