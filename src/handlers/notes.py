import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

logger = structlog.get_logger(__name__)
router = Router(name="notes_router")

class NoteCreate(StatesGroup):
    content = State()
    tags = State()

@router.message(Command("notes"))
async def list_notes_handler(message: Message) -> None:
    """List all notes."""
    await message.answer("📓 Sizning eslatmalaringiz:")

@router.message(Command("addnote"))
async def add_note_start(message: Message, state: FSMContext) -> None:
    """Start FSM for adding a note."""
    await message.answer("✍️ Eslatma matnini kiriting:")
    await state.set_state(NoteCreate.content)

@router.message(NoteCreate.content, F.text)
async def add_note_content(message: Message, state: FSMContext) -> None:
    """Handle note content."""
    await state.update_data(content=message.text)
    await message.answer("🏷️ Teglarni vergul bilan ajratib kiriting (yoki /skip):")
    await state.set_state(NoteCreate.tags)

@router.message(NoteCreate.tags, F.text)
async def add_note_tags(message: Message, state: FSMContext) -> None:
    """Handle note tags and save."""
    data = await state.get_data()
    tags = message.text
    await state.clear()
    await message.answer("✅ Eslatma muvaffaqiyatli saqlandi!")

@router.message(Command("searchnotes"))
async def search_notes_handler(message: Message) -> None:
    """Search within notes."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("🔍 Qidirish uchun so'z kiriting: /searchnotes <so'z>")
        return
    query = args[1]
    await message.answer(f"🔍 '{query}' bo'yicha qidiruv natijalari:")
