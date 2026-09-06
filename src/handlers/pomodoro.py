import datetime
import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.pomodoro import PomodoroType
from src.services.pomodoro import PomodoroService

logger = structlog.get_logger(__name__)
router = Router(name="pomodoro_router")


def build_pomodoro_menu(active_session=None) -> InlineKeyboardMarkup:
    if active_session:
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Muvaffaqiyatli tugatish", callback_data=f"pomo_done:{active_session.id}"),
                InlineKeyboardButton(text="⏹ To'xtatish", callback_data=f"pomo_stop:{active_session.id}"),
            ],
            [InlineKeyboardButton(text="🔄 Yangilash", callback_data="pomo_refresh")]
        ])

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍅 25m Fokus", callback_data="pomo_start:25:work"),
            InlineKeyboardButton(text="⚡️ 50m Chuqur fokus", callback_data="pomo_start:50:work"),
        ],
        [
            InlineKeyboardButton(text="☕️ 5m Tanaffus", callback_data="pomo_start:5:short_break"),
            InlineKeyboardButton(text="🌴 15m Katta tanaffus", callback_data="pomo_start:15:long_break"),
        ],
        [
            InlineKeyboardButton(text="📊 Mening statistikam", callback_data="pomo_stats")
        ]
    ])


@router.message(Command("pomodoro", "pomo"))
@router.message(F.text == "🍅 Pomodoro")
async def pomodoro_menu(message: Message, session: AsyncSession, user: User) -> None:
    """Pomodoro timer dashboard."""
    service = PomodoroService(session)
    active = await service.get_active_session(user.id)

    if active:
        started = active.started_at
        if started.tzinfo is None:
            started = started.replace(tzinfo=datetime.timezone.utc)
        elapsed = int((datetime.datetime.now(datetime.timezone.utc) - started).total_seconds() / 60)
        remaining = max(0, active.duration_minutes - elapsed)
        text = (
            f"🍅 <b>Pomodoro taymeri ishlamoqda!</b>\n\n"
            f"🎯 <b>Rejim:</b> {active.type.value if hasattr(active.type, 'value') else active.type}\n"
            f"⏱ <b>Davomiyligi:</b> {active.duration_minutes} daqiqa\n"
            f"⏳ <b>O'tgan vaqt:</b> {elapsed} daqiqa\n"
            f"⏳ <b>Qolgan vaqt:</b> {remaining} daqiqa\n\n"
            f"Fokusni saqlang va chalg'imang! 🚀"
        )
        markup = build_pomodoro_menu(active)
    else:
        text = (
            "🍅 <b>Pomodoro Taymeri</b>\n\n"
            "Pomodoro texnikasi samaradorlikni oshirish va diqqatni jamlash uchun 25 daqiqa intensiv ishlash "
            "va 5 daqiqa tanaffus qilish tamoyiliga asoslangan.\n\n"
            "Quyidagi rejimlardan birini tanlang:"
        )
        markup = build_pomodoro_menu()

    await message.answer(text, reply_markup=markup, parse_mode="HTML")


@router.callback_query(F.data == "pomo_refresh")
async def pomo_refresh_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    service = PomodoroService(session)
    active = await service.get_active_session(user.id)
    if not active:
        await callback.message.edit_text(
            "🍅 <b>Faol Pomodoro sessiyasi yo'q.</b> Boshlash uchun rejimni tanlang:",
            reply_markup=build_pomodoro_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    started = active.started_at
    if started.tzinfo is None:
        started = started.replace(tzinfo=datetime.timezone.utc)
    elapsed = int((datetime.datetime.now(datetime.timezone.utc) - started).total_seconds() / 60)
    remaining = max(0, active.duration_minutes - elapsed)
    text = (
        f"🍅 <b>Pomodoro taymeri ishlamoqda!</b>\n\n"
        f"🎯 <b>Rejim:</b> {active.type.value if hasattr(active.type, 'value') else active.type}\n"
        f"⏱ <b>Davomiyligi:</b> {active.duration_minutes} daqiqa\n"
        f"⏳ <b>O'tgan vaqt:</b> {elapsed} daqiqa\n"
        f"⏳ <b>Qolgan vaqt:</b> {remaining} daqiqa\n\n"
        f"Fokusni saqlang va chalg'imang! 🚀"
    )
    try:
        await callback.message.edit_text(text, reply_markup=build_pomodoro_menu(active), parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("pomo_start:"))
async def pomo_start_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    parts = callback.data.split(":")
    duration = int(parts[1])
    type_str = parts[2]
    pomo_type = PomodoroType.WORK if "work" in type_str else PomodoroType.SHORT_BREAK

    service = PomodoroService(session)
    active = await service.start_session(user_id=user.id, duration_minutes=duration, session_type=pomo_type)
    text = (
        f"🚀 <b>Yangi Pomodoro sessiyasi boshlandi!</b>\n\n"
        f"⏱ <b>Davomiyligi:</b> {duration} daqiqa\n"
        f"🎯 Fokus qiling, xabar va chalg'ituvchi narsalardan uzoqlashing!"
    )
    await callback.message.edit_text(text, reply_markup=build_pomodoro_menu(active), parse_mode="HTML")
    await callback.answer("Taymer ishga tushdi! 🍅")


@router.callback_query(F.data.startswith("pomo_done:"))
async def pomo_done_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    session_id = int(callback.data.split(":")[1])
    service = PomodoroService(session)
    await service.end_session(session_id, status="completed")
    stats = await service.stats(user.id)

    text = (
        "🎉 <b>Ajoyib! Pomodoro sessiyasi muvaffaqiyatli yakunlandi!</b>\n\n"
        f"📊 Jami yakunlangan sessiyalar: <b>{stats['completed_sessions']}</b> ta\n"
        f"⏱ Jami fokus vaqti: <b>{stats['total_minutes']}</b> daqiqa\n\n"
        "Endi ozgina dam oling yoki yangi sessiya boshlang:"
    )
    await callback.message.edit_text(text, reply_markup=build_pomodoro_menu(), parse_mode="HTML")
    await callback.answer("Tabriklaymiz! 🎉")


@router.callback_query(F.data.startswith("pomo_stop:"))
async def pomo_stop_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    session_id = int(callback.data.split(":")[1])
    service = PomodoroService(session)
    await service.end_session(session_id, status="interrupted")
    text = (
        "⏹ <b>Pomodoro to'xtatildi.</b>\n\n"
        "Hechqisi yo'q, keyingi safar albatta oxirigacha yetkazasiz! Qayta boshlash uchun:"
    )
    await callback.message.edit_text(text, reply_markup=build_pomodoro_menu(), parse_mode="HTML")
    await callback.answer("Sessiya to'xtatildi.")


@router.callback_query(F.data == "pomo_stats")
@router.message(Command("pomostats"))
async def pomo_stats_handler(event: Message | CallbackQuery, session: AsyncSession, user: User) -> None:
    message = event if isinstance(event, Message) else event.message
    if isinstance(event, CallbackQuery):
        await event.answer()

    service = PomodoroService(session)
    stats = await service.stats(user.id)
    text = (
        "📊 <b>Pomodoro Statistikangiz:</b>\n\n"
        f"🍅 Yakunlangan sessiyalar: <b>{stats['completed_sessions']}</b> ta\n"
        f"⏱ Jami fokus qilingan vaqt: <b>{stats['total_minutes']}</b> daqiqa ({stats['total_minutes'] // 60} soat {stats['total_minutes'] % 60} daqiqa)\n\n"
        "Har kuni o'z natijangizni yangilang! 💪"
    )
    await message.answer(text, parse_mode="HTML")

