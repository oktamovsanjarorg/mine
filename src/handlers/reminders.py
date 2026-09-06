"""
Reminders Handler - Relative time parsing, listing, and scheduling.
"""

import re
import structlog
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.reminder import ReminderService
from src.models.user import User
from src.core.utils.datetime_utils import parse_datetime, format_relative

logger = structlog.get_logger(__name__)
router = Router(name="reminders_router")


class ReminderCreate(StatesGroup):
    time = State()
    title = State()


def build_reminders_markup(reminders) -> InlineKeyboardMarkup:
    keyboard = []
    for r in reminders:
        keyboard.append([
            InlineKeyboardButton(text=f"🗑 #{r.id} O'chirish", callback_data=f"remind_del:{r.id}")
        ])
    keyboard.append([
        InlineKeyboardButton(text="➕ Yangi eslatma", callback_data="remind_add_btn"),
        InlineKeyboardButton(text="🔄 Yangilash", callback_data="remind_refresh_btn"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def format_reminders_text(reminders) -> str:
    if not reminders:
        return (
            "⏰ <b>Sizda hozircha faol eslatmalar yo'q!</b>\n\n"
            "Yangi eslatma o'rnatish uchun masalan:\n"
            "• <code>/remind 15m Choy ichish</code>\n"
            "• <code>/remind 2h Uchrashuv</code>\n"
            "• <code>/remind ertaga 09:00 Dars</code>"
        )

    lines = ["⏰ <b>Sizning faol eslatmalaringiz:</b>\n"]
    for i, r in enumerate(reminders, 1):
        rel_str = format_relative(r.remind_at) if r.remind_at else ""
        time_str = r.remind_at.strftime("%d.%m %H:%M") if r.remind_at else ""
        lines.append(f"{i}. <b>#{r.id}: {r.title}</b>\n   🕒 {time_str} <i>({rel_str})</i>")

    return "\n".join(lines)


@router.message(Command("reminders"))
async def list_reminders_handler(message: Message, session: AsyncSession, user: User) -> None:
    service = ReminderService(session)
    reminders = await service.repo.get_active(user.id, limit=10)
    text = format_reminders_text(reminders)
    markup = build_reminders_markup(reminders)
    await message.answer(text, reply_markup=markup, parse_mode="HTML")


@router.message(Command("remind"))
async def add_reminder_quick(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    text = message.text.split(maxsplit=1)
    if len(text) > 1:
        payload = text[1].strip()
        # 1. Try matching "ertaga HH:MM <title>"
        ertaga_m = re.match(r'^(ertaga\s+\d{1,2}:\d{2})\s+(.+)$', payload, re.IGNORECASE)
        if ertaga_m:
            time_part = ertaga_m.group(1)
            title = ertaga_m.group(2).strip()
            dt = parse_datetime(time_part)
            if dt:
                service = ReminderService(session)
                rem = await service.create_reminder(user_id=user.id, title=title, remind_at=dt)
                await message.answer(
                    f"⏰ <b>Eslatma muvaffaqiyatli saqlandi!</b>\n\n"
                    f"📌 <b>{rem.title}</b>\n"
                    f"🕒 Vaqti: <b>{rem.remind_at.strftime('%Y-%m-%d %H:%M')}</b>\n"
                    f"Vaqt kelganda sizga xabar beraman! 🤖",
                    parse_mode="HTML"
                )
                return

        # 2. Try single-token time like "15m <title>" or "2h <title>"
        parts = payload.split(maxsplit=1)
        if len(parts) == 2:
            time_text, title = parts[0], parts[1].strip()
            dt = parse_datetime(time_text)
            if dt:
                service = ReminderService(session)
                rem = await service.create_reminder(user_id=user.id, title=title, remind_at=dt)
                await message.answer(
                    f"⏰ <b>Eslatma muvaffaqiyatli saqlandi!</b>\n\n"
                    f"📌 <b>{rem.title}</b>\n"
                    f"🕒 Vaqti: <b>{rem.remind_at.strftime('%Y-%m-%d %H:%M')}</b>\n"
                    f"Vaqt kelganda sizga xabar beraman! 🤖",
                    parse_mode="HTML"
                )
                return

    await state.set_state(ReminderCreate.time)
    await message.answer(
        "⏰ <b>Eslatma qachonga belgilansin?</b>\n\n"
        "Masalan: <code>15m</code> (15 daqiqadan so'ng), <code>2h</code> (2 soatdan so'ng), <code>ertaga 10:00</code>:",
        parse_mode="HTML"
    )


@router.callback_query(F.data == "remind_add_btn")
async def remind_add_btn_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(
        "⏰ <b>Eslatma vaqtini kiriting</b> (masalan: <code>30m</code>, <code>2h</code>, <code>ertaga 09:00</code>):",
        parse_mode="HTML"
    )
    await state.set_state(ReminderCreate.time)
    await callback.answer()


@router.message(ReminderCreate.time, F.text)
async def reminder_time_entered(message: Message, state: FSMContext) -> None:
    dt = parse_datetime(message.text.strip())
    if not dt:
        await message.answer(
            "❌ Vaqt formati tushunarsiz bo'ldi. Iltimos, qaytadan kiriting:\n"
            "Masalan: <code>15m</code>, <code>2h</code>, <code>ertaga 18:00</code>:",
            parse_mode="HTML"
        )
        return

    await state.update_data(remind_at=dt.isoformat())
    await message.answer("✍️ <b>Nimani eslatishim kerak? (Eslatma matni):</b>", parse_mode="HTML")
    await state.set_state(ReminderCreate.title)


@router.message(ReminderCreate.title, F.text)
async def reminder_title_entered(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    data = await state.get_data()
    await state.clear()

    dt = datetime.fromisoformat(data["remind_at"])
    title = message.text.strip()

    service = ReminderService(session)
    rem = await service.create_reminder(user_id=user.id, title=title, remind_at=dt)

    await message.answer(
        f"✅ <b>Eslatma o'rnatildi!</b>\n\n"
        f"📌 #{rem.id}: <b>{rem.title}</b>\n"
        f"🕒 Belgilangan vaqt: <b>{rem.remind_at.strftime('%Y-%m-%d %H:%M')}</b>",
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("remind_del:"))
async def remind_del_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    rem_id = int(callback.data.split(":")[1])
    service = ReminderService(session)
    rem = await service.repo.get_by_id(rem_id)
    if rem and rem.user_id == user.id:
        await service.deactivate(rem_id)
        await callback.answer("🗑 Eslatma bekor qilindi!")
        reminders = await service.repo.get_active(user.id, limit=10)
        text = format_reminders_text(reminders)
        markup = build_reminders_markup(reminders)
        try:
            await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
        except Exception:
            pass
    else:
        await callback.answer("Eslatma topilmadi!", show_alert=True)


@router.callback_query(F.data == "remind_refresh_btn")
async def remind_refresh_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    service = ReminderService(session)
    reminders = await service.repo.get_active(user.id, limit=10)
    text = format_reminders_text(reminders)
    markup = build_reminders_markup(reminders)
    try:
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer("Yangilandi!")
