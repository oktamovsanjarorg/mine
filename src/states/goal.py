from aiogram.fsm.state import State, StatesGroup

class GoalStates(StatesGroup):
    """States for Goal management."""
    waiting_title = State()
    waiting_description = State()
    waiting_target = State()
    waiting_unit = State()
    waiting_deadline = State()
    waiting_icon = State()
    confirm_create = State()
    updating_progress = State()
