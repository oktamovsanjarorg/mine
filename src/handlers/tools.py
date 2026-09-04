import structlog
import uuid
import base64
import json
import time
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = structlog.get_logger(__name__)
router = Router(name="tools_router")

@router.message(Command("uuid"))
async def generate_uuid(message: Message) -> None:
    """Generate UUID."""
    val = uuid.uuid4()
    await message.answer(f"🔑 UUIDv4:\n<code>{val}</code>", parse_mode="HTML")

@router.message(Command("base64"))
async def encode_base64(message: Message) -> None:
    """Encode text to Base64."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Foydalanish: /base64 <matn>")
        return
    encoded = base64.b64encode(args[1].encode()).decode()
    await message.answer(f"🔠 Base64:\n<code>{encoded}</code>", parse_mode="HTML")

@router.message(Command("timestamp"))
async def get_timestamp(message: Message) -> None:
    """Get current unix timestamp."""
    ts = int(time.time())
    await message.answer(f"⏱ Unix Timestamp:\n<code>{ts}</code>", parse_mode="HTML")

@router.message(Command("weather"))
async def get_weather(message: Message) -> None:
    """Get weather info and warn if sharp temperature change >= 10°C."""
    from src.integrations.weather import weather_client
    data = await weather_client.get_current("Tashkent")
    text = (
        f"🌤 <b>Toshkent shahrida ob-havo:</b>\n\n"
        f"🌡 Harorat: <b>{data['temp']}°C</b> (sezilishi: {data['feels_like']}°C)\n"
        f"💧 Namlik: {data['humidity']}%\n"
        f"💨 Shamol: {data['wind']} m/s\n"
        f"☁️ Holat: {data['description']}"
    )
    should_alert, alert_msg = await weather_client.check_temperature_difference("Tashkent", threshold=10.0)
    if should_alert:
        text += f"\n\n{alert_msg}"
    await message.answer(text)

@router.message(Command("calc"))
async def calc_math(message: Message) -> None:
    """Calculate expression."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Foydalanish: /calc 2+2*2")
        return
    expr = args[1]
    # Do NOT use eval in production directly without safety checks
    await message.answer(f"🧮 Hisoblash (xavfsiz rejim kerak): {expr}")
