from collections.abc import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db as _get_db
from core.database import redis_client


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async SQLAlchemy session."""
    async for session in _get_db():
        yield session


async def get_redis() -> Redis:
    """Dependency that provides a Redis client."""
    return redis_client
