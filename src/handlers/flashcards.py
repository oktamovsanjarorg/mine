import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

logger = structlog.get_logger(__name__)
router = Router(name="flashcards_router")

class FlashcardCreate(StatesGroup):
    question = State()
    answer = State()

@router.message(Command("flashcards"))
async def flashcards_menu(message: Message) -> None:
    """Flashcards main menu."""
    await message.answer("🗂 Flashcardlar bo'limi:\n/study - O'rganishni boshlash\n/adddeck - Yangi to'plam qo'shish\n/addcard - Karta qo'shish")

@router.message(Command("study"))
async def study_flashcards(message: Message) -> None:
    """Start SM-2 study session."""
    await message.answer("🧠 O'rganish boshlandi!\nSavol: Python'da ro'yxat (list) qanday yaratiladi?\n(Javobni ko'rish uchun tugmani bosing)")

@router.message(Command("adddeck"))
async def add_deck(message: Message) -> None:
    """Add a new deck."""
    await message.answer("To'plam nomini kiriting:")

@router.message(Command("addcard"))
async def add_card(message: Message, state: FSMContext) -> None:
    """Start adding a flashcard."""
    await message.answer("Savolni kiriting:")
    await state.set_state(FlashcardCreate.question)

@router.message(FlashcardCreate.question, F.text)
async def card_question(message: Message, state: FSMContext) -> None:
    """Handle card question."""
    await state.update_data(question=message.text)
    await message.answer("Javobni kiriting:")
    await state.set_state(FlashcardCreate.answer)

@router.message(FlashcardCreate.answer, F.text)
async def card_answer(message: Message, state: FSMContext) -> None:
    """Handle card answer."""
    await state.clear()
    await message.answer("✅ Karta saqlandi!")
