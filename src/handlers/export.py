import json
import structlog
from datetime import datetime
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.repositories.export import ExportRepository

logger = structlog.get_logger(__name__)
router = Router(name="export_router")


@router.message(Command("export"))
@router.message(Command("backup"))
async def export_data(message: Message, session: AsyncSession, user: User) -> None:
    """Export all user data into a downloadable JSON file."""
    await message.answer("📤 Ma'lumotlaringiz tayyorlanmoqda, iltimos kuting...")
    try:
        repo = ExportRepository(session)
        data = await repo.get_all_user_data(user.id)
        
        json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M")
        filename = f"sanjarbot_backup_{user.id}_{timestamp_str}.json"
        
        file = BufferedInputFile(json_bytes, filename=filename)
        await message.answer_document(
            document=file,
            caption=(
                "📦 <b>Sizning ma'lumotlaringiz to'liq zaxiralandi!</b>\n\n"
                f"📋 Vazifalar: {len(data.get('tasks', []))} ta\n"
                f"📝 Eslatmalar: {len(data.get('notes', []))} ta\n"
                f"💰 Tranzaksiyalar: {len(data.get('transactions', []))} ta\n"
                f"🌱 Odatlar: {len(data.get('habits', []))} ta\n"
                f"⏰ Eslatmalar: {len(data.get('reminders', []))} ta\n\n"
                "Ushbu faylni xohlagan vaqtda saqlab qo'yishingiz mumkin."
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error("Export error", user_id=user.id, error=str(e))
        await message.answer(f"❌ Eksport qilishda xatolik yuz berdi: {e}")


@router.message(Command("import"))
async def import_data(message: Message) -> None:
    """Import data placeholder."""
    await message.answer("📥 JSON zaxira faylingizni yuboring, uni qayta tiklayman.")
