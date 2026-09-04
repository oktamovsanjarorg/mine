from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.user import UserRepository
import structlog

logger = structlog.get_logger()

class AuthMiddleware(BaseMiddleware):
    """Authentication and User registration middleware."""
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = None
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user

        if not user:
            return await handler(event, data)

        session: AsyncSession = data.get("session")
        if not session:
            logger.error("Session not found in data")
            return await handler(event, data)

        user_repo = UserRepository(session)
        
        db_user = await user_repo.get_by_telegram_id(user.id)
        if not db_user:
            db_user = await user_repo.create(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code
            )
        else:
            await user_repo.update_last_active(db_user.id)

        if hasattr(db_user, 'is_active') and not db_user.is_active:
            logger.info("User is not active", user_id=db_user.id)
            return
            
        data["user"] = db_user
        
        return await handler(event, data)
