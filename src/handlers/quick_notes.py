import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.quick_note import QuickNoteService

logger = structlog.get_logger(__name__)
router = Router(name="quick_notes_router")


def build_clips_markup(notes) -> InlineKeyboardMarkup:
    keyboard = []
    for n in notes:
        pin_icon = "📌" if n.is_pinned else "📍"
        row = [
            InlineKeyboardButton(text=f"{pin_icon} #{n.id} {n.content[:20]}", callback_data=f"clip_view:{n.id}"),
            InlineKeyboardButton(text="📌" if not n.is_pinned else "Unpin", callback_data=f"clip_pin:{n.id}"),
            InlineKeyboardButton(text="🗑", callback_data=f"clip_del:{n.id}"),
        ]
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.message(Command("clip"))
async def clip_text(message: Message, session: AsyncSession, user: User) -> None:
    """Clip text quickly or clip replied message."""
    content = ""
    args = message.text.split(maxsplit=1)
    if len(args) >= 2:
        content = args[1].strip()
    elif message.reply_to_message and message.reply_to_message.text:
        content = message.reply_to_message.text.strip()

    if not content:
        await message.answer("ℹ️ Foydalanish: <code>/clip &lt;matn&gt;</code> yoki xabarga reply qilib <code>/clip</code> yuboring.", parse_mode="HTML")
        return

    service = QuickNoteService(session)
    note = await service.create(user_id=user.id, content=content, is_pinned=False)
    await message.answer(
        f"📎 <b>Tezkor qoralama saqlandi!</b> (#{note.id})\n\n"
        f"📝 <i>{note.content[:200]}</i>\n\n"
        f"Barcha qoralamalar: /clips",
        parse_mode="HTML"
    )


@router.message(Command("clips", "quicknotes"))
@router.message(F.text == "📎 Qoralamalar")
async def list_clips(message: Message, session: AsyncSession, user: User) -> None:
    """List recent quick notes and clips."""
    service = QuickNoteService(session)
    notes = await service.get_recent(user.id, limit=10)
    if not notes:
        await message.answer("📎 <b>Hozircha hech qanday tezkor qoralama yo'q.</b>\n\nSaqlash uchun: <code>/clip Salom dunyo</code>", parse_mode="HTML")
        return

    lines = ["📎 <b>Sizning tezkor qoralamalaringiz (Clips):</b>\n"]
    for i, n in enumerate(notes, 1):
        pin = "📌 " if n.is_pinned else ""
        lines.append(f"{i}. {pin}<b>#{n.id}</b>: {n.content[:60]}")

    markup = build_clips_markup(notes)
    await message.answer("\n".join(lines), reply_markup=markup, parse_mode="HTML")


@router.message(Command("pin"))
async def pin_message(message: Message, session: AsyncSession, user: User) -> None:
    """Pin the replied message in Telegram and save to DB."""
    if not message.reply_to_message:
        await message.answer("📌 Qadab qo'yish uchun xabarga 'reply' qilib /pin yozing.")
        return

    # Try pinning in chat
    try:
        await message.reply_to_message.pin()
    except Exception as e:
        logger.warning("Telegram pin error", error=str(e))

    # Save to quick notes with is_pinned=True
    text_to_pin = message.reply_to_message.text or message.reply_to_message.caption or "[Media xabar]"
    service = QuickNoteService(session)
    note = await service.create(user_id=user.id, content=text_to_pin, is_pinned=True)
    await message.answer(f"📌 Xabar chatga va tizimga qadab qo'yildi! (#{note.id})")


@router.callback_query(F.data.startswith("clip_pin:"))
async def clip_pin_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    note_id = int(callback.data.split(":")[1])
    service = QuickNoteService(session)
    pinned = await service.toggle_pin(note_id)
    state_str = "📌 Qadaldi" if pinned else "Qadash bekor qilindi"
    await callback.answer(state_str)

    notes = await service.get_recent(user.id, limit=10)
    lines = ["📎 <b>Sizning tezkor qoralamalaringiz (Clips):</b>\n"]
    for i, n in enumerate(notes, 1):
        pin = "📌 " if n.is_pinned else ""
        lines.append(f"{i}. {pin}<b>#{n.id}</b>: {n.content[:60]}")
    markup = build_clips_markup(notes)
    try:
        await callback.message.edit_text("\n".join(lines), reply_markup=markup, parse_mode="HTML")
    except Exception:
        pass


@router.callback_query(F.data.startswith("clip_del:"))
async def clip_del_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    note_id = int(callback.data.split(":")[1])
    service = QuickNoteService(session)
    await service.delete(note_id)
    await callback.answer("🗑 Qoralama o'chirildi!")

    notes = await service.get_recent(user.id, limit=10)
    if not notes:
        await callback.message.edit_text("📎 <b>Barcha qoralamalar o'chirildi.</b>", parse_mode="HTML")
        return

    lines = ["📎 <b>Sizning tezkor qoralamalaringiz (Clips):</b>\n"]
    for i, n in enumerate(notes, 1):
        pin = "📌 " if n.is_pinned else ""
        lines.append(f"{i}. {pin}<b>#{n.id}</b>: {n.content[:60]}")
    markup = build_clips_markup(notes)
    try:
        await callback.message.edit_text("\n".join(lines), reply_markup=markup, parse_mode="HTML")
    except Exception:
        pass


@router.callback_query(F.data.startswith("clip_view:"))
async def clip_view_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    note_id = int(callback.data.split(":")[1])
    service = QuickNoteService(session)
    note = await service.repo.get_by_id(note_id)
    if note:
        await callback.answer(note.content[:200], show_alert=True)
    else:
        await callback.answer("Topilmadi", show_alert=True)

