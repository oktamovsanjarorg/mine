import structlog
from datetime import date
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.health import HealthService
from src.core.utils.formatters import progress_bar

logger = structlog.get_logger(__name__)
router = Router(name="health_router")


def build_health_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💧 +250 ml", callback_data="health_water:250"),
            InlineKeyboardButton(text="💧 +500 ml", callback_data="health_water:500"),
        ],
    ])


@router.message(Command("health"))
@router.message(F.text == "🏥 Salomatlik")
async def health_menu(message: Message, session: AsyncSession, user: User) -> None:
    """Health dashboard showing today's metrics."""
    service = HealthService(session)
    today = date.today()
    water = await service.repo.get_today_water(user.id, today)
    target_water = 2000
    pct = min(max(water / target_water, 0.0), 1.0) * 100
    pbar = progress_bar(water, target_water, length=10)

    sleep_log = await service.repo.get_latest(user.id, "sleep")
    weight_log = await service.repo.get_latest(user.id, "weight")
    exercise_logs = await service.repo.get_by_type_and_date(user.id, "exercise", today)
    exercise_total = sum(e.value for e in exercise_logs)

    sleep_str = f"{float(sleep_log.value):.1f} soat" if sleep_log else "kiritilmagan"
    weight_str = f"{float(weight_log.value):.1f} kg" if weight_log else "kiritilmagan"
    exercise_str = f"{int(exercise_total)} daqiqa" if exercise_total else "0 daqiqa"

    text = (
        "🏥 <b>Salomatlik va Jismoniy Holat Boshqaruvi</b>\n\n"
        f"💧 <b>Ichilgan suv:</b> <code>{water} / {target_water} ml</code>\n"
        f"[{pbar}] {pct:.0f}%\n\n"
        f"😴 <b>Oxirgi uyqu:</b> <code>{sleep_str}</code>\n"
        f"⚖️ <b>Joriy vazn:</b> <code>{weight_str}</code>\n"
        f"🏋️ <b>Bugungi mashg'ulot:</b> <code>{exercise_str}</code>\n\n"
        "<b>Tezkor buyruqlar:</b>\n"
        "• /water 250 - Suv kiritish (ml)\n"
        "• /sleep 8 - Uyqu soatini yozish\n"
        "• /weight 72 - Vaznni qayd etish (kg)\n"
        "• /exercise 30 - Mashg'ulot (daqiqa)"
    )
    await message.answer(text, reply_markup=build_health_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("health_water:"))
async def quick_water_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    amount = float(callback.data.split(":")[1])
    service = HealthService(session)
    await service.log_health(user_id=user.id, metric_type="water", value=amount)
    await callback.answer(f"✅ +{int(amount)} ml suv qo'shildi!")
    
    today = date.today()
    water = await service.repo.get_today_water(user.id, today)
    target_water = 2000
    pct = min(max(water / target_water, 0.0), 1.0) * 100
    pbar = progress_bar(water, target_water, length=10)
    
    sleep_log = await service.repo.get_latest(user.id, "sleep")
    weight_log = await service.repo.get_latest(user.id, "weight")
    exercise_logs = await service.repo.get_by_type_and_date(user.id, "exercise", today)
    exercise_total = sum(e.value for e in exercise_logs)
    sleep_str = f"{float(sleep_log.value):.1f} soat" if sleep_log else "kiritilmagan"
    weight_str = f"{float(weight_log.value):.1f} kg" if weight_log else "kiritilmagan"
    exercise_str = f"{int(exercise_total)} daqiqa" if exercise_total else "0 daqiqa"

    text = (
        "🏥 <b>Salomatlik va Jismoniy Holat Boshqaruvi</b>\n\n"
        f"💧 <b>Ichilgan suv:</b> <code>{water} / {target_water} ml</code>\n"
        f"[{pbar}] {pct:.0f}%\n\n"
        f"😴 <b>Oxirgi uyqu:</b> <code>{sleep_str}</code>\n"
        f"⚖️ <b>Joriy vazn:</b> <code>{weight_str}</code>\n"
        f"🏋️ <b>Bugungi mashg'ulot:</b> <code>{exercise_str}</code>\n\n"
        "<b>Tezkor buyruqlar:</b>\n"
        "• /water 250 - Suv kiritish (ml)\n"
        "• /sleep 8 - Uyqu soatini yozish\n"
        "• /weight 72 - Vaznni qayd etish (kg)\n"
        "• /exercise 30 - Mashg'ulot (daqiqa)"
    )
    try:
        await callback.message.edit_text(text, reply_markup=build_health_markup(), parse_mode="HTML")
    except Exception:
        pass


@router.message(Command("water"))
async def log_water_cmd(message: Message, session: AsyncSession, user: User) -> None:
    args = message.text.split()
    if len(args) < 2:
        await message.answer("ℹ️ Masalan: <code>/water 250</code> yoki <code>/water 500</code>", parse_mode="HTML")
        return
    try:
        val = float(args[1])
    except ValueError:
        await message.answer("❌ Miqdor raqamda bo'lishi kerak.")
        return

    service = HealthService(session)
    await service.log_health(user_id=user.id, metric_type="water", value=val)
    today = date.today()
    total = await service.repo.get_today_water(user.id, today)
    await message.answer(f"💧 <b>+{int(val)} ml</b> suv saqlandi! Bugungi jami: <b>{total} ml</b>", parse_mode="HTML")


@router.message(Command("sleep"))
async def log_sleep_cmd(message: Message, session: AsyncSession, user: User) -> None:
    args = message.text.split()
    if len(args) < 2:
        await message.answer("ℹ️ Masalan: <code>/sleep 8</code> yoki <code>/sleep 7.5</code>", parse_mode="HTML")
        return
    try:
        val = float(args[1])
    except ValueError:
        await message.answer("❌ Uyqu soati raqamda bo'lishi kerak.")
        return

    service = HealthService(session)
    await service.log_health(user_id=user.id, metric_type="sleep", value=val)
    await message.answer(f"😴 <b>{val} soat</b> uyqu muvaffaqiyatli saqlandi!", parse_mode="HTML")


@router.message(Command("weight"))
async def log_weight_cmd(message: Message, session: AsyncSession, user: User) -> None:
    args = message.text.split()
    if len(args) < 2:
        await message.answer("ℹ️ Masalan: <code>/weight 72.5</code>", parse_mode="HTML")
        return
    try:
        val = float(args[1])
    except ValueError:
        await message.answer("❌ Vazn raqamda bo'lishi kerak.")
        return

    service = HealthService(session)
    await service.log_health(user_id=user.id, metric_type="weight", value=val)
    await message.answer(f"⚖️ Vazn: <b>{val} kg</b> qayd etildi!", parse_mode="HTML")


@router.message(Command("exercise"))
async def log_exercise_cmd(message: Message, session: AsyncSession, user: User) -> None:
    args = message.text.split()
    if len(args) < 2:
        await message.answer("ℹ️ Masalan: <code>/exercise 45</code> (daqiqa)", parse_mode="HTML")
        return
    try:
        val = float(args[1])
    except ValueError:
        await message.answer("❌ Vaqt raqamda bo'lishi kerak.")
        return

    service = HealthService(session)
    await service.log_health(user_id=user.id, metric_type="exercise", value=val)
    await message.answer(f"🏋️ <b>{int(val)} daqiqa</b> mashg'ulot saqlandi! Barakalla! 💪", parse_mode="HTML")
