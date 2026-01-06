from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_sessionmaker

async def get_db() -> AsyncSession:
    SessionLocal = get_sessionmaker()
    async with SessionLocal() as session:
        yield session