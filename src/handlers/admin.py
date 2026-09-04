import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="admin_router")

def is_admin(user_id: int) -> bool:
    # Basic stub
    return user_id in [123456789]

@router.message(Command("admin"))
async def admin_panel(message: Message) -> None:
    """Show admin panel."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu buyruq faqat administratorlar uchun.")
        return
    await message.answer("👑 Admin Panel:\n/healthcheck - Tizim holati\n/users - Foydalanuvchilar soni\n/broadcast - Xabar tarqatish")
