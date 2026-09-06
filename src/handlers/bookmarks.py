import structlog
import re
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.bookmark import BookmarkService

logger = structlog.get_logger(__name__)
router = Router(name="bookmarks_router")


def build_bookmark_markup(bookmarks) -> InlineKeyboardMarkup:
    keyboard = []
    for b in bookmarks:
        fav_star = "⭐" if b.is_favorite else "☆"
        row = [
            InlineKeyboardButton(text=f"{fav_star} #{b.id} {b.title[:20]}", url=b.url),
            InlineKeyboardButton(text="🗑", callback_data=f"bm_del:{b.id}"),
        ]
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.message(Command("bookmarks"))
@router.message(F.text == "🔖 Xatcho'plar")
async def bookmarks_menu(message: Message, session: AsyncSession, user: User) -> None:
    """List bookmarks."""
    service = BookmarkService(session)
    bookmarks = await service.get_bookmarks(user.id, limit=10)
    if not bookmarks:
        await message.answer(
            "🔖 <b>Sizda hozircha saqlangan xatcho'plar yo'q!</b>\n\n"
            "Havolani saqlash uchun: <code>/save https://example.com</code>",
            parse_mode="HTML"
        )
        return

    lines = ["🔖 <b>Sizning saqlangan xatcho'plaringiz:</b>\n"]
    for i, b in enumerate(bookmarks, 1):
        fav_icon = "⭐ " if b.is_favorite else ""
        lines.append(f"{i}. {fav_icon}<b><a href='{b.url}'>{b.title}</a></b>\n   🔗 <code>{b.url[:50]}</code>")

    markup = build_bookmark_markup(bookmarks)
    await message.answer("\n".join(lines), reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)


@router.message(Command("save"))
async def save_bookmark_cmd(message: Message, session: AsyncSession, user: User) -> None:
    """Save a URL bookmark."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("ℹ️ Foydalanish: <code>/save https://example.com</code>", parse_mode="HTML")
        return

    url = args[1].strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    service = BookmarkService(session)
    bm = await service.save_bookmark(user_id=user.id, url=url)
    await message.answer(
        f"✅ <b>Xatcho'p muvaffaqiyatli saqlandi!</b>\n\n"
        f"🔖 <b><a href='{bm.url}'>{bm.title}</a></b>\n"
        f"🔗 <code>{bm.url}</code>",
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@router.callback_query(F.data.startswith("bm_del:"))
async def delete_bookmark_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    bm_id = int(callback.data.split(":")[1])
    service = BookmarkService(session)
    bm = await service.repo.get_by_id(bm_id)
    if bm and bm.user_id == user.id:
        await service.repo.delete(bm_id)
        await session.commit()
        await callback.answer("🗑 Xatcho'p o'chirildi!")
        
        bookmarks = await service.get_bookmarks(user.id, limit=10)
        if not bookmarks:
            await callback.message.edit_text("🔖 <b>Barcha xatcho'plar o'chirildi.</b>", parse_mode="HTML")
            return
        lines = ["🔖 <b>Sizning saqlangan xatcho'plaringiz:</b>\n"]
        for i, b in enumerate(bookmarks, 1):
            fav_icon = "⭐ " if b.is_favorite else ""
            lines.append(f"{i}. {fav_icon}<b><a href='{b.url}'>{b.title}</a></b>\n   🔗 <code>{b.url[:50]}</code>")
        markup = build_bookmark_markup(bookmarks)
        try:
            await callback.message.edit_text("\n".join(lines), reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)
        except Exception:
            pass
