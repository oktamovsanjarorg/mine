import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.journal import JournalService

logger = structlog.get_logger(__name__)
router = Router(name="journal_router")


class JournalEntry(StatesGroup):
    content = State()
    mood = State()


@router.message(Command("journal"))
@router.message(F.text == "📓 Kundalik")
async def journal_menu(message: Message, session: AsyncSession, user: User) -> None:
    """List journal entries."""
    service = JournalService(session)
    entries = await service.repo.get_all(user.id, limit=10)
    if not entries:
        await message.answer(
            "📓 <b>Sizda hozircha kundalik yozuvlari yo'q!</b>\n\n"
            "Yangi yozuv qo'shish uchun /write buyrug'ini bosing.",
            parse_mode="HTML"
        )
        return

    lines = ["📓 <b>Sizning shaxsiy kundaligingiz:</b>\n"]
    for i, e in enumerate(entries, 1):
        mood_str = f" [{e.mood}]" if e.mood else ""
        date_str = e.created_at.strftime("%d.%m.%Y %H:%M") if e.created_at else ""
        preview = (e.content[:60] + "...") if len(e.content) > 60 else e.content
        lines.append(f"{i}. <b>#{e.id} {date_str}</b>{mood_str}\n   <i>{preview}</i>")

    lines.append("\nYangi yozuv qo'shish uchun: /write")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("write"))
async def journal_write(message: Message, state: FSMContext) -> None:
    """Start new journal entry."""
    await message.answer("✍️ <b>Bugungi kuningiz haqida nimalarni yozmoqchisiz?</b>\nMatnni yuboring:", parse_mode="HTML")
    await state.set_state(JournalEntry.content)


@router.message(JournalEntry.content, F.text)
async def journal_content(message: Message, state: FSMContext) -> None:
    """Save content and ask mood."""
    await state.update_data(content=message.text.strip())
    await message.answer("😊 <b>Hozirgi kayfiyatingizni tanlang:</b>\nMasalan: 🤩 A'lo, 😊 Yaxshi, 😐 O'rtacha, 😢 Xomush", parse_mode="HTML")
    await state.set_state(JournalEntry.mood)


@router.message(JournalEntry.mood, F.text)
async def journal_mood(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    """Save journal entry."""
    data = await state.get_data()
    await state.clear()

    content = data.get("content", "")
    mood = message.text.strip()

    service = JournalService(session)
    entry = await service.write_entry(user_id=user.id, content=content, mood=mood)

    await message.answer(
        f"✅ <b>Kundalik yozuv saqlandi!</b>\n\n"
        f"📓 #{entry.id} ({mood})\n"
        f"<i>\"{entry.content[:100]}\"</i>\n\n"
        f"Barcha yozuvlarni ko'rish: /journal",
        parse_mode="HTML"
    )
