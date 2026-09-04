import os

handlers_dir = "/home/sanjar/mine/sanjar-bot/src/handlers/"
os.makedirs(handlers_dir, exist_ok=True)

files = {
    "reminders.py": """import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

logger = structlog.get_logger(__name__)
router = Router(name="reminders_router")

@router.message(Command("reminders"))
async def list_reminders(message: Message):
    await message.answer("⏰ Barcha eslatmalar ro'yxati:")

@router.message(Command("remind"))
async def add_reminder(message: Message):
    await message.answer("⏰ Eslatma qachonga belgilansin? (Masalan: /remind 10m choy ichish)")
""",
    "finance.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="finance_router")

@router.message(Command("finance"))
async def finance_menu(message: Message):
    await message.answer("💰 Moliya bo'limi:")
""",
    "habits.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="habits_router")

@router.message(Command("habits"))
async def habits_menu(message: Message):
    await message.answer("🔄 Odatlar bo'limi:")
""",
    "health.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="health_router")

@router.message(Command("health"))
async def health_menu(message: Message):
    await message.answer("❤️ Salomatlik bo'limi:")
""",
    "journal.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="journal_router")

@router.message(Command("journal"))
async def journal_menu(message: Message):
    await message.answer("📖 Kundalik bo'limi:")
""",
    "bookmarks.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="bookmarks_router")

@router.message(Command("bookmarks"))
async def bookmarks_menu(message: Message):
    await message.answer("🔖 Xatcho'plar bo'limi:")
""",
    "goals.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="goals_router")

@router.message(Command("goals"))
async def goals_menu(message: Message):
    await message.answer("🎯 Maqsadlar bo'limi:")
""",
    "flashcards.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="flashcards_router")

@router.message(Command("flashcards"))
async def flashcards_menu(message: Message):
    await message.answer("🗂 Flashcardlar bo'limi:")
""",
    "contacts.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="contacts_router")

@router.message(Command("contacts"))
async def contacts_menu(message: Message):
    await message.answer("📞 Kontaktlar bo'limi:")
""",
    "snippets.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="snippets_router")

@router.message(Command("snippets"))
async def snippets_menu(message: Message):
    await message.answer("✂️ Snippetlar bo'limi:")
""",
    "files.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="files_router")

@router.message(Command("files"))
async def files_menu(message: Message):
    await message.answer("📁 Fayllar bo'limi:")
""",
    "monitors.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="monitors_router")

@router.message(Command("monitors"))
async def monitors_menu(message: Message):
    await message.answer("📈 Monitorlar bo'limi:")
""",
    "rss.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="rss_router")

@router.message(Command("rss"))
async def rss_menu(message: Message):
    await message.answer("📰 RSS bo'limi:")
""",
    "pomodoro.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="pomodoro_router")

@router.message(Command("pomodoro"))
async def pomodoro_menu(message: Message):
    await message.answer("🍅 Pomodoro bo'limi:")
""",
    "ai_chat.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="ai_chat_router")

@router.message(Command("ai"))
async def ai_menu(message: Message):
    await message.answer("🤖 AI Chat bo'limi:")
""",
    "quick_notes.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="quick_notes_router")

@router.message(Command("clip"))
async def clip_menu(message: Message):
    await message.answer("📎 Tezkor eslatmalar:")
""",
    "tools.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="tools_router")

@router.message(Command("calc"))
async def tools_menu(message: Message):
    await message.answer("🛠 Asboblar bo'limi:")
""",
    "export.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="export_router")

@router.message(Command("export"))
async def export_menu(message: Message):
    await message.answer("📤 Eksport bo'limi:")
""",
    "admin.py": """import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="admin_router")

@router.message(Command("admin"))
async def admin_menu(message: Message):
    await message.answer("👑 Admin panel:")
"""
}

for name, content in files.items():
    with open(os.path.join(handlers_dir, name), "w") as f:
        f.write(content)

print("All 19 additional files created.")
