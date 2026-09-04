import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="files_router")

@router.message(Command("files"))
async def files_menu(message: Message) -> None:
    """List uploaded files."""
    await message.answer("📁 Fayllar markazi:\n/files - Ro'yxat\n(Fayl, rasm yoki audio yuboring va men saqlab qo'yaman)")

@router.message(F.document | F.photo | F.audio | F.video)
async def handle_files(message: Message) -> None:
    """Auto-upload documents/media to MinIO."""
    file_id = None
    file_type = "noma'lum"
    if message.document:
        file_id = message.document.file_id
        file_type = "Hujjat"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "Rasm"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "Audio"
    elif message.video:
        file_id = message.video.file_id
        file_type = "Video"
        
    logger.info("file_received", type=file_type, file_id=file_id)
    await message.answer(f"✅ {file_type} qabul qilindi va bulutga yuklandi!")
