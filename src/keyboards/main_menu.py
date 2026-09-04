from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from src.callbacks.factory import MenuCB

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy reply keyboard."""
    builder = ReplyKeyboardBuilder()
    buttons = [
        ["📋 Vazifalar", "📝 Eslatmalar", "💰 Moliya"],
        ["🎯 Maqsadlar", "✅ Odatlar", "🏥 Salomatlik"],
        ["📓 Kundalik", "🔖 Xatcho'p", "📚 Flashcard"],
        ["👤 Kontaktlar", "💻 Kod", "📁 Fayllar"],
        ["🤖 AI Chat", "🛠 Asboblar", "⚙️ Sozlamalar"]
    ]
    for row in buttons:
        for btn in row:
            builder.button(text=btn)
    builder.adjust(3, 3, 3, 3, 3)
    return builder.as_markup(resize_keyboard=True)

def get_main_inline_menu() -> InlineKeyboardMarkup:
    """Asosiy inline keyboard — /menu uchun."""
    builder = InlineKeyboardBuilder()
    menus = [
        ("📋 Vazifalar", "tasks"), ("📝 Eslatmalar", "notes"), ("💰 Moliya", "finance"),
        ("🎯 Maqsadlar", "goals"), ("✅ Odatlar", "habits"), ("🏥 Salomatlik", "health"),
        ("📓 Kundalik", "journal"), ("🔖 Xatcho'p", "bookmarks"), ("📚 Flashcard", "flashcards"),
        ("👤 Kontaktlar", "contacts"), ("💻 Kod", "code"), ("📁 Fayllar", "files"),
        ("🤖 AI Chat", "ai_chat"), ("🛠 Asboblar", "tools"), ("⚙️ Sozlamalar", "settings")
    ]
    for text, action in menus:
        builder.button(text=text, callback_data=MenuCB(action=action))
    builder.adjust(3, 3, 3, 3, 3)
    return builder.as_markup()
