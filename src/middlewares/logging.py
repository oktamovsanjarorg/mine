import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
import structlog

logger = structlog.get_logger()

class LoggingMiddleware(BaseMiddleware):
    """Request logging middleware."""
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        start_time = time.monotonic()
        user_id = None
        update_type = type(event).__name__
        action = None

        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            action = event.text or event.caption
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
            action = event.data

        logger.info(
            "Request started",
            user_id=user_id,
            update_type=update_type,
            action=action
        )

        try:
            result = await handler(event, data)
            return result
        finally:
            process_time = time.monotonic() - start_time
            logger.info(
                "Request finished",
                user_id=user_id,
                update_type=update_type,
                process_time=f"{process_time:.3f}s"
            )
