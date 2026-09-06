"""
Notes Handler - Full CRUD, Search, and Pinned Notes.
"""

import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.note import NoteService
from src.models.user import User

logger = structlog.get_logger(__name__)
router = Router(name="notes_router")


class NoteCreate(StatesGroup):
    title = State()
    content = State()


def build_notes_markup(notes) -> InlineKeyboardMarkup:
    keyboard = []
    for n in notes:
        pin_btn = "📌" if not n.is_pinned else "📍"
        row = [
            InlineKeyboardButton(text=f"{pin_btn} #{n.id}", callback_data=f"note_pin:{n.id}"),
            InlineKeyboardButton(text=f"👁 Ko'rish", callback_data=f"note_view:{n.id}"),
            InlineKeyboardButton(text=f"🗑", callback_data=f"note_del:{n.id}"),
        ]
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(text="➕ Yangi eslatma", callback_data="note_add_btn"),
        InlineKeyboardButton(text="🔄 Yangilash", callback_data="note_refresh_btn"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def format_notes_text(notes) -> str:
    if not notes:
        return (
            "📝 <b>Sizda hozircha hech qanday eslatma yo'q!</b>\n\n"
            "Yangi eslatma yozish uchun /addnote buyrug'ini bering yoki quyidagi tugmani bosing."
        )

    lines = ["📝 <b>Sizning eslatmalaringiz:</b>\n"]
    for i, n in enumerate(notes, 1):
        pin_badge = "📌 " if n.is_pinned else ""
        content_preview = (n.content[:40] + "...") if len(n.content) > 40 else n.content
        lines.append(f"{i}. {pin_badge}<b>#{n.id}: {n.title}</b>\n   <i>{content_preview}</i>")
    return "\n".join(lines)


@router.message(Command("notes"))
@router.message(F.text == "📝 Eslatmalar")
async def list_notes_handler(message: Message, session: AsyncSession, user: User) -> None:
    service = NoteService(session)
    notes = await service.get_notes(user.id, limit=10)
    text = format_notes_text(notes)
    markup = build_notes_markup(notes)
    await message.answer(text, reply_markup=markup, parse_mode="HTML")


@router.message(Command("addnote"))
async def add_note_start(message: Message, state: FSMContext) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        await state.update_data(title=args[1].strip())
        await message.answer("✍️ Eslatma matnini kiriting:")
        await state.set_state(NoteCreate.content)
        return

    await message.answer("📌 <b>Eslatma sarlavhasini kiriting:</b>", parse_mode="HTML")
    await state.set_state(NoteCreate.title)


@router.callback_query(F.data == "note_add_btn")
async def note_add_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("📌 <b>Eslatma sarlavhasini kiriting:</b>", parse_mode="HTML")
    await state.set_state(NoteCreate.title)
    await callback.answer()


@router.message(NoteCreate.title, F.text)
async def note_title_entered(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip())
    await message.answer("✍️ <b>Eslatma asosiy matnini kiriting:</b>", parse_mode="HTML")
    await state.set_state(NoteCreate.content)


@router.message(NoteCreate.content, F.text)
async def note_content_entered(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    data = await state.get_data()
    await state.clear()

    title = data.get("title", "Sarlavhasiz")
    content = message.text.strip()

    service = NoteService(session)
    note = await service.create_note(user_id=user.id, title=title, content=content)

    await message.answer(
        f"✅ <b>Eslatma saqlandi!</b>\n\n"
        f"📌 #{note.id}: <b>{note.title}</b>\n\n"
        f"{note.content}",
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("note_view:"))
async def view_note_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    note_id = int(callback.data.split(":")[1])
    service = NoteService(session)
    note = await service.repo.get_by_id(note_id)
    if note and note.user_id == user.id:
        text = (
            f"📝 <b>Eslatma #{note.id}</b>\n\n"
            f"📌 <b>{note.title}</b>\n\n"
            f"{note.content}\n\n"
            f"🕒 <i>Yaratilgan: {note.created_at.strftime('%Y-%m-%d %H:%M')}</i>"
        )
        await callback.message.answer(text, parse_mode="HTML")
    else:
        await callback.answer("Eslatma topilmadi!", show_alert=True)
    await callback.answer()


@router.callback_query(F.data.startswith("note_del:"))
async def delete_note_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    note_id = int(callback.data.split(":")[1])
    service = NoteService(session)
    note = await service.repo.get_by_id(note_id)
    if note and note.user_id == user.id:
        await service.delete_note(note_id)
        await callback.answer("🗑 Eslatma o'chirildi!")
        notes = await service.get_notes(user.id, limit=10)
        text = format_notes_text(notes)
        markup = build_notes_markup(notes)
        try:
            await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
        except Exception:
            pass
    else:
        await callback.answer("Eslatma topilmadi!", show_alert=True)


@router.callback_query(F.data == "note_refresh_btn")
async def refresh_note_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    service = NoteService(session)
    notes = await service.get_notes(user.id, limit=10)
    text = format_notes_text(notes)
    markup = build_notes_markup(notes)
    try:
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer("Yangilandi!")
