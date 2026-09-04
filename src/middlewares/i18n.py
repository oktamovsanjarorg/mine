from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

class I18nMiddleware(BaseMiddleware):
    """Internationalization middleware (stub for storing language)."""
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("user")
        if user and hasattr(user, "language_code"):
            data["locale"] = user.language_code
        else:
            tg_user = None
            if isinstance(event, (Message, CallbackQuery)):
                tg_user = event.from_user
            data["locale"] = tg_user.language_code if tg_user else "uz"
            
        return await handler(event, data)
