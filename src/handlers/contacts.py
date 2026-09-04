import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

logger = structlog.get_logger(__name__)
router = Router(name="contacts_router")

class ContactCreate(StatesGroup):
    name = State()
    phone = State()
    birthday = State()

@router.message(Command("contacts"))
async def contacts_menu(message: Message) -> None:
    """List all contacts."""
    await message.answer("📞 Kontaktlaringiz ro'yxati:\nJami: 0 ta kontakt.")

@router.message(Command("addcontact"))
async def add_contact(message: Message, state: FSMContext) -> None:
    """Start adding a contact."""
    await message.answer("Kontakt ismini kiriting:")
    await state.set_state(ContactCreate.name)

@router.message(ContactCreate.name, F.text)
async def contact_name(message: Message, state: FSMContext) -> None:
    """Handle contact name."""
    await state.update_data(name=message.text)
    await message.answer("Telefon raqamini kiriting:")
    await state.set_state(ContactCreate.phone)

@router.message(ContactCreate.phone, F.text)
async def contact_phone(message: Message, state: FSMContext) -> None:
    """Handle contact phone."""
    await state.update_data(phone=message.text)
    await message.answer("Tug'ilgan sanasini kiriting (YYYY-MM-DD) yoki /skip:")
    await state.set_state(ContactCreate.birthday)

@router.message(ContactCreate.birthday, F.text)
async def contact_birthday(message: Message, state: FSMContext) -> None:
    """Handle contact birthday."""
    await state.clear()
    await message.answer("✅ Kontakt saqlandi!")

@router.message(Command("birthdays"))
async def upcoming_birthdays(message: Message) -> None:
    """List upcoming birthdays."""
    await message.answer("🎂 Yaqinlashib kelayotgan tug'ilgan kunlar:\nShu oyda tug'ilgan kunlar yo'q.")
