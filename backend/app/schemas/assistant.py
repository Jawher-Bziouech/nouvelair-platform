from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CitationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ressource_id: int
    extrait: str
    score_pertinence: float | None = None
    titre_ressource: str | None = None


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    texte: str
    role: str
    date_envoi: datetime | None = None
    citations: list[CitationRead] = []


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    utilisateur_id: int
    date_debut: datetime | None = None
    date_derniere_activite: datetime | None = None


class QuestionRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    session_id: int | None = None


class QuestionResponse(BaseModel):
    session_id: int
    question: MessageRead
    answer: MessageRead
    mode: str  # "openai" | "local"
