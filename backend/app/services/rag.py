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

import logging
import re

logger = logging.getLogger(__name__)

from app.core.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    RAG_TOP_K,
)
from app.services.indexer import extract_search_terms, query_relevant_chunks

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
    "Réponds en français, comme un collègue expérimenté : explique avec tes propres mots, "
    "ne recopie jamais les extraits bruts ni les cases à cocher. "
    "Commence par une phrase qui répond directement à la question, "
    "puis détaille en paragraphes courts ou listes (un élément par ligne). "
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
    filtered = [p for p in passages if float(p.get("score") or 0) >= min_score]
    if filtered:
        return filtered
    # Keep best match when typos / phrasing lowered scores but something was retrieved
    if passages and float(passages[0].get("score") or 0) >= 0.1:
        return passages[:3]
    return []


def _retrieve_passages(question: str, top_k: int) -> list[dict]:
    """Search with full question plus keyword-only variant (helps natural-language queries)."""
    merged: dict[tuple[int, int], dict] = {}
    keyword_q = extract_search_terms(question)
    queries = [question]
    if keyword_q and keyword_q.lower() != question.strip().lower():
        queries.append(keyword_q)

    for q in queries:
        for p in query_relevant_chunks(q, top_k=top_k):
            key = (int(p["ressource_id"]), int(p.get("chunk_index") or 0))
            prev = merged.get(key)
            if not prev or float(p.get("score") or 0) > float(prev.get("score") or 0):
                merged[key] = p

    return sorted(merged.values(), key=lambda x: float(x.get("score") or 0), reverse=True)[:top_k]


def _extract_steps(text: str) -> list[str]:
    """Pull checklist or list items out of raw document text."""
    text = (text or "").replace("\r\n", "\n")
    items: list[str] = []

    for line in text.split("\n"):
        line = line.strip()
        match = re.match(r"^\[\s*[xX ]?\s*\]\s*(.+)$", line)
        if match:
            items.append(match.group(1).strip())

    if not items:
        for match in re.finditer(r"\[\s*\]\s*([^[\]]+?)(?=\[\s*\]|$)", text):
            item = match.group(1).strip()
            if item:
                items.append(item)

    if not items:
        for line in text.split("\n"):
            line = line.strip()
            match = re.match(r"^(?:\d+[.)]\s+|[-•–]\s+)(.+)$", line)
            if match:
                items.append(match.group(1).strip())

    return [item for item in items if item]


def _humanize_item(item: str) -> str:
    """Turn terse checklist labels into short actionable phrases."""
    item = item.strip().rstrip(".")
    if not item:
        return item

    lower = item.lower()
    verb_starts = (
        "effectuer",
        "organiser",
        "vérifier",
        "verifier",
        "contrôler",
        "controler",
        "confirmer",
        "clôturer",
        "cloturer",
        "valider",
        "préparer",
        "preparer",
        "réaliser",
        "realiser",
    )
    if any(lower.startswith(v) for v in verb_starts):
        return item[0].upper() + item[1:]

    if "briefing" in lower:
        return f"Organiser le {lower}"
    if "contrôle" in lower or "controle" in lower:
        if "document" in lower:
            return "Effectuer le contrôle des documents"
        return f"Effectuer le {lower}"
    if "confirmation" in lower or "charge utile" in lower:
        return f"Confirmer la {lower}"
    if "go" in lower or "no-go" in lower or "dispatch" in lower:
        return f"Valider la décision {lower} avec le dispatch"
    if "clôture" in lower or "cloture" in lower or "dossier" in lower:
        return f"Clôturer le {lower.replace('clôture ', '').replace('cloture ', '')}"

    return item[0].upper() + item[1:]


def _intro_for_question(question: str, titre: str) -> str:
    q = question.lower()
    if any(w in q for w in ("départ", "depart", "avant", "vol", "vole")):
        return (
            f"Avant le départ d'un vol, la procédure **{titre}** "
            "prévoit les étapes suivantes :"
        )
    if any(w in q for w in ("embarquement", "embarquer", "passager")):
        return f"Pour l'embarquement, **{titre}** indique de suivre ces points :"
    if any(w in q for w in ("vpn", "connexion", "accès", "acces", "connecter")):
        return f"Pour vous connecter au VPN, **{titre}** décrit la marche à suivre :"
    if any(w in q for w in ("réclamation", "reclamation", "client", "plainte")):
        return f"En cas de réclamation client, **{titre}** prévoit :"
    if any(w in q for w in ("comment", "quoi", "que faire", "procédure", "procedure", "étapes", "etapes")):
        return f"Voici ce qu'il faut retenir d'après **{titre}** :"
    return f"D'après **{titre}**, voici les éléments essentiels :"


