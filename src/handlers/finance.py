"""
Finance Handler - Real Transactions, Balances, Reports, and Inline Controls.
"""

import structlog
import re
from datetime import datetime, date
from decimal import Decimal
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.finance import FinanceService
from src.models.user import User
from src.core.utils.formatters import format_currency

logger = structlog.get_logger(__name__)
router = Router(name="finance_router")


class FinanceState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_desc = State()


def build_finance_menu_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Daromad", callback_data="fin_add:income"),
            InlineKeyboardButton(text="➖ Xarajat", callback_data="fin_add:expense"),
        ],
        [
            InlineKeyboardButton(text="📊 Oylik hisobot", callback_data="fin_report"),
            InlineKeyboardButton(text="📜 Oxirgi amallar", callback_data="fin_history"),
        ],
    ])


@router.message(Command("finance"))
@router.message(F.text == "💰 Moliya")
async def finance_dashboard(message: Message, session: AsyncSession, user: User) -> None:
    """Display comprehensive finance dashboard."""
    service = FinanceService(session)
    balance = await service.get_balance(user.id)
    
    now = datetime.utcnow()
    report = await service.repo.get_monthly_report(user.id, now.year, now.month)
    
    income = report.get("income", 0.0)
    expense = report.get("expense", 0.0)
    
    text = (
        f"💰 <b>Moliya boshqaruv markazi</b>\n\n"
        f"💳 <b>Joriy balans:</b> <code>{format_currency(balance)}</code>\n\n"
        f"📅 <b>Shu oylik ko'rsatkichlar ({now.strftime('%B')}):</b>\n"
        f"🟢 Daromad: <code>+{format_currency(income)}</code>\n"
        f"🔴 Xarajat: <code>-{format_currency(expense)}</code>\n"
        f"📈 Sof farq: <code>{format_currency(income - expense)}</code>\n\n"
        f"<i>Tezkor kiritish uchun:</i>\n"
        f"• <code>/income 500000 Maosh</code>\n"
        f"• <code>/expense 35000 Tushlik</code>"
    )
    await message.answer(text, reply_markup=build_finance_menu_markup(), parse_mode="HTML")


@router.message(Command("balance"))
async def balance_cmd(message: Message, session: AsyncSession, user: User) -> None:
    service = FinanceService(session)
    balance = await service.get_balance(user.id)
    await message.answer(f"💳 Sizning umumiy balansingiz: <b>{format_currency(balance)}</b>", parse_mode="HTML")


