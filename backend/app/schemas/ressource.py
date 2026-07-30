from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.categorie import CategorieRead
from app.schemas.user import UserRead


class RessourceBase(BaseModel):
    titre: str
    type: str = Field(
        description="document | procedure | note | guide | publication_interne | blog"
    )
    contenu: str | None = None
    type_fichier: str | None = None
    chemin_fichier: str | None = None
    categorie_id: int


class RessourceCreate(RessourceBase):
    pass


class RessourceUpdate(BaseModel):
    titre: str | None = None
    type: str | None = None
    contenu: str | None = None
    type_fichier: str | None = None
    chemin_fichier: str | None = None
    categorie_id: int | None = None
    est_indexe: bool | None = None


class RessourceRead(RessourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    auteur_id: int
    date_ajout: datetime | None = None
    est_indexe: bool = False
    categorie: CategorieRead | None = None
    auteur: UserRead | None = None
