from aiogram.filters import BaseFilter
from aiogram.types import Message

class IsPrivateChat(BaseFilter):
    """Filter to check if the chat is a private chat."""
    async def __call__(self, message: Message) -> bool:
        return message.chat.type == 'private'
