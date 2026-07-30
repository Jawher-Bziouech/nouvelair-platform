from sqlalchemy.orm import Session

from app.models.categorie import Categorie
from app.schemas.categorie import CategorieCreate, CategorieUpdate


def get_categories(db: Session) -> list[Categorie]:
    return db.query(Categorie).order_by(Categorie.id.asc()).all()


def get_categorie(db: Session, categorie_id: int) -> Categorie | None:
    return db.query(Categorie).filter(Categorie.id == categorie_id).first()


def get_categorie_by_nom(db: Session, nom: str) -> Categorie | None:
    return db.query(Categorie).filter(Categorie.nom == nom).first()


def create_categorie(db: Session, categorie_in: CategorieCreate) -> Categorie:
    categorie = Categorie(
        nom=categorie_in.nom,
        description=categorie_in.description,
    )
    db.add(categorie)
    db.commit()
    db.refresh(categorie)
    return categorie


def update_categorie(
    db: Session,
    categorie: Categorie,
    categorie_in: CategorieUpdate,
) -> Categorie:
    data = categorie_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(categorie, field, value)
    db.commit()
    db.refresh(categorie)
    return categorie


def delete_categorie(db: Session, categorie: Categorie) -> None:
    db.delete(categorie)
    db.commit()
