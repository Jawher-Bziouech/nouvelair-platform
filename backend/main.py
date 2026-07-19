# backend/main.py
from fastapi import FastAPI
from sqlalchemy import text
from app.database import Base, engine
from app.models import role, user

Base.metadata.create_all(bind=engine)


app = FastAPI(title="Nouvelair Knowledge Platform")

@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected"}