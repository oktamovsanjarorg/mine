from aiogram.fsm.state import State, StatesGroup

class JournalStates(StatesGroup):
    """States for Journal management."""
    waiting_content = State()
    waiting_mood = State()
    waiting_energy = State()
    confirm_save = State()
