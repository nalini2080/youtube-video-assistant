from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Base class every ORM model inherits from."""
    pass


engine = create_async_engine(settings.database_url, echo=False)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields one database session per request."""
    async with AsyncSessionLocal() as session:
        yield session