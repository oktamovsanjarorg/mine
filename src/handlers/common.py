import structlog
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

logger = structlog.get_logger(__name__)
router = Router(name="common_router")

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    """Handle /start command, register user if needed, and show main menu."""
    await state.clear()
    logger.info("user_started", user_id=message.from_user.id)
    welcome_text = (
        f"👋 Salom, {message.from_user.first_name}!\n\n"
        "Men sizning shaxsiy yordamchingizman. 🤖\n"
        "Quyidagi menyudan kerakli bo'limni tanlang:"
    )
    # Keyboard implementation would go here using src/keyboards/
    await message.answer(welcome_text)

@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """Show help manual."""
    help_text = (
        "📚 <b>Yordam bo'limi</b>\n\n"
        "Asosiy buyruqlar:\n"
        "/start - Botni ishga tushirish 🚀\n"
        "/menu - Asosiy menyu 📋\n"
        "/tasks - Vazifalar 📝\n"
        "/notes - Eslatmalar 📓\n"
        "/finance - Moliya 💰\n"
        "Va boshqalar..."
    )
    await message.answer(help_text, parse_mode="HTML")

@router.message(Command("menu"))
async def menu_handler(message: Message, state: FSMContext) -> None:
    """Show inline main menu."""
    await state.clear()
    await message.answer("📋 Asosiy menyu:")

@router.message(Command("settings"))
async def settings_handler(message: Message) -> None:
    """Show settings menu."""
    await message.answer("⚙️ Sozlamalar:\nTil, vaqt mintaqasi va boshqalarni o'zgartirish:")

@router.message(Command("stats"))
async def stats_handler(message: Message) -> None:
    """Show user statistics."""
    await message.answer("📊 Sizning statistikangiz:\nBarcha vazifalar, xarajatlar va faollik shu yerda ko'rinadi.")

@router.message(Command("profile"))
async def profile_handler(message: Message) -> None:
    """Show user profile."""
    await message.answer(f"👤 Profil:\nIsm: {message.from_user.first_name}\nID: {message.from_user.id}")

@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """Cancel any active FSM state."""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Bekor qilinadigan amal yo'q. 🤷‍♂️")
        return
    await state.clear()
    await message.answer("Amal bekor qilindi. ❌ Asosiy menyuga qaytdingiz.")

@router.message(F.text == "📋 Vazifalar")
async def tasks_menu_btn(message: Message) -> None:
    await message.answer("Vazifalar bo'limiga xush kelibsiz! 📝")

@router.message(F.text == "📝 Eslatmalar")
async def notes_menu_btn(message: Message) -> None:
    await message.answer("Eslatmalar bo'limiga xush kelibsiz! 📓")
