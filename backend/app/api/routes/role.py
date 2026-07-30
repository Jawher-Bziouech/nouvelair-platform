from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.role import (
    count_users_with_role,
    create_role,
    delete_role,
    get_role,
    get_role_by_nom,
    get_roles,
    update_role,
)
from app.dependencies import get_current_user, get_db, require_roles
from app.models.user import User
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=list[RoleRead])
def list_roles(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_roles(db)


@router.get("/{role_id}", response_model=RoleRead)
def retrieve_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    return role


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_new_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("Administrateur")),
):
    existing_role = get_role_by_nom(db, role_in.nom)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists",
        )
    return create_role(db, role_in)


@router.put("/{role_id}", response_model=RoleRead)
def update_existing_role(
    role_id: int,
    role_in: RoleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("Administrateur")),
):
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    if role_in.nom is not None:
        existing = get_role_by_nom(db, role_in.nom)
        if existing and existing.id != role_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already exists",
            )

    return update_role(db, role, role_in)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("Administrateur")),
):
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    if count_users_with_role(db, role_id) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a role still assigned to users",
        )

    delete_role(db, role)
    return None
