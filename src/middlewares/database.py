from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker
import structlog

logger = structlog.get_logger()

class DatabaseMiddleware(BaseMiddleware):
    """Database session management middleware."""
    def __init__(self, session_factory: async_sessionmaker | None = None):
        self._session_factory = session_factory

    @property
    def session_factory(self) -> async_sessionmaker:
        if self._session_factory is not None:
            return self._session_factory
        from src.core import database
        if database.session_factory is None:
            raise RuntimeError("Database session factory is not initialized")
        return database.session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_factory() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                logger.error("Database transaction rollback", error=str(e))
                raise e
