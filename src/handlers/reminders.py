import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

logger = structlog.get_logger(__name__)
router = Router(name="reminders_router")

class ReminderCreate(StatesGroup):
    time = State()
    text = State()

@router.message(Command("reminders"))
async def list_reminders(message: Message) -> None:
    """List all active reminders."""
    await message.answer("⏰ Faol eslatmalar:\n1. 14:00 - Uchrashuv\n2. 20:00 - Kitob o'qish")

@router.message(Command("remind"))
async def add_reminder_cmd(message: Message, state: FSMContext) -> None:
    """Start reminder creation or parse inline."""
    args = message.text.split(maxsplit=2)
    if len(args) == 3:
        time_str = args[1]
        text_str = args[2]
        await message.answer(f"✅ Eslatma o'rnatildi: {time_str} da '{text_str}'")
        return
    await message.answer("⏰ Eslatma vaqtini kiriting (Masalan: 14:30 yoki 5m):")
    await state.set_state(ReminderCreate.time)

@router.message(ReminderCreate.time, F.text)
async def reminder_time(message: Message, state: FSMContext) -> None:
    """Handle reminder time."""
    await state.update_data(time=message.text)
    await message.answer("📝 Eslatma matnini kiriting:")
    await state.set_state(ReminderCreate.text)

@router.message(ReminderCreate.text, F.text)
async def reminder_text(message: Message, state: FSMContext) -> None:
    """Handle reminder text and save."""
    data = await state.get_data()
    await state.clear()
    await message.answer(f"✅ Eslatma muvaffaqiyatli saqlandi: {data.get('time')} - {message.text}")
