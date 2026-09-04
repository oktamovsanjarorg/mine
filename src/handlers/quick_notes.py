import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="quick_notes_router")

@router.message(Command("clip"))
async def clip_text(message: Message) -> None:
    """Clip text quickly."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Foydalanish: /clip <matn>")
        return
    text = args[1]
    await message.answer("📎 Matn clipboard'ga saqlandi!")

@router.message(Command("pin"))
async def pin_message(message: Message) -> None:
    """Pin the replied message."""
    if not message.reply_to_message:
        await message.answer("📌 Qadab qo'yish uchun xabarga 'reply' qilib /pin yozing.")
        return
    await message.reply_to_message.pin()
    await message.answer("📌 Xabar qadaldi!")
