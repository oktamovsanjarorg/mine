import structlog
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.keyboards.main_menu import get_main_menu_keyboard, get_main_inline_menu
from src.callbacks.factory import MenuCB

logger = structlog.get_logger(__name__)
router = Router(name="common_router")


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext | None = None) -> None:
    """Handle /start command and display main keyboards."""
    if state:
        await state.clear()
    logger.info("user_started", user_id=message.from_user.id)
    
    welcome_text = (
        f"👋 Salom, <b>{message.from_user.first_name}</b>!\n\n"
        "Men sizning barcha ishlaringiz uchun shaxsiy yordamchingizman. 🤖\n\n"
        "Quyidagi klaviatura yoki menyudan kerakli bo'limni tanlang:"
    )
    # Send persistent reply keyboard
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
    # Also send inline interactive menu
    await message.answer("📱 <b>Asosiy boshqaruv paneli:</b>", reply_markup=get_main_inline_menu(), parse_mode="HTML")


@router.message(Command("menu"))
async def menu_handler(message: Message, state: FSMContext) -> None:
    """Show inline main menu."""
    await state.clear()
    await message.answer("📋 <b>Asosiy menyu:</b>", reply_markup=get_main_inline_menu(), parse_mode="HTML")


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """Show help manual."""
    help_text = (
        "📚 <b>Yordam qo'llanmasi</b>\n\n"
        "<b>Asosiy buyruqlar:</b>\n"
        "• /start - Botni ishga tushirish\n"
        "• /menu - Asosiy interaktiv menyu\n"
        "• /tasks - Vazifalar ro'yxati (/addtask)\n"
        "• /notes - Eslatmalar (/addnote, /searchnotes)\n"
        "• /finance - Moliyaviy hisob-kitob (/income, /expense, /balance)\n"
        "• /habits - Odatlar (/checkin)\n"
        "• /health - Salomatlik jurnali (/water, /sleep, /weight)\n"
        "• /journal - Shaxsiy kundalik (/write)\n"
        "• /goals - Maqsadlar (/addgoal)\n"
        "• /flashcards - Flashcardlar bilan o'rganish (/study)\n"
        "• /ai - Sun'iy intellekt bilan suhbat (/ai <savol>)\n"
        "• /weather - 10°C keskin o'zgarish tekshiruvli ob-havo\n"
        "• /calc - Kalkulyator (/calc 2+2*2)\n"
        "• /qr - QR-kod yaratish (/qr <matn>)\n"
        "• /pass - Xavfsiz parol yaratish (/pass 16)\n"
        "• /cancel - Har qanday jarayonni bekor qilish\n"
    )
    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """Cancel any active FSM state."""
    current_state = await state.get_state()
    await state.clear()
    if current_state:
        await message.answer("❌ Amal bekor qilindi. Asosiy menyudasiz.", reply_markup=get_main_menu_keyboard())
    else:
        await message.answer("Hozir hech qanday faol amal yo'q.", reply_markup=get_main_menu_keyboard())


# ==================== REPLY BUTTON ROUTING ====================

@router.message(F.text == "📋 Vazifalar")
async def tasks_menu_btn(message: Message) -> None:
    from src.keyboards.inline.tasks import task_filter_keyboard
    await message.answer("📋 <b>Vazifalar bo'limi:</b>\n\nKerakli toifani tanlang:", reply_markup=task_filter_keyboard(), parse_mode="HTML")


@router.message(F.text == "📝 Eslatmalar")
async def notes_menu_btn(message: Message) -> None:
    from src.keyboards.inline.notes import note_filter_keyboard
    await message.answer("📝 <b>Eslatmalar bo'limi:</b>\n\nYangi eslatma yozish uchun /addnote buyrug'idan foydalaning.", reply_markup=note_filter_keyboard(), parse_mode="HTML")


@router.message(F.text == "💰 Moliya")
async def finance_menu_btn(message: Message) -> None:
    from src.keyboards.inline.finance import finance_menu_keyboard
    await message.answer("💰 <b>Moliya boshqaruvi:</b>\n\nDaromad yoki xarajatni kiriting yoki hisobotni ko'ring:", reply_markup=finance_menu_keyboard(), parse_mode="HTML")


@router.message(F.text == "🎯 Maqsadlar")
async def goals_menu_btn(message: Message) -> None:
    await message.answer("🎯 <b>Maqsadlar:</b>\nYangi maqsad qo'shish uchun: /addgoal\nRo'yxat: /goals", parse_mode="HTML")


@router.message(F.text == "✅ Odatlar")
async def habits_menu_btn(message: Message) -> None:
    await message.answer("✅ <b>Odatlar kuzatuvi:</b>\nBugungi odatlaringizni belgilash uchun /checkin yoki /habits buyrug'ini yuboring.", parse_mode="HTML")


@router.message(F.text == "🏥 Salomatlik")
async def health_menu_btn(message: Message) -> None:
    from src.keyboards.inline.health import health_menu_keyboard
    await message.answer("🏥 <b>Salomatlik nazorati:</b>\nKo'rsatkichlarni kiriting:", reply_markup=health_menu_keyboard(), parse_mode="HTML")


