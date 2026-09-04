import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

logger = structlog.get_logger(__name__)
router = Router(name="journal_router")

class JournalEntry(StatesGroup):
    mood = State()
    content = State()

@router.message(Command("journal"))
async def journal_menu(message: Message) -> None:
    """List journal entries."""
    await message.answer("📖 Kundalik yozuvlaringiz:\nYangi yozuv qo'shish uchun /write bosing.")

@router.message(Command("write"))
async def journal_write(message: Message, state: FSMContext) -> None:
    """Start new journal entry."""
    await message.answer("Bugungi kun haqida nimalar demoqchisiz? Matnni yozing:")
    await state.set_state(JournalEntry.content)

@router.message(JournalEntry.content, F.text)
async def journal_content(message: Message, state: FSMContext) -> None:
    """Save content and ask mood."""
    await state.update_data(content=message.text)
    await message.answer("Kayfiyatingizni tanlang: 😢 😐 😊 😄 🤩")
    await state.set_state(JournalEntry.mood)

@router.message(JournalEntry.mood, F.text)
async def journal_mood(message: Message, state: FSMContext) -> None:
    """Save journal entry."""
    await state.clear()
    await message.answer("✅ Kundalik yozuv saqlandi!")

@router.message(Command("mood"))
async def log_mood(message: Message) -> None:
    """Quick mood log."""
    await message.answer("Hozirgi kayfiyatingiz qanday? Emoji yuboring.")
