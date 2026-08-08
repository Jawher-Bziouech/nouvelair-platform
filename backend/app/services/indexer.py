"""
Index knowledge resources into a local vector store for RAG retrieval.

Why not ChromaDB here?
  ChromaDB's native dependency (chroma-hnswlib) needs a C++ toolchain and often
  fails on Windows / newer Python. We keep the same RAG idea — chunk, embed,
  search, cite — with a portable JSON-backed store under backend/vector_store/.

Embedding strategy:
  Lightweight hashing bag-of-words embeddings (dim=384). Works offline with no
  model download. Good enough for French keyword-ish retrieval in demos.
  Generation can still use OpenAI when OPENAI_API_KEY is set.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import threading
from collections import Counter
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import BASE_DIR, CHUNK_OVERLAP, CHUNK_SIZE, RAG_TOP_K, VECTOR_DIR
from app.models.ressource import RessourceDeConnaissance
from app.services.text_extract import extract_ressource_text

STORE_PATH = VECTOR_DIR / "chunks.json"
EMBED_DIM = 384

_lock = threading.Lock()


def _ensure_store() -> list[dict]:
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.exists():
        STORE_PATH.write_text("[]", encoding="utf-8")
        return []
    try:
        return json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _save_store(rows: list[dict]) -> None:
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Zàâäéèêëïîôùûüç0-9]+", text.lower())


def _stable_bucket(tok: str, dim: int) -> int:
    digest = hashlib.md5(tok.encode("utf-8")).hexdigest()
    return int(digest, 16) % dim


def _embed(text: str, dim: int = EMBED_DIM) -> list[float]:
    counts = Counter(_tokenize(text))
    vec = [0.0] * dim
    for tok, n in counts.items():
        idx = _stable_bucket(tok, dim)
        vec[idx] += float(n)
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


def clear_vector_store() -> None:
    """Wipe all indexed chunks (used by seed / full rebuild)."""
    with _lock:
        _save_store([])


def delete_ressource_vectors(ressource_id: int) -> None:
    with _lock:
        rows = [r for r in _ensure_store() if int(r.get("ressource_id", -1)) != ressource_id]
        _save_store(rows)


def _keyword_overlap(question: str, document: str, titre: str = "") -> float:
    """Share of query tokens found in titre+document (helps names / typos resistance)."""
    q_tokens = [t for t in _tokenize(question) if len(t) > 2]
    if not q_tokens:
        return 0.0
    hay = f"{titre} {document}".lower()
    hits = 0
    for tok in q_tokens:
        if tok in hay:
            hits += 1
            continue
        # soft match: prefix for typos like reciept/receipt
        if len(tok) >= 5 and any(tok[:4] in w for w in _tokenize(hay) if len(w) >= 4):
            hits += 0.6
    return hits / len(q_tokens)


def index_ressource(db: Session, ressource: RessourceDeConnaissance) -> bool:
    """
    Extract → chunk → upsert embeddings → set est_indexe.
    Returns True when at least one chunk was indexed.
    """
    text = extract_ressource_text(ressource)
    # Include title so queries like "receipt" match even if body is sparse
    titre = (ressource.titre or "").strip()
    if titre:
        text = f"{titre}\n\n{text}".strip() if text else titre

    delete_ressource_vectors(ressource.id)

    chunks = chunk_text(text)
    if not chunks:
        ressource.est_indexe = False
        db.add(ressource)
        db.commit()
        db.refresh(ressource)
        return False

    new_rows = []
    for i, chunk in enumerate(chunks):
        new_rows.append(
            {
                "id": f"r{ressource.id}_c{i}",
                "ressource_id": ressource.id,
                "titre": titre[:200],
                "type": ressource.type or "",
                "chunk_index": i,
                "document": chunk,
                "embedding": _embed(chunk),
            }
        )

    with _lock:
        rows = [r for r in _ensure_store() if int(r.get("ressource_id", -1)) != ressource.id]
        rows.extend(new_rows)
        _save_store(rows)

    ressource.est_indexe = True
    db.add(ressource)
    db.commit()
    db.refresh(ressource)
    return True


def query_relevant_chunks(question: str, top_k: int = RAG_TOP_K) -> list[dict]:
    """Return ranked passages: {ressource_id, titre, extrait, score, chunk_index}."""
    with _lock:
        rows = _ensure_store()

    if not rows:
        return []

    q_vec = _embed(question)
    scored: list[tuple[float, dict]] = []
    for row in rows:
        emb = row.get("embedding") or []
        if len(emb) != len(q_vec):
            continue
        cosine = _cosine(q_vec, emb)
        overlap = _keyword_overlap(
            question,
            row.get("document") or "",
            row.get("titre") or "",
        )
        # Hybrid: embeddings + explicit keyword hits (names, titles)
        score = 0.55 * cosine + 0.45 * overlap
        scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    passages: list[dict] = []
    for score, row in scored[:top_k]:
        passages.append(
            {
                "ressource_id": int(row["ressource_id"]),
                "titre": row.get("titre") or "",
                "extrait": row.get("document") or "",
                "score": round(float(score), 4),
                "chunk_index": int(row.get("chunk_index") or 0),
            }
        )
    return passages
