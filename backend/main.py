from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.routes.auth import router as auth_router
from app.api.routes.categorie import router as categorie_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.ressource import router as ressource_router
from app.api.routes.role import router as role_router
from app.api.routes.user import router as user_router
from app.database import Base, engine
from app.models import categorie, ressource, role, user

Base.metadata.create_all(bind=engine)


def _ensure_contenu_column() -> None:
    """Add contenu column on existing MySQL tables (create_all does not alter)."""
    with engine.begin() as conn:
        exists = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'ressources_connaissance'
                  AND COLUMN_NAME = 'contenu'
                """
            )
        ).scalar()
        if not exists:
            conn.execute(
                text(
                    "ALTER TABLE ressources_connaissance "
                    "ADD COLUMN contenu TEXT NULL AFTER type"
                )
            )


_ensure_contenu_column()

app = FastAPI(title="Nouvelair Knowledge Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(role_router)
app.include_router(user_router)
app.include_router(categorie_router)
app.include_router(ressource_router)
app.include_router(dashboard_router)


@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected"}
