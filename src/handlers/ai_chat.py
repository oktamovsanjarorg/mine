import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from src.config import settings

logger = structlog.get_logger(__name__)
router = Router(name="ai_chat_router")


async def generate_ai_reply(prompt: str) -> str:
    """Generate reply using Gemini or OpenAI with fallbacks."""
    # 1. Try Gemini
    if settings.gemini_api_key:
        try:
            from src.integrations.gemini import gemini_client
            if gemini_client and gemini_client.model:
                reply = await gemini_client.generate_text(
                    prompt=prompt,
                    system_prompt="Siz Sanjar uchun shaxsiy yordamchi AI siz. O'zbek tilida juda aniq, do'stona va amaliy javob bering."
                )
                if reply and reply.strip():
                    return reply
        except Exception as e:
            logger.warning("Gemini query failed", error=str(e))

    # 2. Try OpenAI
    if settings.openai_api_key:
        try:
            from src.integrations.openai_client import openai_client
            if openai_client and openai_client.client:
                messages = [
                    {"role": "system", "content": "Siz Sanjar uchun shaxsiy yordamchi AI siz. O'zbek tilida javob bering."},
                    {"role": "user", "content": prompt}
                ]
                reply = await openai_client.chat_completion(messages=messages)
                if reply and reply.strip():
                    return reply
        except Exception as e:
            logger.warning("OpenAI query failed", error=str(e))

    return (
        "🤖 <b>AI Xizmati Ulandi va Tayyor!</b>\n\n"
        "AI bilan jonli muloqot qilish uchun <code>GEMINI_API_KEY</code> yoki <code>OPENAI_API_KEY</code> kerak.\n\n"
        "💡 <b>Google Gemini API kaliti bepul beriladi:</b>\n"
        "👉 <a href='https://aistudio.google.com/app/apikey'>aistudio.google.com/app/apikey</a>\n\n"
        "Kalitingizni shu yerga yuborsangiz yoki <code>.env</code> ga qo'shsangiz, darhol ishga tushadi!"
    )


@router.message(Command("ai"))
async def ai_query(message: Message) -> None:
    """Direct AI query."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "💡 <b>Foydalanish:</b>\n<code>/ai Python da eng tezkor async kutubxona qaysi?</code>",
            parse_mode="HTML"
        )
        return
    query = args[1]
    wait_msg = await message.answer("🧠 <i>AI o'ylamoqda...</i>", parse_mode="HTML")
    try:
        reply = await generate_ai_reply(query)
        await wait_msg.edit_text(reply, parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        reply = await generate_ai_reply(query)
        await wait_msg.edit_text(reply)


@router.message(Command("chat"))
async def chat_mode(message: Message) -> None:
    """Toggle chat mode."""
    await message.answer(
        "💬 <b>AI Suhbat Rejimi:</b>\n\n"
        "Istalgan savolingizni <code>/ai savolingiz</code> ko'rinishida yuboring!",
        parse_mode="HTML"
    )


@router.message(Command("translate"))
async def translate_text(message: Message) -> None:
    """Translate text with AI."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("💡 <b>Foydalanish:</b> /translate <matn>", parse_mode="HTML")
        return
    wait_msg = await message.answer("🔤 <i>Tarjima qilinmoqda...</i>", parse_mode="HTML")
    reply = await generate_ai_reply(f"Quyidagi matnni O'zbek tiliga mukammal tarjima qilib ber:\n\n{args[1]}")
    await wait_msg.edit_text(reply)
