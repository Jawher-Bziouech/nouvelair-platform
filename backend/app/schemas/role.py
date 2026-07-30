from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    nom: str


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    nom: str | None = None


class RoleRead(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
