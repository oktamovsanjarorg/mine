import structlog
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from src.config import settings

logger = structlog.get_logger()

engine: AsyncEngine | None = None
session_factory: async_sessionmaker[AsyncSession] | None = None

async def init_db() -> None:
    """Initialize database engine and session factory."""
    global engine, session_factory
    engine = create_async_engine(
        settings.database_url,
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
    )
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    logger.info("Database initialized", host=settings.db_host, db=settings.db_name)

async def close_db() -> None:
    """Close the database connection."""
    global engine, session_factory
    if engine:
        await engine.dispose()
        engine = None
        session_factory = None
        logger.info("Database connection closed")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session generator."""
    if session_factory is None:
        raise RuntimeError("Database not initialized")
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
