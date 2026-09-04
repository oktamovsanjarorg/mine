from aiogram.fsm.state import State, StatesGroup

class ContactStates(StatesGroup):
    """States for Contact management."""
    waiting_name = State()
    waiting_phone = State()
    waiting_email = State()
    waiting_telegram = State()
    waiting_birthday = State()
    waiting_company = State()
    waiting_position = State()
    waiting_notes = State()
    waiting_category = State()
    confirm_create = State()
    editing = State()
