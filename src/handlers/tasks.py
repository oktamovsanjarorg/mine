import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

logger = structlog.get_logger(__name__)
router = Router(name="tasks_router")

class TaskCreate(StatesGroup):
    title = State()
    description = State()
    priority = State()
    due_date = State()
    category = State()

@router.message(Command("tasks"))
async def list_tasks_handler(message: Message) -> None:
    """List all tasks with pagination."""
    await message.answer("📋 Sizning vazifalaringiz ro'yxati:")

@router.message(Command("addtask"))
async def add_task_start(message: Message, state: FSMContext) -> None:
    """Start FSM for adding a new task."""
    await message.answer("📝 Yangi vazifa nomini kiriting:")
    await state.set_state(TaskCreate.title)

@router.message(TaskCreate.title, F.text)
async def add_task_title(message: Message, state: FSMContext) -> None:
    """Handle task title."""
    await state.update_data(title=message.text)
    await message.answer("📄 Vazifa tafsilotini kiriting (yoki /skip):")
    await state.set_state(TaskCreate.description)

@router.message(TaskCreate.description, F.text)
async def add_task_desc(message: Message, state: FSMContext) -> None:
    """Handle task description."""
    await state.update_data(description=message.text)
    await message.answer("⚡ Prioritetni tanlang (Past/O'rta/Yuqori):")
    await state.set_state(TaskCreate.priority)

@router.message(TaskCreate.priority, F.text)
async def add_task_priority(message: Message, state: FSMContext) -> None:
    """Handle task priority."""
    await state.update_data(priority=message.text)
    await message.answer("📅 Muddatni kiriting (Masalan: YYYY-MM-DD):")
    await state.set_state(TaskCreate.due_date)

@router.message(TaskCreate.due_date, F.text)
async def add_task_due_date(message: Message, state: FSMContext) -> None:
    """Handle task due date."""
    await state.update_data(due_date=message.text)
    await message.answer("📁 Kategoriyani kiriting:")
    await state.set_state(TaskCreate.category)

@router.message(TaskCreate.category, F.text)
async def add_task_category(message: Message, state: FSMContext) -> None:
    """Handle task category and save task."""
    data = await state.get_data()
    category = message.text
    # Save to DB logic here
    await state.clear()
    await message.answer(f"✅ Vazifa saqlandi!\nNomi: {data.get('title')}\nKategoriya: {category}")

@router.message(Command("donetask"))
async def done_task_handler(message: Message) -> None:
    """Mark a task as done."""
    await message.answer("Qaysi vazifani bajarildi deb belgilaymiz? ID kiriting:")
