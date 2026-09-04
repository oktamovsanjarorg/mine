import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="health_router")

@router.message(Command("health"))
async def health_menu(message: Message) -> None:
    """Health dashboard."""
    await message.answer("❤️ Salomatlik paneli:\nSuv: 0 ml\nUyqu: 0 soat\nQadamlar: 0")

@router.message(Command("water"))
async def log_water(message: Message) -> None:
    """Log water intake."""
    await message.answer("💧 Qancha suv ichdingiz? (ml da kiriting, masalan: 250)")

@router.message(Command("sleep"))
async def log_sleep(message: Message) -> None:
    """Log sleep hours."""
    await message.answer("😴 Necha soat uxladingiz?")

@router.message(Command("weight"))
async def log_weight(message: Message) -> None:
    """Log weight."""
    await message.answer("⚖️ Joriy vazningizni kiriting (kg):")

@router.message(Command("exercise"))
async def log_exercise(message: Message) -> None:
    """Log exercise."""
    await message.answer("🏋️ Mashg'ulot davomiyligini kiriting (daqiqa):")
