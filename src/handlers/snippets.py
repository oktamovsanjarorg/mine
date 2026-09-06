import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.snippet import SnippetService

logger = structlog.get_logger(__name__)
router = Router(name="snippets_router")


class SnippetCreate(StatesGroup):
    title = State()
    language = State()
    code = State()


@router.message(Command("snippets"))
@router.message(F.text == "💻 Kodlar")
async def snippets_menu(message: Message, session: AsyncSession, user: User) -> None:
    """List code snippets."""
    service = SnippetService(session)
    snippets = await service.get_snippets(user.id, limit=15)
    if not snippets:
        await message.answer(
            "💻 <b>Sizda hozircha saqlangan kod parchalari yo'q!</b>\n\n"
            "Yangi kod parchasini saqlash uchun: /addsnippet",
            parse_mode="HTML"
        )
        return

    lines = [f"💻 <b>Sizning kod snippetlaringiz ({len(snippets)} ta):</b>\n"]
    for i, s in enumerate(snippets, 1):
        lang_str = f" <code>[{s.language}]</code>" if s.language else ""
        lines.append(f"{i}. <b>#{s.id}: {s.title}</b>{lang_str}")

    lines.append("\n<b>Buyruqlar:</b>")
    lines.append("• /snippet <id> - Kodni ochish va nusxalash")
    lines.append("• /addsnippet - Yangi kod saqlash")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("addsnippet"))
async def add_snippet(message: Message, state: FSMContext) -> None:
    """Start adding a snippet."""
    await message.answer("📝 <b>Snippet nomini kiriting</b> (masalan: <i>Docker run PostgreSQL</i> yoki <i>FastAPI CORS</i>):", parse_mode="HTML")
    await state.set_state(SnippetCreate.title)


@router.message(SnippetCreate.title, F.text)
async def snippet_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip())
    await message.answer("🌐 <b>Dasturlash tilini kiriting</b> (masalan: <code>python</code>, <code>bash</code>, <code>sql</code>, <code>json</code>):", parse_mode="HTML")
    await state.set_state(SnippetCreate.language)


@router.message(SnippetCreate.language, F.text)
async def snippet_lang(message: Message, state: FSMContext) -> None:
    await state.update_data(language=message.text.strip().lower())
    await message.answer("💻 <b>Kodni yuboring:</b>", parse_mode="HTML")
    await state.set_state(SnippetCreate.code)


@router.message(SnippetCreate.code, F.text)
async def snippet_code(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    data = await state.get_data()
    await state.clear()

    title = data["title"]
    language = data.get("language", "plaintext")
    code = message.text

    service = SnippetService(session)
    snippet = await service.repo.create(
        user_id=user.id,
        title=title,
        language=language,
        code=code
    )
    await session.commit()

    await message.answer(
        f"✅ <b>Kod parchasi saqlandi!</b>\n\n"
        f"💻 #{snippet.id}: <b>{snippet.title}</b> ({language})\n\n"
        f"<pre><code class='language-{language}'>{code}</code></pre>",
        parse_mode="HTML"
    )


@router.message(Command("snippet"))
async def get_snippet(message: Message, session: AsyncSession, user: User) -> None:
    """Get a snippet by ID."""
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("ℹ️ Foydalanish: <code>/snippet <id></code>", parse_mode="HTML")
        return

    snippet_id = int(args[1])
    service = SnippetService(session)
    snippet = await service.repo.get_by_id(snippet_id)
    if not snippet or snippet.user_id != user.id:
        await message.answer("❌ Snippet topilmadi.")
        return

    await service.increment_usage(snippet_id)
    await message.answer(
        f"💻 <b>#{snippet.id}: {snippet.title}</b> ({snippet.language})\n\n"
        f"<pre><code class='language-{snippet.language}'>{snippet.code}</code></pre>",
        parse_mode="HTML"
    )
