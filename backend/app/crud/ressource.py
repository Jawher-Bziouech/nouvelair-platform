from sqlalchemy.orm import Session, joinedload

from app.models.ressource import RessourceDeConnaissance
from app.schemas.ressource import RessourceCreate, RessourceUpdate


def get_ressources(
    db: Session,
    *,
    categorie_id: int | None = None,
    type: str | None = None,
    q: str | None = None,
) -> list[RessourceDeConnaissance]:
    query = db.query(RessourceDeConnaissance).options(
        joinedload(RessourceDeConnaissance.categorie),
        joinedload(RessourceDeConnaissance.auteur),
    )

    if categorie_id is not None:
        query = query.filter(RessourceDeConnaissance.categorie_id == categorie_id)
    if type is not None:
        query = query.filter(RessourceDeConnaissance.type == type)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (RessourceDeConnaissance.titre.ilike(like))
            | (RessourceDeConnaissance.contenu.ilike(like))
        )

    return query.order_by(RessourceDeConnaissance.id.asc()).all()


def get_ressource(db: Session, ressource_id: int) -> RessourceDeConnaissance | None:
    return (
        db.query(RessourceDeConnaissance)
        .options(
            joinedload(RessourceDeConnaissance.categorie),
            joinedload(RessourceDeConnaissance.auteur),
        )
        .filter(RessourceDeConnaissance.id == ressource_id)
        .first()
    )


def create_ressource(
    db: Session,
    ressource_in: RessourceCreate,
    auteur_id: int,
) -> RessourceDeConnaissance:
    ressource = RessourceDeConnaissance(
        titre=ressource_in.titre,
        type=ressource_in.type,
        contenu=ressource_in.contenu,
        type_fichier=ressource_in.type_fichier,
        chemin_fichier=ressource_in.chemin_fichier,
        categorie_id=ressource_in.categorie_id,
        auteur_id=auteur_id,
        est_indexe=False,
    )
    db.add(ressource)
    db.commit()
    db.refresh(ressource)
    return get_ressource(db, ressource.id)


def update_ressource(
    db: Session,
    ressource: RessourceDeConnaissance,
    ressource_in: RessourceUpdate,
) -> RessourceDeConnaissance:
    data = ressource_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(ressource, field, value)
    db.commit()
    db.refresh(ressource)
    return get_ressource(db, ressource.id)


def delete_ressource(db: Session, ressource: RessourceDeConnaissance) -> None:
    db.delete(ressource)
    db.commit()


def count_ressources(db: Session) -> int:
    return db.query(RessourceDeConnaissance).count()


def count_ressources_by_auteur(db: Session, auteur_id: int) -> int:
    return (
        db.query(RessourceDeConnaissance)
        .filter(RessourceDeConnaissance.auteur_id == auteur_id)
        .count()
    )
