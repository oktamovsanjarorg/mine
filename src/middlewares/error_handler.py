from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from src.config import settings
import structlog
import traceback

logger = structlog.get_logger()

class ErrorHandlerMiddleware(BaseMiddleware):
    """Global error handler middleware."""
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error("Unhandled exception", error=str(e), exc_info=True)
            
            error_msg = "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."
            
            if isinstance(event, Message):
                await event.answer(error_msg)
            elif isinstance(event, CallbackQuery):
                await event.message.answer(error_msg)
                await event.answer()
            elif hasattr(event, "message") and event.message:
                await event.message.answer(error_msg)
                
            bot = data.get("bot")
            if bot and settings.bot_admin_ids:
                admin_msg = f"❗️ <b>Tizimda xatolik:</b>\n<pre><code class='language-python'>{traceback.format_exc()[-2000:]}</code></pre>"
                for admin_id in settings.bot_admin_ids:
                    try:
                        await bot.send_message(admin_id, admin_msg, parse_mode="HTML")
                    except Exception as ex:
                        logger.error("Failed to notify admin", admin_id=admin_id, error=str(ex))
