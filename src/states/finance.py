from aiogram.fsm.state import State, StatesGroup

class FinanceStates(StatesGroup):
    """States for Finance management."""
    waiting_type = State()
    waiting_amount = State()
    waiting_currency = State()
    waiting_category = State()
    waiting_description = State()
    waiting_date = State()
    waiting_payment_method = State()
    confirm_transaction = State()
    report_type = State()
    report_period = State()
    budget_name = State()
    budget_amount = State()
    budget_period = State()
    budget_category = State()