@router.message(Command("income"))
async def add_income_cmd(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    args = message.text.split(maxsplit=2)
    if len(args) > 1:
        try:
            amount = float(args[1].replace(" ", "").replace(",", "."))
            desc = args[2] if len(args) > 2 else "Daromad"
            service = FinanceService(session)
            tx = await service.add_transaction(user_id=user.id, amount=amount, category="Daromad", type="income", description=desc)
            bal = await service.get_balance(user.id)
            await message.answer(
                f"✅ <b>Daromad qo'shildi:</b> +{format_currency(tx.amount)}\n"
                f"📝 Tavsif: {tx.description}\n"
                f"💳 Yangi balans: <b>{format_currency(bal)}</b>",
                parse_mode="HTML"
            )
            return
        except ValueError:
            pass

    await state.update_data(tx_type="income")
    await message.answer("🟢 Daromad miqdorini kiriting (masalan: <code>1500000</code>):", parse_mode="HTML")
    await state.set_state(FinanceState.waiting_for_amount)


@router.message(Command("expense"))
async def add_expense_cmd(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    args = message.text.split(maxsplit=2)
    if len(args) > 1:
        try:
            amount = float(args[1].replace(" ", "").replace(",", "."))
            desc = args[2] if len(args) > 2 else "Xarajat"
            service = FinanceService(session)
            tx = await service.add_transaction(user_id=user.id, amount=amount, category="Xarajat", type="expense", description=desc)
            bal = await service.get_balance(user.id)
            await message.answer(
                f"📉 <b>Xarajat qo'shildi:</b> -{format_currency(tx.amount)}\n"
                f"📝 Tavsif: {tx.description}\n"
                f"💳 Yangi balans: <b>{format_currency(bal)}</b>",
                parse_mode="HTML"
            )
            return
        except ValueError:
            pass

    await state.update_data(tx_type="expense")
    await message.answer("🔴 Xarajat miqdorini kiriting (masalan: <code>45000</code>):", parse_mode="HTML")
    await state.set_state(FinanceState.waiting_for_amount)


@router.callback_query(F.data.startswith("fin_add:"))
async def fin_add_callback(callback: CallbackQuery, state: FSMContext) -> None:
    tx_type = callback.data.split(":")[1]
    await state.update_data(tx_type=tx_type)
    action_text = "🟢 Daromad" if tx_type == "income" else "🔴 Xarajat"
    await callback.message.answer(f"{action_text} miqdorini kiriting:")
    await state.set_state(FinanceState.waiting_for_amount)
    await callback.answer()


@router.message(FinanceState.waiting_for_amount, F.text)
async def fin_amount_entered(message: Message, state: FSMContext) -> None:
    cleaned = message.text.replace(" ", "").replace(",", ".").replace("so'm", "").replace("uzs", "").strip()
    try:
        amount = float(cleaned)
        if amount <= 0:
            raise ValueError()
        await state.update_data(amount=amount)
        await message.answer("📝 Ushbu amal uchun tavsif/izoh kiriting (masalan: <i>Bozorlik</i> yoki /skip):", parse_mode="HTML")
        await state.set_state(FinanceState.waiting_for_desc)
    except ValueError:
        await message.answer("❌ Noto'g'ri summa kiritildi. Iltimos, faqat musbat raqam kiriting:")


@router.message(FinanceState.waiting_for_desc, F.text)
async def fin_desc_entered(message: Message, state: FSMContext, session: AsyncSession, user: User) -> None:
    data = await state.get_data()
    await state.clear()

    desc = "Umumiy" if message.text.strip() == "/skip" else message.text.strip()
    amount = data["amount"]
    tx_type = data.get("tx_type", "expense")

    service = FinanceService(session)
    tx = await service.add_transaction(
        user_id=user.id,
        amount=amount,
        category="Umumiy",
        type=tx_type,
        description=desc
    )
    bal = await service.get_balance(user.id)
    
    icon = "🟢 +" if tx_type == "income" else "🔴 -"
    await message.answer(
        f"✅ <b>Amal muvaffaqiyatli saqlandi!</b>\n\n"
        f"{icon}{format_currency(tx.amount)}\n"
        f"📝 Izoh: {tx.description}\n"
        f"💳 Yangi balans: <b>{format_currency(bal)}</b>",
        reply_markup=build_finance_menu_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "fin_report")
@router.message(Command("report"))
async def fin_report_handler(event: Message | CallbackQuery, session: AsyncSession, user: User) -> None:
    message = event if isinstance(event, Message) else event.message
    service = FinanceService(session)
    now = datetime.utcnow()
    report = await service.repo.get_monthly_report(user.id, now.year, now.month)
    
    text = (
        f"📊 <b>{now.year}-yil {now.strftime('%B')} oylik hisoboti</b>\n\n"
        f"🟢 Jami daromad: <b>+{format_currency(report.get('income', 0))}</b>\n"
        f"🔴 Jami xarajat: <b>-{format_currency(report.get('expense', 0))}</b>\n"
        f"💵 Oylik sof foyda: <b>{format_currency(report.get('balance', 0))}</b>"
    )
    await message.answer(text, reply_markup=build_finance_menu_markup(), parse_mode="HTML")
    if isinstance(event, CallbackQuery):
        await event.answer()


@router.callback_query(F.data == "fin_history")
async def fin_history_callback(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    service = FinanceService(session)
    txs = await service.repo.get_all(user_id=user.id, limit=10, order_by="date", desc=True)
    
    if not txs:
        await callback.message.answer("📜 Hozircha hech qanday tranzaksiya mavjud emas.")
        await callback.answer()
        return

    lines = ["📜 <b>Oxirgi 10 ta moliyaviy amal:</b>\n"]
    for t in txs:
        icon = "🟢 +" if t.type in ("income", "INCOME") else "🔴 -"
        lines.append(f"• {t.date}: {icon}{format_currency(t.amount)} ({t.description or 'Izohsiz'})")

    await callback.message.answer("\n".join(lines), parse_mode="HTML")
    await callback.answer()
