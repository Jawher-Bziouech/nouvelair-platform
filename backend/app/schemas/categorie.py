from pydantic import BaseModel, ConfigDict


class CategorieBase(BaseModel):
    nom: str
    description: str | None = None


class CategorieCreate(CategorieBase):
    pass


class CategorieUpdate(BaseModel):
    nom: str | None = None
    description: str | None = None


class CategorieRead(CategorieBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
