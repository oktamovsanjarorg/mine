import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="rss_router")

@router.message(Command("rss"))
async def rss_menu(message: Message) -> None:
    """RSS feed menu."""
    await message.answer("📰 RSS lentalar:\n/news - Yangiliklarni o'qish\n/addrss - Yangi kanal qo'shish")

@router.message(Command("addrss"))
async def add_rss(message: Message) -> None:
    """Add RSS feed."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("RSS havolasini kiriting: /addrss https://rss.example.com")
        return
    url = args[1]
    await message.answer(f"✅ RSS kanal qo'shildi: {url}")

@router.message(Command("news"))
async def read_news(message: Message) -> None:
    """Read unread news."""
    await message.answer("📰 So'nggi yangiliklar:\nHozircha yangiliklar yo'q.")
