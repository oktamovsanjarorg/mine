from aiogram.fsm.state import State, StatesGroup

class ReminderStates(StatesGroup):
    """States for Reminder management."""
    waiting_title = State()
    waiting_time = State()
    waiting_repeat = State()
    waiting_message = State()
    confirm_create = State()
