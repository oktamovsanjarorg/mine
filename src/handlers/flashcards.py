import structlog
from datetime import datetime, date
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User
from src.models.flashcard import FlashcardDeck, Flashcard
from src.services.flashcard import FlashcardService

logger = structlog.get_logger(__name__)
router = Router(name="flashcards_router")


class FlashcardCreate(StatesGroup):
    question = State()
    answer = State()


@router.message(Command("flashcards"))
@router.message(F.text == "📚 Flashcard")
async def flashcards_menu(message: Message, session: AsyncSession, user: User) -> None:
    """Flashcards main menu."""
    service = FlashcardService(session)
    decks = await service.repo.get_decks(user.id)
    if not decks:
        await message.answer(
            "🗂 <b>Flashcardlar (Interaktiv O'rganish)</b>\n\n"
            "Sizda hozircha hech qanday to'plam (deck) yo'q.\n\n"
            "Yangi to'plam ochish uchun: <code>/adddeck Ingliz tili</code>",
            parse_mode="HTML"
        )
        return

    lines = ["🗂 <b>Sizning to'plamlaringiz (Decks):</b>\n"]
    for i, d in enumerate(decks, 1):
        cards = await service.repo.get_cards(d.id, limit=100)
        lines.append(f"{i}. 📁 <b>#{d.id}: {d.name}</b> ({len(cards)} ta karta)")

    lines.append("\n<b>Buyruqlar:</b>")
    lines.append("• /study - SM-2 algoritmi bilan takrorlash")
    lines.append("• /adddeck &lt;nom&gt; - Yangi to'plam ochish")
    lines.append("• /addcard - Karta qo'shish")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 O'rganishni boshlash", callback_data="fc_start_study")],
    ])
    await message.answer("\n".join(lines), reply_markup=kb, parse_mode="HTML")


@router.message(Command("adddeck"))
async def add_deck(message: Message, session: AsyncSession, user: User) -> None:
    """Add a new deck."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("ℹ️ To'plam nomini yozing:\nMasalan: <code>/adddeck Ingliz tili so'zlari</code>", parse_mode="HTML")
        return

    deck_name = args[1].strip()
    service = FlashcardService(session)
    deck = await service.create_deck(user_id=user.id, name=deck_name)
    await message.answer(
        f"✅ <b>Yangi to'plam yaratildi!</b>\n\n"
        f"📁 #{deck.id}: <b>{deck.name}</b>\n\n"
        f"Karta qo'shish uchun: <code>/addcard</code> yoki <code>/addcard Savol | Javob</code>",
        parse_mode="HTML"
    )


@router.message(Command("addcard"))
async def add_card(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    """Add a card quickly or start FSM."""
    args = message.text.split(maxsplit=1)
    if len(args) > 1 and "|" in args[1]:
        parts = args[1].split("|", 1)
        front = parts[0].strip()
        back = parts[1].strip()
        service = FlashcardService(session)
        decks = await service.repo.get_decks(user.id)
        if not decks:
            deck = await service.create_deck(user.id, "Umumiy to'plam")
        else:
            deck = decks[0]
        
        card = await service.add_card(deck.id, front, back)
        await message.answer(f"✅ <b>Karta saqlandi!</b> (#{card.id})\n❓ {front}\n💡 {back}", parse_mode="HTML")
        return

    await message.answer("❓ <b>Karta savolini (front) kiriting:</b>", parse_mode="HTML")
    await state.set_state(FlashcardCreate.question)


@router.message(FlashcardCreate.question, F.text)
async def card_question(message: Message, state: FSMContext) -> None:
    """Handle card question."""
    await state.update_data(question=message.text.strip())
    await message.answer("💡 <b>Karta javobini (back) kiriting:</b>", parse_mode="HTML")
    await state.set_state(FlashcardCreate.answer)


@router.message(FlashcardCreate.answer, F.text)
async def card_answer(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    """Handle card answer and save."""
    data = await state.get_data()
    await state.clear()

    front = data["question"]
    back = message.text.strip()

    service = FlashcardService(session)
    decks = await service.repo.get_decks(user.id)
    if not decks:
        deck = await service.create_deck(user.id, "Umumiy to'plam")
    else:
        deck = decks[0]

    card = await service.add_card(deck.id, front, back)
    await message.answer(
        f"✅ <b>Karta #{card.id} to'plamga qo'shildi!</b>\n\n"
        f"❓ Savol: <b>{front}</b>\n"
        f"💡 Javob: <b>{back}</b>\n\n"
        "Takrorlash uchun: /study",
        parse_mode="HTML"
    )


@router.message(Command("study"))
@router.callback_query(F.data == "fc_start_study")
async def study_flashcards(event: Message | CallbackQuery, session: AsyncSession, user: User) -> None:
    """Start SM-2 study session."""
    target_msg = event.message if isinstance(event, CallbackQuery) else event
    if isinstance(event, CallbackQuery):
        await event.answer()

    service = FlashcardService(session)
    decks = await service.repo.get_decks(user.id)
    if not decks:
        await target_msg.answer("❌ O'rganish uchun avval /adddeck buyrug'i orqali to'plam va /addcard orqali karta qo'shing.")
        return

    # Find due card or any card
    card = None
    for d in decks:
        due = await service.repo.get_due_cards(d.id, date.today(), limit=1)
        if due:
            card = due[0]
            break
    if not card:
        for d in decks:
            all_cards = await service.repo.get_cards(d.id, limit=1)
            if all_cards:
                card = all_cards[0]
                break

    if not card:
        await target_msg.answer("🎉 <b>Barcha kartalar takrorlangan!</b> Hozircha yangi karta yo'q.", parse_mode="HTML")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁 Javobni ko'rish", callback_data=f"fc_reveal:{card.id}")],
    ])
    text = (
        "🧠 <b>SM-2 Xotira Mashg'uloti</b>\n\n"
        f"❓ <b>Savol:</b>\n{card.front}\n\n"
        "<i>Javobni eslashga harakat qiling va tugmani bosing:</i>"
    )
    await target_msg.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("fc_reveal:"))
async def reveal_card_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    card_id = int(callback.data.split(":")[1])
    service = FlashcardService(session)
    card = await service.repo.get_card_by_id(card_id)
    if not card:
        await callback.answer("Karta topilmadi.")
        return

    text = (
        "🧠 <b>SM-2 Xotira Mashg'uloti</b>\n\n"
        f"❓ <b>Savol:</b>\n{card.front}\n\n"
        f"💡 <b>Javob:</b>\n{card.back}\n\n"
        "<i>Qanchalik oson esladingiz? (Baholang):</i>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔴 Qiyin (1)", callback_data=f"fc_rate:{card.id}:1"),
            InlineKeyboardButton(text="🟡 Yaxshi (3)", callback_data=f"fc_rate:{card.id}:3"),
            InlineKeyboardButton(text="🟢 Oson (5)", callback_data=f"fc_rate:{card.id}:5"),
        ]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("fc_rate:"))
async def rate_card_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    parts = callback.data.split(":")
    card_id = int(parts[1])
    rating = int(parts[2])

    service = FlashcardService(session)
    try:
        await service.review_card(card_id, rating)
        await callback.answer(f"Baho: {rating}/5 saqlandi!")
    except Exception as e:
        logger.error("Flashcard review error", error=str(e))
        await callback.answer("Saqlashda xatolik.")

    await study_flashcards(callback, session, user)
