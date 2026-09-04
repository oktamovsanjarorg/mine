from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
import structlog
from src.config import settings

logger = structlog.get_logger()

class ThrottleMiddleware(BaseMiddleware):
    """Rate limiting middleware to prevent spam."""
    def __init__(self, rate_limit: int = 30, period: int = 60, redis_client=None):
        self.rate_limit = rate_limit
        self.period = period
        self.redis_client = redis_client

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = None
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user

        if not user or not self.redis_client:
            return await handler(event, data)

        if user.id in settings.bot_admin_ids:
            return await handler(event, data)

        key = f"throttle:{user.id}"
        
        # Redis INCR + EXPIRE pattern
        current = await self.redis_client.incr(key)
        if current == 1:
            await self.redis_client.expire(key, self.period)

        if current > self.rate_limit:
            throttle_msg = "⏳ Kechirasiz, siz juda ko'p so'rov yubordingiz. Biroz kuting."
            if isinstance(event, Message):
                await event.answer(throttle_msg)
            elif isinstance(event, CallbackQuery):
                await event.answer(throttle_msg, show_alert=True)
            return
            
        return await handler(event, data)
