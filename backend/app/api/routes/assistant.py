from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import assistant as assistant_crud
from app.dependencies import get_current_user, get_db
from app.models.assistant import Citation, MessageAssistant
from app.models.ressource import RessourceDeConnaissance
from app.models.user import User
from app.schemas.assistant import (
    CitationRead,
    MessageRead,
    QuestionRequest,
    QuestionResponse,
    SessionRead,
)
from app.services.rag import answer_question

router = APIRouter(prefix="/assistant", tags=["assistant"])


def _citation_read(cit: Citation, titre_map: dict[int, str]) -> CitationRead:
    return CitationRead(
        id=cit.id,
        ressource_id=cit.ressource_id,
        extrait=cit.extrait,
        score_pertinence=cit.score_pertinence,
        titre_ressource=titre_map.get(cit.ressource_id),
    )


def _message_read(msg: MessageAssistant, titre_map: dict[int, str] | None = None) -> MessageRead:
    titre_map = titre_map or {}
    return MessageRead(
        id=msg.id,
        session_id=msg.session_id,
        texte=msg.texte,
        role=msg.role,
        date_envoi=msg.date_envoi,
        citations=[_citation_read(c, titre_map) for c in (msg.citations or [])],
    )


def _titres_for_ids(db: Session, ids: set[int]) -> dict[int, str]:
    if not ids:
        return {}
    rows = (
        db.query(RessourceDeConnaissance.id, RessourceDeConnaissance.titre)
        .filter(RessourceDeConnaissance.id.in_(ids))
        .all()
    )
    return {r.id: r.titre for r in rows}


@router.get("/sessions", response_model=list[SessionRead])
def list_my_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return assistant_crud.list_sessions(db, current_user.id)


@router.get("/sessions/{session_id}/messages", response_model=list[MessageRead])
def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = assistant_crud.get_session(db, session_id)
    if not session or session.utilisateur_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    messages = assistant_crud.get_session_messages(db, session_id)
    ressource_ids: set[int] = set()
    for m in messages:
        for c in m.citations or []:
            ressource_ids.add(c.ressource_id)
    titres = _titres_for_ids(db, ressource_ids)
    return [_message_read(m, titres) for m in messages]


@router.post("/question", response_model=QuestionResponse)
def ask_question(
    body: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ask the knowledge assistant.
    Creates a session on first message, stores Q/A + citations for traceability.
    """
    question = body.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is required",
        )

    if body.session_id is not None:
        session = assistant_crud.get_session(db, body.session_id)
        if not session or session.utilisateur_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
    else:
        session = assistant_crud.create_session(db, current_user.id)

    user_msg = assistant_crud.add_message(
        db, session_id=session.id, texte=question, role="user"
    )

    answer_text, passages, generation = answer_question(question)

    # Keep only citations that still exist in MySQL (avoids stale vector-store IDs)
    if passages:
        ids = {int(p["ressource_id"]) for p in passages}
        existing = {
            row.id
            for row in db.query(RessourceDeConnaissance.id)
            .filter(RessourceDeConnaissance.id.in_(ids))
            .all()
        }
        passages = [p for p in passages if int(p["ressource_id"]) in existing]

    assistant_msg = assistant_crud.add_message(
        db, session_id=session.id, texte=answer_text, role="assistant"
    )
    citations = assistant_crud.add_citations(
        db, message_id=assistant_msg.id, passages=passages
    )
    assistant_msg.citations = citations
    assistant_crud.touch_session(db, session)

    titres = {p["ressource_id"]: p.get("titre") or "" for p in passages}

    return QuestionResponse(
        session_id=session.id,
        question=_message_read(user_msg),
        answer=_message_read(assistant_msg, titres),
        mode=generation,
    )
