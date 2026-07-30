from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.categorie import (
    create_categorie,
    delete_categorie,
    get_categorie,
    get_categorie_by_nom,
    get_categories,
    update_categorie,
)
from app.dependencies import get_current_user, get_db, require_roles
from app.models.user import User
from app.schemas.categorie import CategorieCreate, CategorieRead, CategorieUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategorieRead])
def list_categories(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_categories(db)


@router.get("/{categorie_id}", response_model=CategorieRead)
def retrieve_categorie(
    categorie_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    categorie = get_categorie(db, categorie_id)
    if not categorie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return categorie


@router.post("/", response_model=CategorieRead, status_code=status.HTTP_201_CREATED)
def create_new_categorie(
    categorie_in: CategorieCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("Administrateur")),
):
    existing = get_categorie_by_nom(db, categorie_in.nom)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists",
        )
    return create_categorie(db, categorie_in)


@router.put("/{categorie_id}", response_model=CategorieRead)
def update_existing_categorie(
    categorie_id: int,
    categorie_in: CategorieUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("Administrateur")),
):
    categorie = get_categorie(db, categorie_id)
    if not categorie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    if categorie_in.nom is not None:
        existing = get_categorie_by_nom(db, categorie_in.nom)
        if existing and existing.id != categorie_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists",
            )

    return update_categorie(db, categorie, categorie_in)


@router.delete("/{categorie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_categorie(
    categorie_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("Administrateur")),
):
    categorie = get_categorie(db, categorie_id)
    if not categorie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    delete_categorie(db, categorie)
    return None
