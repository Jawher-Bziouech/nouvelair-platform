from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.categorie import get_categories
from app.crud.ressource import count_ressources, get_ressources
from app.crud.role import get_roles
from app.crud.user import count_users
from app.dependencies import get_db, require_roles
from app.models.ressource import RessourceDeConnaissance
from app.models.user import User
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("Administrateur")),
):
    indexed = (
        db.query(RessourceDeConnaissance)
        .filter(RessourceDeConnaissance.est_indexe.is_(True))
        .count()
    )
    return DashboardStats(
        users=count_users(db),
        roles=len(get_roles(db)),
        categories=len(get_categories(db)),
        ressources=count_ressources(db),
        ressources_indexees=indexed,
    )