@router.message(F.text == "📓 Kundalik")
async def journal_menu_btn(message: Message) -> None:
    await message.answer("📓 <b>Shaxsiy Kundalik:</b>\nBugungi fikrlaringizni yozish uchun /write buyrug'ini yuboring.", parse_mode="HTML")


@router.message(F.text == "🔖 Xatcho'p")
async def bookmarks_menu_btn(message: Message) -> None:
    await message.answer("🔖 <b>Xatcho'plar:</b>\nBotga istalgan veb-havola (URL) yuborsangiz, avtomatik saqlab oladi. Ro'yxat: /bookmarks", parse_mode="HTML")


@router.message(F.text == "📚 Flashcard")
async def flashcards_menu_btn(message: Message) -> None:
    await message.answer("📚 <b>Flashcardlar bilan takrorlash:</b>\nO'rganishni boshlash: /study\nYangi to'plam: /adddeck", parse_mode="HTML")


@router.message(F.text == "👤 Kontaktlar")
async def contacts_menu_btn(message: Message) -> None:
    await message.answer("👤 <b>Kontaktlar daftari:</b>\nYangi kontakt: /addcontact\nTug'ilgan kunlar: /birthdays", parse_mode="HTML")


@router.message(F.text == "💻 Kod")
async def code_menu_btn(message: Message) -> None:
    await message.answer("💻 <b>Kod parchalari (Snippets):</b>\nRo'yxat: /snippets\nYangi kod qo'shish: /addsnippet", parse_mode="HTML")


@router.message(F.text == "📁 Fayllar")
async def files_menu_btn(message: Message) -> None:
    await message.answer("📁 <b>MinIO Fayllar xotirasi:</b>\nBotga har qanday rasm, hujjat yoki audio yuborsangiz, avtomatik bulutga arxivlanadi. Ro'yxat: /files", parse_mode="HTML")


@router.message(F.text == "🤖 AI Chat")
async def ai_menu_btn(message: Message) -> None:
    await message.answer(
        "🤖 <b>AI Yordamchi:</b>\n\n"
        "AI ga to'g'ridan-to'g'ri savol berish uchun:\n"
        "<code>/ai O'zbekistonda dasturchilar uchun qanday imkoniyatlar bor?</code>\n\n"
        "Suhbat rejimini ochish: /chat",
        parse_mode="HTML"
    )


@router.message(F.text == "🛠 Asboblar")
async def tools_menu_btn(message: Message) -> None:
    await message.answer(
        "🛠 <b>Foydali asboblar:</b>\n\n"
        "• /weather - Ob-havo ma'lumoti\n"
        "• /calc 15*8+120 - Tezkor kalkulyator\n"
        "• /qr <matn> - QR kod yasash\n"
        "• /pass 16 - Mustahkam parol generatsiya qilish\n"
        "• /uuid - Unikal UUID olish",
        parse_mode="HTML"
    )


@router.message(F.text == "⚙️ Sozlamalar")
async def settings_menu_btn(message: Message) -> None:
    await message.answer("⚙️ <b>Sozlamalar:</b>\nTil: O'zbek\nVaqt mintaqasi: Asia/Tashkent\nValyuta: UZS\nOb-havo: Faqat 10°C+ keskin farqda ogohlantirish", parse_mode="HTML")


# ==================== INLINE MENU CALLBACK HANDLER ====================

@router.callback_query(MenuCB.filter())
async def inline_menu_callback(callback: CallbackQuery, callback_data: MenuCB) -> None:
    """Handle clicks on main inline menu buttons."""
    action = callback_data.action
    await callback.answer()
    
    mapping = {
        "tasks": ("📋 <b>Vazifalar:</b> /tasks yoki /addtask", tasks_menu_btn),
        "notes": ("📝 <b>Eslatmalar:</b> /notes yoki /addnote", notes_menu_btn),
        "finance": ("💰 <b>Moliya:</b> /finance yoki /balance", finance_menu_btn),
        "goals": ("🎯 <b>Maqsadlar:</b> /goals yoki /addgoal", goals_menu_btn),
        "habits": ("✅ <b>Odatlar:</b> /habits yoki /checkin", habits_menu_btn),
        "health": ("🏥 <b>Salomatlik:</b> /health yoki /water", health_menu_btn),
        "journal": ("📓 <b>Kundalik:</b> /journal yoki /write", journal_menu_btn),
        "bookmarks": ("🔖 <b>Xatcho'plar:</b> /bookmarks", bookmarks_menu_btn),
        "flashcards": ("📚 <b>Flashcard:</b> /flashcards yoki /study", flashcards_menu_btn),
        "contacts": ("👤 <b>Kontaktlar:</b> /contacts", contacts_menu_btn),
        "code": ("💻 <b>Kodlar:</b> /snippets", code_menu_btn),
        "files": ("📁 <b>Fayllar:</b> /files", files_menu_btn),
        "ai_chat": ("🤖 <b>AI Chat:</b> /ai <savol>", ai_menu_btn),
        "tools": ("🛠 <b>Asboblar:</b> /weather, /calc, /qr", tools_menu_btn),
        "settings": ("⚙️ <b>Sozlamalar:</b> /settings", settings_menu_btn),
    }
    
    if action in mapping:
        text, func = mapping[action]
        await callback.message.answer(text, parse_mode="HTML")

# Aliases for backward compatibility with test suites
cmd_start = start_handler
cmd_help = help_handler
