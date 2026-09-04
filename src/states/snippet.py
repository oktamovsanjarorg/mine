from aiogram.fsm.state import State, StatesGroup

class SnippetStates(StatesGroup):
    """States for Snippet management."""
    waiting_title = State()
    waiting_language = State()
    waiting_code = State()
    waiting_description = State()
    confirm_create = State()
