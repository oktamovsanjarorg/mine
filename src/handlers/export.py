import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="export_router")

@router.message(Command("export"))
async def export_data(message: Message) -> None:
    """Export all user data."""
    await message.answer("📤 Ma'lumotlaringiz CSV va JSON formatida tayyorlanmoqda...")

@router.message(Command("backup"))
async def backup_data(message: Message) -> None:
    """Backup data."""
    await message.answer("📦 Ma'lumotlar zaxira nusxasi yaratilmoqda...")

@router.message(Command("import"))
async def import_data(message: Message) -> None:
    """Import data."""
    await message.answer("📥 JSON faylingizni yuboring, men uni import qilaman.")
