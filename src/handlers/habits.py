"""
Habits Handler - Daily Habits, Streaks, Check-ins, and Reports.
"""

import structlog
from datetime import date
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.habit import HabitService
from src.models.user import User

logger = structlog.get_logger(__name__)
router = Router(name="habits_router")


class HabitCreate(StatesGroup):
    name = State()
    frequency = State()


def build_habit_markup(status_list) -> InlineKeyboardMarkup:
    keyboard = []
    for item in status_list:
        h = item["habit"]
        is_done = item["is_done"]
        btn_text = f"✅ #{h.id} {h.name}" if is_done else f"⭕️ #{h.id} {h.name}"
        keyboard.append([
            InlineKeyboardButton(text=btn_text, callback_data=f"habit_toggle:{h.id}")
        ])

    keyboard.append([
        InlineKeyboardButton(text="➕ Yangi odat", callback_data="habit_add_btn"),
        InlineKeyboardButton(text="🔄 Yangilash", callback_data="habit_refresh_btn"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def format_habits_text(status_list) -> str:
    if not status_list:
        return (
            "🌱 <b>Sizda hozircha hech qanday odat mavjud emas!</b>\n\n"
            "Yangi foydali odat boshlash uchun /addhabit buyrug'ini yuboring yoki quyidagi tugmani bosing."
        )

    lines = ["🌱 <b>Bugungi odatlaringiz holati:</b>\n"]
    for item in status_list:
        h = item["habit"]
        is_done = item["is_done"]
        status_icon = "✅ Bajarildi" if is_done else "⏳ Kutilmoqda"
        streak_icon = f"🔥 {h.current_streak} kun" if h.current_streak > 0 else "0 kun"
        lines.append(f"• <b>{h.name}</b> ({status_icon}) | {streak_icon}")

    lines.append("\n<i>Belgilash uchun odat tugmasini bosing:</i>")
    return "\n".join(lines)


@router.message(Command("habits"))
@router.message(F.text == "✅ Odatlar")
async def habits_menu(message: Message, session: AsyncSession, user: User) -> None:
    service = HabitService(session)
    status_list = await service.get_today_status(user.id)
    text = format_habits_text(status_list)
    markup = build_habit_markup(status_list)
    await message.answer(text, reply_markup=markup, parse_mode="HTML")


@router.message(Command("addhabit"))
async def add_habit_cmd(message: Message, state: FSMContext) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        await state.update_data(name=args[1].strip(), frequency="daily")
        await message.answer(f"🌱 Odat chastotasi: <b>Kunlik (Daily)</b>\nSaqlash uchun tasdiqlaysizmi?", parse_mode="HTML")
        # Proceed directly
        return

    await message.answer("📝 <b>Yangi odat nomini kiriting</b> (masalan: <i>Har kuni 30 daqiqa kitob o'qish</i>):", parse_mode="HTML")
    await state.set_state(HabitCreate.name)


@router.callback_query(F.data == "habit_add_btn")
async def habit_add_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("📝 <b>Yangi odat nomini kiriting:</b>", parse_mode="HTML")
    await state.set_state(HabitCreate.name)
    await callback.answer()


@router.message(HabitCreate.name, F.text)
async def habit_name_entered(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    name = message.text.strip()
    await state.clear()

    service = HabitService(session)
    habit = await service.create_habit(user_id=user.id, title=name, frequency="daily")
    
    await message.answer(
        f"🎉 <b>Yangi odat qo'shildi!</b>\n\n"
        f"🌱 Odat: <b>{habit.name}</b>\n"
        f"📅 Takrorlanishi: Kunlik\n"
        f"🔥 Joriy seriya: 0 kun\n\n"
        f"Odatlar ro'yxatini ko'rish: /habits",
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("habit_toggle:"))
async def toggle_habit_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    habit_id = int(callback.data.split(":")[1])
    service = HabitService(session)
    
    is_done = await service.repo.is_checked_in_today(habit_id)
    if is_done:
        await service.undo_check_in(habit_id)
        await callback.answer("❌ Odat bekor qilindi.")
    else:
        await service.check_in(habit_id)
        await callback.answer("🎉 Bugun uchun bajarildi deb belgilandi! Barakalla! 🔥")

    status_list = await service.get_today_status(user.id)
    text = format_habits_text(status_list)
    markup = build_habit_markup(status_list)
    try:
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        pass


@router.callback_query(F.data == "habit_refresh_btn")
async def refresh_habit_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    service = HabitService(session)
    status_list = await service.get_today_status(user.id)
    text = format_habits_text(status_list)
    markup = build_habit_markup(status_list)
    try:
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer("Yangilandi!")
