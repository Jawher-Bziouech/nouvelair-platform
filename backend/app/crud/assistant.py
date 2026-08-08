from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models.assistant import Citation, MessageAssistant, SessionAssistant


def create_session(db: Session, utilisateur_id: int) -> SessionAssistant:
    session = SessionAssistant(utilisateur_id=utilisateur_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: int) -> SessionAssistant | None:
    return (
        db.query(SessionAssistant)
        .options(
            joinedload(SessionAssistant.messages).joinedload(MessageAssistant.citations)
        )
        .filter(SessionAssistant.id == session_id)
        .first()
    )


def list_sessions(db: Session, utilisateur_id: int) -> list[SessionAssistant]:
    return (
        db.query(SessionAssistant)
        .filter(SessionAssistant.utilisateur_id == utilisateur_id)
        .order_by(SessionAssistant.date_derniere_activite.desc())
        .all()
    )


def touch_session(db: Session, session: SessionAssistant) -> None:
    session.date_derniere_activite = datetime.now(timezone.utc)
    db.add(session)
    db.commit()


def add_message(
    db: Session,
    *,
    session_id: int,
    texte: str,
    role: str,
) -> MessageAssistant:
    message = MessageAssistant(session_id=session_id, texte=texte, role=role)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def add_citations(
    db: Session,
    *,
    message_id: int,
    passages: list[dict],
) -> list[Citation]:
    citations: list[Citation] = []
    for p in passages:
        cit = Citation(
            message_id=message_id,
            ressource_id=int(p["ressource_id"]),
            extrait=p.get("extrait") or "",
            score_pertinence=p.get("score"),
        )
        db.add(cit)
        citations.append(cit)
    db.commit()
    return citations


def get_session_messages(db: Session, session_id: int) -> list[MessageAssistant]:
    return (
        db.query(MessageAssistant)
        .options(joinedload(MessageAssistant.citations))
        .filter(MessageAssistant.session_id == session_id)
        .order_by(MessageAssistant.id.asc())
        .all()
    )
