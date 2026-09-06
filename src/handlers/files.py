import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User
from src.models.file import FileRecord
from src.core.utils.formatters import format_file_size

logger = structlog.get_logger(__name__)
router = Router(name="files_router")


@router.message(Command("files"))
@router.message(F.text == "📁 Fayllar")
async def files_menu(message: Message, session: AsyncSession, user: User) -> None:
    """List uploaded files."""
    result = await session.execute(
        select(FileRecord).where(
            FileRecord.user_id == user.id,
            FileRecord.is_deleted == False
        ).order_by(FileRecord.created_at.desc()).limit(15)
    )
    files = result.scalars().all()
    if not files:
        await message.answer(
            "📁 <b>Sizda hozircha yuklangan fayllar yo'q!</b>\n\n"
            "Ixtiyoriy hujjat, rasm, audio yoki videoni shu yerga yuborsangiz, avtomatik saqlab qo'yaman.",
            parse_mode="HTML"
        )
        return

    lines = [f"📁 <b>Sizning fayllaringiz ({len(files)} ta):</b>\n"]
    for i, f in enumerate(files, 1):
        size_str = format_file_size(f.file_size or 0)
        lines.append(f"{i}. 📄 <b>#{f.id}: {f.file_name or 'Fayl'}</b> ({f.file_type}, {size_str})")

    lines.append("\n<i>Yangi fayl saqlash uchun uni botga yuboring.</i>")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(F.document | F.photo | F.audio | F.video)
async def handle_files(message: Message, session: AsyncSession, user: User) -> None:
    """Auto-save documents/media to DB."""
    file_id = None
    file_name = "fayl"
    file_type = "file"
    mime_type = "application/octet-stream"
    file_size = 0

    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name or "document"
        file_type = "document"
        mime_type = message.document.mime_type or "application/octet-stream"
        file_size = message.document.file_size or 0
    elif message.photo:
        ph = message.photo[-1]
        file_id = ph.file_id
        file_name = f"photo_{ph.file_unique_id}.jpg"
        file_type = "photo"
        mime_type = "image/jpeg"
        file_size = ph.file_size or 0
    elif message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name or f"audio_{message.audio.file_unique_id}.mp3"
        file_type = "audio"
        mime_type = message.audio.mime_type or "audio/mpeg"
        file_size = message.audio.file_size or 0
    elif message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or f"video_{message.video.file_unique_id}.mp4"
        file_type = "video"
        mime_type = message.video.mime_type or "video/mp4"
        file_size = message.video.file_size or 0

    record = FileRecord(
        user_id=user.id,
        telegram_file_id=file_id,
        file_name=file_name,
        file_type=file_type,
        mime_type=mime_type,
        file_size=file_size,
        storage_path=f"{user.id}/{file_name}"
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)

    size_str = format_file_size(file_size)
    await message.answer(
        f"✅ <b>Fayl muvaffaqiyatli saqlandi!</b>\n\n"
        f"📄 #{record.id}: <b>{record.file_name}</b>\n"
        f"📦 Hajmi: {size_str}\n"
        f"📁 Turi: {record.file_type}\n\n"
        "Barcha fayllarni ko'rish: /files",
        parse_mode="HTML"
    )
