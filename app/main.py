from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)

@app.get(f"{settings.API_PREFIX}/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
