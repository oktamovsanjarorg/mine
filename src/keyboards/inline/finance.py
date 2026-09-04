from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks.factory import FinanceCB, FinanceAction
from src.keyboards.builders import pagination_keyboard, back_button

def finance_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Daromad", callback_data=FinanceCB(action=FinanceAction.ADD_INCOME).pack())
    builder.button(text="➖ Xarajat", callback_data=FinanceCB(action=FinanceAction.ADD_EXPENSE).pack())
    builder.button(text="📊 Hisobot", callback_data=FinanceCB(action=FinanceAction.REPORT).pack())
    builder.button(text="💳 Budjet", callback_data=FinanceCB(action=FinanceAction.BUDGET).pack())
    builder.button(text="📋 Tarix", callback_data=FinanceCB(action=FinanceAction.HISTORY).pack())
    builder.button(text="⬅️ Orqaga", callback_data="menu:main")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()

def transaction_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💰 Daromad", callback_data="trx_type:income")
    builder.button(text="💸 Xarajat", callback_data="trx_type:expense")
    builder.button(text="🔄 Transfer", callback_data="trx_type:transfer")
    builder.adjust(2, 1)
    return builder.as_markup()

def report_period_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    periods = [("📅 Bugun", "today"), ("📅 Bu hafta", "week"), ("📅 Bu oy", "month"), ("📅 Bu yil", "year"), ("📅 Boshqa", "custom")]
    for text, p in periods:
        builder.button(text=text, callback_data=f"report_period:{p}")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

def transaction_list_keyboard(transactions: list[tuple[int, str, float]], page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for trx_id, title, amount in transactions:
        sign = "+" if amount > 0 else ""
        builder.button(text=f"{title}: {sign}{amount}", callback_data=FinanceCB(action=FinanceAction.DETAIL, id=trx_id).pack())
    
    builder.adjust(1)
    
    if total_pages > 1:
        pag_kb = pagination_keyboard(module="finance_trx", current_page=page, total_pages=total_pages)
        for row in pag_kb.inline_keyboard:
            builder.row(*row)
            
    builder.row(back_button("menu:finance"))
    return builder.as_markup()

def budget_list_keyboard(budgets: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for b_id, title in budgets:
        builder.button(text=title, callback_data=f"budget:{b_id}")
    builder.button(text="➕ Yangi Budjet", callback_data="budget:new")
    builder.row(back_button("menu:finance"))
    builder.adjust(1)
    return builder.as_markup()
