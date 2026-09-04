from aiogram.filters import BaseFilter
from aiogram.types import Message

class HasURL(BaseFilter):
    """Filter to check if message contains URL entities."""
    async def __call__(self, message: Message) -> bool:
        if not message.entities:
            return False
        return any(entity.type in ('url', 'text_link') for entity in message.entities)

class HasDocument(BaseFilter):
    """Filter to check if message has a document."""
    async def __call__(self, message: Message) -> bool:
        return bool(message.document)

class HasPhoto(BaseFilter):
    """Filter to check if message has a photo."""
    async def __call__(self, message: Message) -> bool:
        return bool(message.photo)

class HasVoice(BaseFilter):
    """Filter to check if message has a voice note."""
    async def __call__(self, message: Message) -> bool:
        return bool(message.voice)

class IsForwarded(BaseFilter):
    """Filter to check if message is forwarded."""
    async def __call__(self, message: Message) -> bool:
        return bool(message.forward_date or message.forward_origin)
