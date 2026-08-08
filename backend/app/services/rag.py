"""
RAG answer generation.

Flow:
  1. Detect greetings / small talk → short polite reply, no forced citations
  2. Retrieve top-k chunks from the local vector store
  3. Keep only passages above a relevance threshold
  4. Build a grounded answer with (in priority order):
       Gemini (free) → Groq (free) → OpenAI (paid) → local excerpts
"""

from __future__ import annotations

import re

from app.core.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    RAG_TOP_K,
)
from app.services.indexer import query_relevant_chunks

# Hashing embeddings are noisy; hybrid score can be lower — keep a soft floor.
MIN_SCORE = 0.18

_GREETING_RE = re.compile(
    r"^\s*("
    r"bonjour|bonsoir|salut|hello|hi|hey|coucou|yo|"
    r"merci|thanks|thank you|"
    r"au revoir|bye|a\s*bientot|"
    r"comment\s+ca\s+va|ça\s+va\s*\??"
    r")[\s!.?]*$",
    re.IGNORECASE,
)

_SYSTEM = (
    "Tu es l'assistant de la base de connaissances Nouvelair. "
    "Réponds uniquement à partir du contexte fourni. "
    "Si le contexte est insuffisant, dis-le clairement. "
    "Réponds en français, de façon concise et professionnelle. "
    "Cite les numéros de sources [n] utilisés."
)


def llm_mode() -> str:
    """Active generation backend for API responses / UI."""
    if GEMINI_API_KEY:
        return "gemini"
    if GROQ_API_KEY:
        return "groq"
    if OPENAI_API_KEY:
        return "openai"
    return "local"


def _is_greeting(question: str) -> bool:
    q = question.strip()
    if len(q) > 60:
        return False
    return bool(_GREETING_RE.match(q))


def _greeting_answer(question: str) -> str:
    q = question.strip().lower()
    if q.startswith("merci") or "thank" in q:
        return "Avec plaisir. Posez-moi une question sur une procédure, un guide ou une note interne."
    if "revoir" in q or q in {"bye", "au revoir"}:
        return "Au revoir. Je reste disponible pour vos questions sur la base de connaissances."
    return (
        "Bonjour ! Je suis l’assistant de la base de connaissances Nouvelair. "
        "Posez une question précise (ex. : étapes d’embarquement, réclamation client, "
        "consignes sécurité piste) et je m’appuierai sur les ressources indexées."
    )


def _filter_passages(passages: list[dict], min_score: float = MIN_SCORE) -> list[dict]:
    return [p for p in passages if float(p.get("score") or 0) >= min_score]


def _fallback_answer(question: str, passages: list[dict]) -> str:
    if not passages:
        return (
            "Je n’ai pas trouvé de ressource indexée suffisamment pertinente pour cette question. "
            "Reformulez avec des mots-clés métier (procédure, guide, sécurité, RH…), "
            "ou vérifiez que les ressources concernées sont bien indexées."
        )

    best = float(passages[0].get("score") or 0)
    if best < 0.38:
        lines = [
            "Voici les extraits les plus proches, sans garantie de réponse complète :",
            "",
        ]
    else:
        lines = [
            "Voici une réponse fondée sur les ressources de connaissance disponibles :",
            "",
        ]

    for i, p in enumerate(passages, 1):
        titre = p.get("titre") or f"Ressource #{p.get('ressource_id')}"
        extrait = (p.get("extrait") or "").strip()
        if len(extrait) > 420:
            extrait = extrait[:420].rstrip() + "…"
        lines.append(f"{i}. **{titre}** — {extrait}")
        lines.append("")

    lines.append("Les sources (citations) permettent de vérifier chaque extrait.")
    return "\n".join(lines).strip()


def _build_context(passages: list[dict]) -> str:
    blocks = []
    for i, p in enumerate(passages, 1):
        blocks.append(
            f"[{i}] Titre: {p.get('titre')}\n"
            f"Ressource ID: {p.get('ressource_id')}\n"
            f"Extrait: {p.get('extrait')}"
        )
    return "\n\n".join(blocks)


def _user_prompt(question: str, passages: list[dict]) -> str:
    return (
        f"Contexte:\n{_build_context(passages)}\n\n"
        f"Question: {question}\n\n"
        "Réponse:"
    )


def _gemini_answer(question: str, passages: list[dict]) -> str:
    from google import genai

    if not passages:
        return _fallback_answer(question, passages)

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"{_SYSTEM}\n\n{_user_prompt(question, passages)}"
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    text = (getattr(response, "text", None) or "").strip()
    return text or _fallback_answer(question, passages)


def _openai_compatible_answer(
    *,
    api_key: str,
    base_url: str | None,
    model: str,
    question: str,
    passages: list[dict],
) -> str:
    from openai import OpenAI

    if not passages:
        return _fallback_answer(question, passages)

    kwargs: dict = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": _user_prompt(question, passages)},
        ],
        temperature=0.2,
    )
    return (response.choices[0].message.content or "").strip() or _fallback_answer(
        question, passages
    )


def answer_question(question: str, top_k: int = RAG_TOP_K) -> tuple[str, list[dict]]:
    if _is_greeting(question):
        return _greeting_answer(question), []

    passages = _filter_passages(query_relevant_chunks(question, top_k=top_k))
    mode = llm_mode()

    try:
        if mode == "gemini":
            text = _gemini_answer(question, passages)
        elif mode == "groq":
            text = _openai_compatible_answer(
                api_key=GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
                model=GROQ_MODEL,
                question=question,
                passages=passages,
            )
        elif mode == "openai":
            text = _openai_compatible_answer(
                api_key=OPENAI_API_KEY,
                base_url=None,
                model=OPENAI_MODEL,
                question=question,
                passages=passages,
            )
        else:
            text = _fallback_answer(question, passages)
    except Exception:
        text = _fallback_answer(question, passages)

    return text, passages
