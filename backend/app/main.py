from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.config import settings
from app.api import videos
from app.database import engine, Base, AsyncSessionLocal
import app.models  # noqa: F401 — registers models with Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev-only convenience: create any tables that don't exist yet, straight
    # from the ORM models. A real production setup would use a migration
    # tool (Alembic) instead, so schema changes are tracked and reversible —
    # skipped here since the schema is still actively evolving.
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="YouTube Video Research Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(videos.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/health/db")
async def health_check_db():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}

@app.get("/")
def root():
    return {"message": "VideoLens API is running. See /docs for available endpoints."}