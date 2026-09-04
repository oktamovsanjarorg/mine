from aiogram.filters import BaseFilter
from aiogram.types import Message
from src.config import settings

class IsAdmin(BaseFilter):
    """Filter to check if user is an admin."""
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
        return message.from_user.id in settings.bot_admin_ids
