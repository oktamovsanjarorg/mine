import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

logger = structlog.get_logger(__name__)
router = Router(name="goals_router")

class GoalCreate(StatesGroup):
    title = State()
    target = State()

@router.message(Command("goals"))
async def goals_menu(message: Message) -> None:
    """List all goals."""
    await message.answer("🎯 Sizning maqsadlaringiz:\n1. Ingliz tili [████░░░░░░] 40%")

@router.message(Command("addgoal"))
async def add_goal(message: Message, state: FSMContext) -> None:
    """Start adding a goal."""
    await message.answer("Maqsad nomini kiriting:")
    await state.set_state(GoalCreate.title)

@router.message(GoalCreate.title, F.text)
async def goal_title(message: Message, state: FSMContext) -> None:
    """Handle goal title."""
    await state.update_data(title=message.text)
    await message.answer("Maqsadning yakuniy ko'rsatkichini kiriting (masalan, 100):")
    await state.set_state(GoalCreate.target)

@router.message(GoalCreate.target, F.text)
async def goal_target(message: Message, state: FSMContext) -> None:
    """Handle goal target."""
    await state.clear()
    await message.answer("✅ Yangi maqsad muvaffaqiyatli qo'shildi!")

@router.message(Command("progress"))
async def update_progress(message: Message) -> None:
    """Update goal progress."""
    args = message.text.split()
    if len(args) < 3:
        await message.answer("Foydalanish: /progress <id> <qiymat>")
        return
    goal_id, value = args[1], args[2]
    await message.answer(f"📈 {goal_id}-maqsad taraqqiyoti {value} ga yangilandi.")
