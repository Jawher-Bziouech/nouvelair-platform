from pydantic import BaseModel


class DashboardStats(BaseModel):
    users: int
    roles: int
    categories: int
    ressources: int
    ressources_indexees: int