def _strip_doc_header(text: str) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if ":" in text[:50]:
        head, body = text.split(":", 1)
        if len(head.split()) <= 5 and body.strip():
            return body.strip()
    return text


def _synthesize_passage(question: str, passage: dict) -> str:
    titre = passage.get("titre") or f"Ressource #{passage.get('ressource_id')}"
    extrait = (passage.get("extrait") or "").strip()
    steps = _extract_steps(extrait)

    if steps:
        lines = [_intro_for_question(question, titre), ""]
        for i, step in enumerate(steps, 1):
            lines.append(f"{i}. {_humanize_item(step)}")
        return "\n".join(lines)

    body = _strip_doc_header(extrait)
    intro = _intro_for_question(question, titre)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]

    if len(sentences) > 1:
        lines = [intro, ""]
        for sentence in sentences[:6]:
            lines.append(f"- {sentence}")
        return "\n".join(lines)

    if len(body) > 320:
        return f"{intro}\n\n{body[:320].rstrip()}…"
    return f"{intro}\n\n{body}"


def _fallback_answer(question: str, passages: list[dict]) -> str:
    if not passages:
        return (
            "Je n’ai pas trouvé de ressource indexée suffisamment pertinente pour cette question. "
            "Reformulez avec des mots-clés métier (procédure, guide, sécurité, RH…), "
            "ou vérifiez que les ressources concernées sont bien indexées."
        )

    lines = [_synthesize_passage(question, passages[0])]

    others = [
        p.get("titre")
        for p in passages[1:3]
        if p.get("titre") and p.get("titre") != passages[0].get("titre")
    ]
    if others:
        lines.append("")
        lines.append(f"_Ressources connexes consultées : {', '.join(others)}._")

    lines.append("")
    lines.append("Les sources ci-dessous reprennent le texte officiel pour vérification.")
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


def _gemini_models() -> list[str]:
    """Primary model first, then lighter free-tier backups when overloaded."""
    preferred = (GEMINI_MODEL or "").strip()
    backups = [
        "gemini-flash-lite-latest",
        "gemini-3.5-flash-lite",
        "gemini-flash-latest",
    ]
    ordered: list[str] = []
    for name in [preferred, *backups]:
        if name and name not in ordered:
            ordered.append(name)
    return ordered


def _gemini_answer(question: str, passages: list[dict]) -> str:
    import time

    from google import genai
    from google.genai import errors as genai_errors

    if not passages:
        return _fallback_answer(question, passages)

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"{_SYSTEM}\n\n{_user_prompt(question, passages)}"
    last_error: Exception | None = None

    for model in _gemini_models():
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                text = (getattr(response, "text", None) or "").strip()
                if text:
                    if model != GEMINI_MODEL:
                        logger.info("Gemini answered with backup model %s", model)
                    return text
            except (genai_errors.ServerError, genai_errors.ClientError) as exc:
                last_error = exc
                status = getattr(exc, "status_code", None)
                logger.warning(
                    "Gemini %s failed (attempt %s, status=%s): %s",
                    model,
                    attempt + 1,
                    status,
                    exc,
                )
                # Retry once on transient overload / rate limit
                if status in {429, 503} and attempt == 0:
                    time.sleep(0.8)
                    continue
                break
            except Exception as exc:
                last_error = exc
                logger.warning("Gemini %s failed: %s", model, exc)
                break

    if last_error:
        raise last_error
    return _fallback_answer(question, passages)


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


def answer_question(question: str, top_k: int = RAG_TOP_K) -> tuple[str, list[dict], str]:
    if _is_greeting(question):
        return _greeting_answer(question), [], "greeting"

    passages = _filter_passages(_retrieve_passages(question, top_k=top_k))
    mode = llm_mode()
    generation = mode

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
            generation = "local"
    except Exception:
        logger.exception("LLM generation failed (%s), using local fallback", mode)
        text = _fallback_answer(question, passages)
        generation = "local-fallback"

    return text, passages, generation
