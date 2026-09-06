import structlog
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.contact import ContactService

logger = structlog.get_logger(__name__)
router = Router(name="contacts_router")


class ContactCreate(StatesGroup):
    name = State()
    phone = State()
    birthday = State()


@router.message(Command("contacts"))
@router.message(F.text == "👤 Kontaktlar")
async def contacts_menu(message: Message, session: AsyncSession, user: User) -> None:
    """List all contacts."""
    service = ContactService(session)
    contacts = await service.get_contacts(user.id, limit=15)
    if not contacts:
        await message.answer(
            "👤 <b>Sizda hozircha kontaktlar mavjud emas!</b>\n\n"
            "Yangi kontakt kiritish uchun: /addcontact",
            parse_mode="HTML"
        )
        return

    lines = [f"📞 <b>Sizning kontaktlaringiz ({len(contacts)} ta):</b>\n"]
    for i, c in enumerate(contacts, 1):
        phone_str = f" | 📱 <code>{c.phone}</code>" if c.phone else ""
        bday_str = f" | 🎂 {c.birthday.strftime('%d.%m.%Y')}" if c.birthday else ""
        lines.append(f"{i}. <b>#{c.id}: {c.name}</b>{phone_str}{bday_str}")

    lines.append("\n<b>Buyruqlar:</b>")
    lines.append("• /addcontact - Yangi kontakt qo'shish")
    lines.append("• /birthdays - Yaqinlashib kelayotgan tug'ilgan kunlar")
    lines.append("• /vcard <id> - Kontaktni telefon kitobchasiga (.vcf) yuklash")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("addcontact"))
async def add_contact_cmd(message: Message, state: FSMContext) -> None:
    """Start adding a contact."""
    await message.answer("👤 <b>Kontakt ismini (va familiyasini) kiriting:</b>", parse_mode="HTML")
    await state.set_state(ContactCreate.name)


@router.message(ContactCreate.name, F.text)
async def contact_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await message.answer("📱 <b>Telefon raqamini kiriting</b> (masalan: <code>+998901234567</code> yoki /skip):", parse_mode="HTML")
    await state.set_state(ContactCreate.phone)


@router.message(ContactCreate.phone, F.text)
async def contact_phone(message: Message, state: FSMContext) -> None:
    phone = None if message.text.strip() == "/skip" else message.text.strip()
    await state.update_data(phone=phone)
    await message.answer("🎂 <b>Tug'ilgan sanasini kiriting</b> (YYYY-MM-DD, masalan: <code>1998-05-24</code> yoki /skip):", parse_mode="HTML")
    await state.set_state(ContactCreate.birthday)


@router.message(ContactCreate.birthday, F.text)
async def contact_birthday(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    data = await state.get_data()
    await state.clear()

    bday = None
    if message.text.strip() != "/skip":
        try:
            bday = datetime.strptime(message.text.strip(), "%Y-%m-%d").date()
        except ValueError:
            pass

    service = ContactService(session)
    contact = await service.create_contact(
        user_id=user.id,
        name=data["name"],
        phone=data.get("phone") or "",
        birthday=bday
    )

    bday_msg = f"\n🎂 Tug'ilgan sana: {contact.birthday.strftime('%d.%m.%Y')}" if contact.birthday else ""
    await message.answer(
        f"✅ <b>Kontakt muvaffaqiyatli saqlandi!</b>\n\n"
        f"👤 #{contact.id}: <b>{contact.name}</b>\n"
        f"📱 Telefon: <code>{contact.phone or 'kiritilmadi'}</code>"
        f"{bday_msg}\n\n"
        "Kontaktlar ro'yxati: /contacts",
        parse_mode="HTML"
    )


@router.message(Command("birthdays"))
async def upcoming_birthdays(message: Message, session: AsyncSession, user: User) -> None:
    """List upcoming birthdays."""
    service = ContactService(session)
    upcoming = await service.get_upcoming_birthdays(user.id, days=30)
    if not upcoming:
        await message.answer("🎂 <b>Yaqin 30 kun ichida tug'ilgan kunlar yo'q.</b>", parse_mode="HTML")
        return

    lines = ["🎂 <b>Yaqinlashib kelayotgan tug'ilgan kunlar:</b>\n"]
    for i, c in enumerate(upcoming, 1):
        lines.append(f"{i}. 🎉 <b>{c.name}</b> — <b>{c.birthday.strftime('%d-%B')}</b>")

    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("vcard"))
async def export_vcard(message: Message, session: AsyncSession, user: User) -> None:
    """Export contact as .vcf file for easy smartphone import."""
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("ℹ️ Foydalanish: <code>/vcard <id></code>", parse_mode="HTML")
        return

    contact_id = int(args[1])
    service = ContactService(session)
    try:
        vcard_text = await service.vcard_export(contact_id)
        doc = BufferedInputFile(vcard_text.encode("utf-8"), filename=f"contact_{contact_id}.vcf")
        await message.answer_document(doc, caption="📇 <i>Telefon kontaktlariga qo'shish uchun faylni oching.</i>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Xatolik: Kontakt topilmadi ({e})")
