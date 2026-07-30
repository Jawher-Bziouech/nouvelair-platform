from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.role import RoleRead


class UserBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    role_id: int


class UserCreate(UserBase):
    mot_de_passe: str


class UserUpdate(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    email: EmailStr | None = None
    role_id: int | None = None
    mot_de_passe: str | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_creation: datetime | None = None
    role: RoleRead | None = None
