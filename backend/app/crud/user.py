from sqlalchemy.orm import Session, joinedload

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_users(db: Session) -> list[User]:
    return (
        db.query(User)
        .options(joinedload(User.role))
        .order_by(User.id.asc())
        .all()
    )


def get_user(db: Session, user_id: int) -> User | None:
    return (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == user_id)
        .first()
    )


def get_user_by_email(db: Session, email: str) -> User | None:
    return (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.email == email)
        .first()
    )


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        nom=user_in.nom,
        prenom=user_in.prenom,
        email=user_in.email,
        mot_de_passe=hash_password(user_in.mot_de_passe),
        role_id=user_in.role_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return get_user(db, user.id)


def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    data = user_in.model_dump(exclude_unset=True)
    if "mot_de_passe" in data and data["mot_de_passe"]:
        data["mot_de_passe"] = hash_password(data["mot_de_passe"])
    elif "mot_de_passe" in data:
        data.pop("mot_de_passe")

    for field, value in data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return get_user(db, user.id)


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def count_users(db: Session) -> int:
    return db.query(User).count()
