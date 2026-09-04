import structlog
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

logger = structlog.get_logger(__name__)

class NotificationService:
    """Service for sending notifications."""
    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot

    async def send_unified_notification(self, user_id: int, text: str, silent: bool = False, reply_markup: Optional[Any] = None) -> bool:
        """Unified bot notification sender with error handling, silent options."""
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=text,
                disable_notification=silent,
                reply_markup=reply_markup
            )
            logger.info("Xabarnoma yuborildi", user_id=user_id, silent=silent)
            return True
        except TelegramAPIError as e:
            logger.error("Xabarnoma yuborishda xatolik", user_id=user_id, error=str(e))
            return False
        except Exception as e:
            logger.error("Kutilmagan xatolik xabarnoma yuborishda", user_id=user_id, error=str(e))
            return False
