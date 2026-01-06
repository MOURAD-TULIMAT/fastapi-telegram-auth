from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.db.session import init_db, close_db
from app.api.routers import db_health
from app.api.routers import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(db_health.router, prefix=settings.API_PREFIX, tags=["health"])
app.include_router(auth.router, prefix=settings.API_PREFIX, tags=["auth"])

@app.get(f"{settings.API_PREFIX}/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
