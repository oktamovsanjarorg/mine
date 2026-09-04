from aiogram.fsm.state import State, StatesGroup

class NoteStates(StatesGroup):
    """States for Note management."""
    waiting_title = State()
    waiting_content = State()
    waiting_category = State()
    waiting_tags = State()
    confirm_create = State()
    editing_note = State()
    searching = State()
