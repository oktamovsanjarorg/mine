from aiogram.fsm.state import State, StatesGroup

class TaskStates(StatesGroup):
    """States for Task management."""
    waiting_title = State()
    waiting_description = State()
    waiting_priority = State()
    waiting_due_date = State()
    waiting_category = State()
    waiting_reminder = State()
    confirm_create = State()
    editing_field = State()
    editing_value = State()
