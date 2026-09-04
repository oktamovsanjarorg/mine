import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="pomodoro_router")

@router.message(Command("pomodoro", "pomo"))
async def pomodoro_menu(message: Message) -> None:
    """Pomodoro timer dashboard."""
    await message.answer(
        "🍅 <b>Pomodoro Taymeri</b>\n\n"
        "25 daqiqalik fokus vaqtini boshlash uchun quyidagi tugmani bosing.",
        parse_mode="HTML"
        # Inline Keyboard should be added here
    )
