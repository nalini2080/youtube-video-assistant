from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Base class every ORM model inherits from."""
    pass


def _build_engine_kwargs(database_url: str):
    """
    Hosted Postgres providers like Neon include 'sslmode' and
    'channel_binding' in their connection strings. Our async driver
    (asyncpg) doesn't recognize those as URL parameters — they're specific
    to a different driver's DSN format. We strip them out here and pass the
    SSL requirement through connect_args instead, so a Neon connection
    string can be pasted in as-is without manual editing.
    """
    parsed = urlparse(database_url)
    query = parse_qs(parsed.query)
    query.pop("sslmode", None)
    query.pop("channel_binding", None)
    cleaned = parsed._replace(query=urlencode(query, doseq=True))
    clean_url = urlunparse(cleaned)

    connect_args = {}
    if "asyncpg" in parsed.scheme:
        connect_args["ssl"] = "require"

    return clean_url, connect_args


_clean_url, _connect_args = _build_engine_kwargs(settings.database_url)
engine = create_async_engine(_clean_url, echo=False, connect_args=_connect_args)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields one database session per request."""
    async with AsyncSessionLocal() as session:
        yield session