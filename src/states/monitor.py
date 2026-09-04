from aiogram.fsm.state import State, StatesGroup

class MonitorStates(StatesGroup):
    """States for Monitor management."""
    waiting_name = State()
    waiting_url = State()
    waiting_selector = State()
    waiting_interval = State()
    confirm_create = State()
