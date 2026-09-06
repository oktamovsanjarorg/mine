import os
import platform
import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.config import settings
from src.models.user import User
from src.repositories.stats import StatsRepository

logger = structlog.get_logger(__name__)
router = Router(name="admin_router")

OWNER_ID = 7537966029


def is_admin(user_id: int) -> bool:
    """Check if user is the bot owner or in admin lists."""
    return user_id == OWNER_ID or user_id in settings.bot_admin_ids or user_id in settings.admin_ids


@router.message(Command("admin"))
async def admin_panel(message: Message, session: AsyncSession) -> None:
    """Show admin panel."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu buyruq faqat administratorlar uchun.")
        return

    stats_repo = StatsRepository(session)
    stats = await stats_repo.get_global_stats()
    
    user_count = await session.scalar(select(func.count(User.id)))

    text = (
        "👑 <b>Admin Boshqaruv Paneli</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{user_count or 0}</b>\n"
        f"📋 Jami vazifalar: <b>{stats.get('total_tasks', 0)}</b>\n"
        f"📝 Jami eslatmalar: <b>{stats.get('total_notes', 0)}</b>\n"
        f"🌱 Jami odatlar: <b>{stats.get('total_habits', 0)}</b>\n"
        f"💰 Tranzaksiyalar soni: <b>{stats.get('total_transactions', 0)}</b>\n\n"
        "<b>Admin buyruqlari:</b>\n"
        "• /healthcheck - Server va xizmatlar holati\n"
        "• /users - Foydalanuvchilar tafsiloti\n"
        "• /export - Barcha ma'lumotlarni yuklab olish"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("healthcheck"))
async def healthcheck_handler(message: Message, session: AsyncSession) -> None:
    """Check services health."""
    if not is_admin(message.from_user.id):
        return

    # Check DB
    db_status = "🟢 Faol"
    try:
        await session.execute(select(1))
    except Exception as e:
        db_status = f"🔴 Xatolik: {e}"

    # Check Redis
    redis_status = "🟢 Faol"
    try:
        from src.core.redis import get_redis
        redis = await get_redis()
        await redis.ping()
    except Exception as e:
        redis_status = f"🔴 Xatolik: {e}"

    load_avg = os.getloadavg() if hasattr(os, "getloadavg") else ("N/A", "N/A", "N/A")
    load_str = f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}" if isinstance(load_avg, tuple) else str(load_avg)

    msg = (
        "🏥 <b>Tizim Salomatligi Holati (Healthcheck):</b>\n\n"
        f"🗄 <b>PostgreSQL:</b> {db_status}\n"
        f"⚡ <b>Redis:</b> {redis_status}\n"
        f"💻 <b>Load Average (1, 5, 15 m):</b> {load_str}\n"
        f"🐧 <b>OS:</b> {platform.system()} {platform.release()}"
    )
    await message.answer(msg, parse_mode="HTML")


@router.message(Command("users"))
async def users_list_handler(message: Message, session: AsyncSession) -> None:
    """List registered users."""
    if not is_admin(message.from_user.id):
        return

    result = await session.execute(select(User).order_by(User.created_at.desc()).limit(15))
    users = result.scalars().all()
    if not users:
        await message.answer("👥 Foydalanuvchilar mavjud emas.")
        return

    lines = ["👥 <b>Oxirgi ro'yxatdan o'tgan foydalanuvchilar:</b>\n"]
    for u in users:
        uname = f"@{u.username}" if u.username else "username yo'q"
        status = "🟢" if u.is_active else "🔴"
        lines.append(f"{status} <b>{u.first_name}</b> (<code>{u.telegram_id}</code>) - {uname}")

    await message.answer("\n".join(lines), parse_mode="HTML")
