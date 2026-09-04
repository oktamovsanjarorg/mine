import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

logger = structlog.get_logger(__name__)
router = Router(name="snippets_router")

class SnippetCreate(StatesGroup):
    code = State()
    language = State()

@router.message(Command("snippets"))
async def snippets_menu(message: Message) -> None:
    """List code snippets."""
    await message.answer("✂️ Kod snippetlari ro'yxati:\nHozircha bo'sh.")

@router.message(Command("addsnippet"))
async def add_snippet(message: Message, state: FSMContext) -> None:
    """Start adding a snippet."""
    await message.answer("Kod matnini yuboring:")
    await state.set_state(SnippetCreate.code)

@router.message(SnippetCreate.code, F.text)
async def snippet_code(message: Message, state: FSMContext) -> None:
    """Handle snippet code."""
    await state.update_data(code=message.text)
    await message.answer("Dasturlash tilini kiriting (python, js, c++ va h.k):")
    await state.set_state(SnippetCreate.language)

@router.message(SnippetCreate.language, F.text)
async def snippet_lang(message: Message, state: FSMContext) -> None:
    """Handle snippet language."""
    data = await state.get_data()
    code = data.get('code')
    lang = message.text
    await state.clear()
    await message.answer(f"✅ Snippet saqlandi!\n\n<pre><code class='language-{lang}'>{code}</code></pre>", parse_mode="HTML")

@router.message(Command("snippet"))
async def get_snippet(message: Message) -> None:
    """Get a snippet by ID."""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Foydalanish: /snippet <id>")
        return
    await message.answer("Mana sizning snippetingiz (hozircha topilmadi).")
