import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from aiogram import Bot
from src.core.settings import Settings
from src.infrastructure.database.models import User
import uuid

@pytest.fixture
def test_settings():
    return Settings(
        BOT_TOKEN="123456789:AABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQ",
        DB_URL="sqlite+aiosqlite:///:memory:",
        REDIS_URL="redis://localhost:6379/0",
        ADMIN_ID=123456789,
        LOG_LEVEL="DEBUG"
    )

@pytest.fixture
async def async_engine(test_settings):
    engine = create_async_engine(test_settings.DB_URL, echo=False)
    from src.infrastructure.database.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def async_session(async_engine):
    session_maker = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

@pytest.fixture
def mock_bot():
    bot = AsyncMock(spec=Bot)
    bot.send_message = AsyncMock()
    return bot

@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.delete = AsyncMock()
    return redis

@pytest.fixture
async def test_user(async_session):
    user = User(
        id=uuid.uuid4(),
        telegram_id=123456789,
        full_name="Test User",
        username="testuser",
        is_active=True,
        language_code="uz"
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user
