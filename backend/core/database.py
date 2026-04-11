import asyncio
import logging
from typing import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

# Use SQLite for development
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Use SQLite sync engine for GeoPandas
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+aiosqlite", ""),
    echo=False,
)


def _build_redis_client():
    """Build cache client - use memory cache for development."""
    if settings.REDIS_URL.startswith("memory://"):
        from core.memory_cache import memory_cache
        return memory_cache
    else:
        return Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)


redis_client = _build_redis_client()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    async with async_session_maker() as session:
        yield session


async def init_db(retries: int = 5, base_delay: float = 1.0) -> None:
    """Initialize database and create tables with retry."""
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            async with engine.begin() as conn:
                # For SQLite, enable spatial extension if available
                try:
                    await conn.execute(text("SELECT load_extension('mod_spatialite')"))
                except Exception:
                    # SpatiaLite not available, continue without spatial extensions
                    logger.warning("SpatiaLite extension not available, using basic geometry support")
                
                # Create all tables
                await conn.run_sync(Base.metadata.create_all)
                
            logger.info("Database initialized successfully")
            
            # Apply database enhancements for optimal performance
            try:
                from .database_enhancements import enhance_database_setup
                enhancements = await enhance_database_setup(engine)
                logger.info(f"Database enhancements applied: {enhancements}")
            except ImportError:
                logger.warning("Database enhancements module not found, skipping optimizations")
            except Exception as e:
                logger.warning(f"Database enhancements failed: {e}")
            
            return
        except Exception as exc:  # pragma: no cover
            last_error = exc
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                "Database init attempt %s/%s failed: %s. Retrying in %.1fs",
                attempt,
                retries,
                exc,
                delay,
            )
            await asyncio.sleep(delay)
    raise RuntimeError(f"Failed to initialize database after {retries} attempts: {last_error}")


async def check_tables_exist() -> bool:
    """Check if core seeded table exists."""
    async with engine.begin() as conn:
        result = await conn.execute(
            text(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='demographic_zones'
                """
            )
        )
    return bool(result.scalar())


async def comprehensive_health_check() -> dict:
    """
    Comprehensive health check for database and spatial capabilities.
    
    Returns:
        dict: Health status with detailed information
    """
    health_status = {
        'database_connected': False,
        'spatial_available': False,
        'tables_exist': False,
        'cache_connected': False,
        'data_populated': False,
        'errors': []
    }
    
    try:
        # Test database connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            health_status['database_connected'] = True
            
            # Check if tables exist
            health_status['tables_exist'] = await check_tables_exist()
            
            # Check data population
            if health_status['tables_exist']:
                result = await conn.execute(text("SELECT COUNT(*) FROM demographic_zones"))
                demo_count = result.scalar()
                result = await conn.execute(text("SELECT COUNT(*) FROM points_of_interest"))
                poi_count = result.scalar()
                health_status['data_populated'] = demo_count > 0 and poi_count > 0
                health_status['demo_zones'] = demo_count
                health_status['poi_count'] = poi_count
    
    except Exception as e:
        health_status['errors'].append(f"Database check failed: {str(e)}")
    
    try:
        # Test cache connection
        await redis_client.ping()
        health_status['cache_connected'] = True
    except Exception as e:
        health_status['errors'].append(f"Cache check failed: {str(e)}")
    
    # Overall health status
    health_status['overall_healthy'] = (
        health_status['database_connected'] and
        health_status['cache_connected'] and
        len(health_status['errors']) == 0
    )
    
    return health_status
