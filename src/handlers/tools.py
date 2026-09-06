"""
Tools & Utilities Handler - Weather, Calculator, QR Generator, Password Generator, and Encoding.
"""

import io
import ast
import time
import uuid
import base64
import operator
import qrcode
import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from src.core.utils.crypto import generate_password

logger = structlog.get_logger(__name__)
router = Router(name="tools_router")

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def safe_eval(node):
    if isinstance(node, ast.Expression):
        return safe_eval(node.body)
    elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.BinOp):
        op = type(node.op)
        if op in OPERATORS:
            return OPERATORS[op](safe_eval(node.left), safe_eval(node.right))
    elif isinstance(node, ast.UnaryOp):
        op = type(node.op)
        if op in OPERATORS:
            return OPERATORS[op](safe_eval(node.operand))
    raise ValueError("Ruxsat berilmagan ifoda")


@router.message(Command("calc"))
async def calc_math(message: Message) -> None:
    """Safe mathematical expression calculator."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("ℹ️ Foydalanish: <code>/calc 25 * 4 + 100</code>", parse_mode="HTML")
        return

    expr = args[1].strip()
    try:
        parsed = ast.parse(expr, mode='eval')
        result = safe_eval(parsed)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        await message.answer(
            f"🧮 <b>Hisoblash natijasi:</b>\n\n"
            f"<code>{expr}</code> = <b>{result}</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Xatolik: Ifodani hisoblab bo'lmadi ({e}).")


@router.message(Command("qr"))
async def generate_qr(message: Message) -> None:
    """Generate high quality QR code image."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("ℹ️ Foydalanish: <code>/qr https://example.com</code> yoki <code>/qr Salom</code>", parse_mode="HTML")
        return

    text = args[1].strip()
    try:
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        bio = io.BytesIO()
        img.save(bio, "PNG")
        bio.seek(0)

        photo = BufferedInputFile(bio.read(), filename="qrcode.png")
        await message.answer_photo(
            photo=photo,
            caption=f"📱 <b>QR-kod tayyor!</b>\n\n<code>{text[:100]}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error("QR creation failed", error=str(e))
        await message.answer("❌ QR-kod yaratishda xatolik yuz berdi.")


@router.message(Command("pass"))
async def generate_pass_handler(message: Message) -> None:
    """Generate strong random password."""
    args = message.text.split()
    length = 16
    if len(args) > 1 and args[1].isdigit():
        length = min(max(int(args[1]), 8), 64)

    pwd = generate_password(length=length)
    await message.answer(
        f"🔐 <b>Xavfsiz parol ({length} belgi):</b>\n\n"
        f"<code>{pwd}</code>\n\n"
        f"<i>Nusxa olish uchun parol ustiga bosing.</i>",
        parse_mode="HTML"
    )


@router.message(Command("uuid"))
async def generate_uuid(message: Message) -> None:
    """Generate UUIDv4."""
    val = uuid.uuid4()
    await message.answer(f"🔑 <b>UUIDv4:</b>\n<code>{val}</code>", parse_mode="HTML")


@router.message(Command("base64"))
async def encode_base64(message: Message) -> None:
    """Encode text to Base64."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("ℹ️ Foydalanish: <code>/base64 Matn</code>", parse_mode="HTML")
        return
    encoded = base64.b64encode(args[1].encode()).decode()
    await message.answer(f"🔠 <b>Base64:</b>\n<code>{encoded}</code>", parse_mode="HTML")


@router.message(Command("timestamp"))
async def get_timestamp(message: Message) -> None:
    """Get current unix timestamp."""
    ts = int(time.time())
    await message.answer(f"⏱ <b>Unix Timestamp:</b> <code>{ts}</code>", parse_mode="HTML")


@router.message(Command("weather"))
async def get_weather(message: Message) -> None:
    """Get weather info and check 10°C sharp difference rule."""
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
    else:
        text += "\n\n<i>Bugun va ertaga o'rtasida keskin harorat farqi (10°C) kuzatilmayapti.</i>"
    await message.answer(text, parse_mode="HTML")
