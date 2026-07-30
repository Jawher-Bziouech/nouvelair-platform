from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate


def get_roles(db: Session) -> list[Role]:
    return db.query(Role).order_by(Role.id.asc()).all()


def get_role(db: Session, role_id: int) -> Role | None:
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_nom(db: Session, nom: str) -> Role | None:
    return db.query(Role).filter(Role.nom == nom).first()


def create_role(db: Session, role_in: RoleCreate) -> Role:
    role = Role(nom=role_in.nom)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role: Role, role_in: RoleUpdate) -> Role:
    data = role_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(role, field, value)
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role: Role) -> None:
    db.delete(role)
    db.commit()


def count_users_with_role(db: Session, role_id: int) -> int:
    return db.query(User).filter(User.role_id == role_id).count()
