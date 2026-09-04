import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

logger = structlog.get_logger(__name__)
router = Router(name="habits_router")

class HabitCreate(StatesGroup):
    title = State()
    frequency = State()

@router.message(Command("habits"))
async def habits_menu(message: Message) -> None:
    """List habits."""
    await message.answer("🔄 Sizning odatlaringiz:\nHozircha odatlar yo'q. /addhabit orqali qo'shing.")

@router.message(Command("addhabit"))
async def add_habit(message: Message, state: FSMContext) -> None:
    """Start adding a habit."""
    await message.answer("Odat nomini kiriting:")
    await state.set_state(HabitCreate.title)

@router.message(HabitCreate.title, F.text)
async def add_habit_title(message: Message, state: FSMContext) -> None:
    """Set habit title."""
    await state.update_data(title=message.text)
    await message.answer("Chastotani kiriting (masalan: Har kuni, Haftada 3 marta):")
    await state.set_state(HabitCreate.frequency)
    
@router.message(HabitCreate.frequency, F.text)
async def add_habit_freq(message: Message, state: FSMContext) -> None:
    """Set habit frequency and save."""
    await state.clear()
    await message.answer("✅ Yangi odat muvaffaqiyatli saqlandi!")

@router.message(Command("checkin"))
async def checkin_habit(message: Message) -> None:
    """Check in a habit for today."""
    await message.answer("Qaysi odatni bajardingiz? ID yoki nomini kiriting:")
