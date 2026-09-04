from aiogram.fsm.state import State, StatesGroup

class SettingsStates(StatesGroup):
    """States for Settings management."""
    choosing_setting = State()
    changing_language = State()
    changing_timezone = State()
    changing_currency = State()
    changing_digest_time = State()
    changing_ai_provider = State()
