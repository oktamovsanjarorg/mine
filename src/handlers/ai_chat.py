import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="ai_chat_router")

@router.message(Command("ai"))
async def ai_query(message: Message) -> None:
    """Direct AI query."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("AI ga savol bering: /ai <savol>")
        return
    query = args[1]
    await message.answer(f"🤖 AI o'ylamoqda: '{query}'...")

@router.message(Command("chat"))
async def chat_mode(message: Message) -> None:
    """Toggle chat mode."""
    await message.answer("💬 AI suhbat rejimi faollashtirildi. Xabar yuboring!")

@router.message(Command("newchat"))
async def new_chat(message: Message) -> None:
    """Clear chat context."""
    await message.answer("🔄 Suhbat tarixi tozalandi. Yangi suhbatni boshlashingiz mumkin.")

@router.message(Command("translate"))
async def translate_text(message: Message) -> None:
    """Translate text with AI."""
    await message.answer("🔤 Tarjima qilinadigan matnni yuboring:")

@router.message(Command("summarize"))
async def summarize_text(message: Message) -> None:
    """Summarize text with AI."""
    await message.answer("📝 Xulosalanadigan matn yoki havolani yuboring:")

@router.message(Command("explain"))
async def explain_topic(message: Message) -> None:
    """Explain topic with AI."""
    await message.answer("🤔 Tushuntirib berish kerak bo'lgan mavzuni yozing:")

@router.message(Command("grammar"))
async def check_grammar(message: Message) -> None:
    """Check grammar with AI."""
    await message.answer("✍️ Grammatik xatolarini tekshirmoqchi bo'lgan matnni yuboring:")
