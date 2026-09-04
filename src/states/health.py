from aiogram.fsm.state import State, StatesGroup

class HealthStates(StatesGroup):
    """States for Health management."""
    waiting_type = State()
    waiting_value = State()
    waiting_note = State()
    confirm_log = State()
