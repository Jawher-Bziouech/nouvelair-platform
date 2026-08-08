"""Extract plain text from a knowledge resource (contenu field and/or uploaded file)."""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.config import OCR_MIN_CHARS
from app.models.ressource import RessourceDeConnaissance
from app.services.storage import resolve_stored_path

logger = logging.getLogger(__name__)


def extract_text_from_file(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")

    if ext == ".pdf":
        return _extract_pdf(path)

    if ext in {".docx", ".doc"}:
        if ext == ".doc":
            # Legacy .doc is not reliably parseable without extra native deps.
            return ""
        try:
            import docx
        except ImportError as exc:
            raise RuntimeError("python-docx is required to index DOCX files") from exc
        document = docx.Document(str(path))
        return "\n".join(p.text for p in document.paragraphs if p.text)

    return ""


def _extract_pdf(path: Path) -> str:
    """
    1) Native text layer (pypdf)
    2) If almost empty → OCR (scanned / image PDF)
    """
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("pypdf is required to index PDF files") from exc

    reader = PdfReader(str(path))
    parts = [(page.extract_text() or "") for page in reader.pages]
    text = "\n".join(parts).strip()

    if len(text) >= OCR_MIN_CHARS:
        return text

    logger.info(
        "PDF %s has little selectable text (%s chars) → OCR",
        path.name,
        len(text),
    )
    try:
        from app.services.ocr import ocr_pdf

        ocr_text = ocr_pdf(path)
    except Exception as exc:
        logger.warning("OCR unavailable for %s: %s", path.name, exc)
        return text

    # Prefer OCR when it yields more content; otherwise keep native text.
    if len(ocr_text) > len(text):
        return ocr_text
    return text or ocr_text


def extract_ressource_text(ressource: RessourceDeConnaissance) -> str:
    """
    Build the text corpus for indexing.
    Prefer contenu (blog / note) and append extracted file text when present.
    """
    parts: list[str] = []
    if ressource.contenu and ressource.contenu.strip():
        parts.append(ressource.contenu.strip())

    path = resolve_stored_path(ressource.chemin_fichier)
    if path:
        file_text = extract_text_from_file(path).strip()
        if file_text:
            parts.append(file_text)

    return "\n\n".join(parts).strip()
