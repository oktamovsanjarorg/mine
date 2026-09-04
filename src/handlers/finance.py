import structlog
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

logger = structlog.get_logger(__name__)
router = Router(name="finance_router")

class FinanceTx(StatesGroup):
    amount = State()
    category = State()
    description = State()

@router.message(Command("finance"))
async def finance_menu(message: Message) -> None:
    """Show finance dashboard."""
    await message.answer("💰 Moliya bo'limi:\n\nBalansingiz: 0 so'm\n/income - Daromad qo'shish\n/expense - Xarajat qo'shish")

@router.message(Command("income"))
async def add_income(message: Message, state: FSMContext) -> None:
    """Start adding income."""
    args = message.text.split(maxsplit=2)
    if len(args) > 1:
        amount = args[1]
        desc = args[2] if len(args) > 2 else "Daromad"
        await message.answer(f"✅ Daromad qo'shildi: +{amount} ({desc})")
        return
    await message.answer("Daromad miqdorini kiriting:")
    await state.set_state(FinanceTx.amount)
    
@router.message(Command("expense"))
async def add_expense(message: Message, state: FSMContext) -> None:
    """Start adding expense."""
    args = message.text.split(maxsplit=2)
    if len(args) > 1:
        amount = args[1]
        desc = args[2] if len(args) > 2 else "Xarajat"
        await message.answer(f"📉 Xarajat qo'shildi: -{amount} ({desc})")
        return
    await message.answer("Xarajat miqdorini kiriting:")
    await state.set_state(FinanceTx.amount)

@router.message(Command("balance"))
async def balance_handler(message: Message) -> None:
    """Show current balance."""
    await message.answer("💳 Joriy balans: 0 UZS")

@router.message(Command("report"))
async def report_handler(message: Message) -> None:
    """Show financial report."""
    await message.answer("📊 Shu oylik hisobot:\nKirim: 0\nChiqim: 0")
