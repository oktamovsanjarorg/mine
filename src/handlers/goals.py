import structlog
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.goal import GoalService
from src.core.utils.formatters import progress_bar

logger = structlog.get_logger(__name__)
router = Router(name="goals_router")


class GoalCreate(StatesGroup):
    title = State()
    target = State()


@router.message(Command("goals"))
@router.message(F.text == "🎯 Maqsadlar")
async def goals_menu(message: Message, session: AsyncSession, user: User) -> None:
    """List all goals for user."""
    service = GoalService(session)
    goals = await service.repo.get_all(user.id, limit=10)
    if not goals:
        await message.answer(
            "🎯 <b>Sizda hozircha faol maqsadlar mavjud emas!</b>\n\n"
            "Yangi maqsad belgilash uchun /addgoal buyrug'ini yuboring.",
            parse_mode="HTML"
        )
        return

    lines = ["🎯 <b>Sizning maqsadlaringiz:</b>\n"]
    for i, g in enumerate(goals, 1):
        target = float(g.target_value) if g.target_value else 1.0
        current = float(g.current_value) if g.current_value else 0.0
        pct = min(max(current / target, 0.0), 1.0) * 100
        pbar = progress_bar(current, target, length=10)
        unit_str = f" {g.unit}" if g.unit else ""
        lines.append(f"{i}. <b>#{g.id}: {g.title}</b>\n   [{pbar}] {pct:.0f}%\n   📊 {current:.1f}/{target:.1f}{unit_str}")

    lines.append("\n<i>Taraqqiyotni yangilash uchun: /progress <id> <qiymat></i>")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("addgoal"))
async def add_goal(message: Message, state: FSMContext) -> None:
    """Start adding a goal."""
    await message.answer("🎯 <b>Maqsad nomini kiriting:</b>\n(Masalan: <i>10 ta kitob o'qish</i> yoki <i>100 km yugurish</i>)", parse_mode="HTML")
    await state.set_state(GoalCreate.title)


@router.message(GoalCreate.title, F.text)
async def goal_title(message: Message, state: FSMContext) -> None:
    """Handle goal title."""
    await state.update_data(title=message.text.strip())
    await message.answer("📊 <b>Maqsadning yakuniy ko'rsatkichini kiriting:</b>\n(Masalan: <code>10</code>, <code>100</code>, <code>5000000</code>):", parse_mode="HTML")
    await state.set_state(GoalCreate.target)


@router.message(GoalCreate.target, F.text)
async def goal_target(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    """Handle goal target."""
    data = await state.get_data()
    await state.clear()

    try:
        target_val = float(message.text.strip().replace(" ", ""))
    except ValueError:
        target_val = 100.0

    service = GoalService(session)
    deadline = datetime.utcnow() + timedelta(days=90)
    goal = await service.create_goal(
        user_id=user.id,
        title=data["title"],
        target=target_val,
        unit="birlik",
        deadline=deadline
    )

    await message.answer(
        f"✅ <b>Yangi maqsad belgilandi!</b>\n\n"
        f"🎯 #{goal.id}: <b>{goal.title}</b>\n"
        f"🏁 Maqsad ko'rsatkichi: <b>{target_val}</b>\n\n"
        f"Barcha maqsadlarni ko'rish: /goals",
        parse_mode="HTML"
    )


@router.message(Command("progress"))
async def update_progress(message: Message, session: AsyncSession, user: User) -> None:
    """Update goal progress."""
    args = message.text.split()
    if len(args) < 3:
        await message.answer("ℹ️ Foydalanish: <code>/progress <goal_id> <qiymat></code>\nMasalan: <code>/progress 1 5</code>", parse_mode="HTML")
        return

    try:
        goal_id = int(args[1])
        value = float(args[2])
    except ValueError:
        await message.answer("❌ ID va qiymat raqam bo'lishi kerak.")
        return

    service = GoalService(session)
    try:
        goal = await service.update_progress(goal_id, value)
        milestones = await service.milestones_check(goal_id)
        m_str = f"\n\n{' '.join(milestones)}" if milestones else ""
        await message.answer(
            f"📈 <b>#{goal.id}: {goal.title}</b> taraqqiyoti yangilandi!\n"
            f"📊 Joriy holat: <b>{goal.current_value}/{goal.target_value}</b>{m_str}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error("Goal progress error", error=str(e))
        await message.answer(f"❌ Xatolik: Maqsad yangilanmadi ({e})")
