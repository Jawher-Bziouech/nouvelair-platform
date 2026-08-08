from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class SessionAssistant(Base):
    """One chat thread between a user and the RAG assistant."""

    __tablename__ = "sessions_assistant"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    date_debut = Column(DateTime(timezone=True), server_default=func.now())
    date_derniere_activite = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    utilisateur = relationship("User")
    messages = relationship(
        "MessageAssistant",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="MessageAssistant.id",
    )


class MessageAssistant(Base):
    __tablename__ = "messages_assistant"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions_assistant.id"), nullable=False)
    texte = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # user | assistant
    date_envoi = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("SessionAssistant", back_populates="messages")
    citations = relationship(
        "Citation",
        back_populates="message",
        cascade="all, delete-orphan",
    )


class Citation(Base):
    """Excerpt from a knowledge resource that justified an assistant answer."""

    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages_assistant.id"), nullable=False)
    ressource_id = Column(
        Integer,
        ForeignKey("ressources_connaissance.id", ondelete="CASCADE"),
        nullable=False,
    )
    extrait = Column(Text, nullable=False)
    score_pertinence = Column(Float, nullable=True)

    message = relationship("MessageAssistant", back_populates="citations")
    ressource = relationship("RessourceDeConnaissance")
