from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RessourceDeConnaissance(Base):
    __tablename__ = "ressources_connaissance"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    contenu = Column(Text, nullable=True)
    type_fichier = Column(String(50), nullable=True)
    chemin_fichier = Column(String(500), nullable=True)
    date_ajout = Column(DateTime(timezone=True), server_default=func.now())
    est_indexe = Column(Boolean, nullable=False, default=False)

    categorie_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    auteur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)

    categorie = relationship("Categorie", back_populates="ressources")
    auteur = relationship("User")
