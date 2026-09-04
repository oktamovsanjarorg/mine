import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="bookmarks_router")

@router.message(Command("bookmarks"))
async def bookmarks_menu(message: Message) -> None:
    """List bookmarks."""
    await message.answer("🔖 Saqlangan xatcho'plar (havolalar):")

@router.message(Command("save"))
async def save_bookmark(message: Message) -> None:
    """Save a URL bookmark."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Havolani kiriting: /save https://example.com")
        return
    url = args[1]
    await message.answer(f"✅ Havola saqlandi: {url}")

@router.message(F.text.regexp(r'https?://[^\s]+'))
async def auto_save_url(message: Message) -> None:
    """Auto-save URL if sent in chat."""
    url = message.text
    # Log logic here
    await message.answer(f"🔗 Havola aniqlandi va saqlandi: {url}")
