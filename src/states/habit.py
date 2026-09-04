from aiogram.fsm.state import State, StatesGroup

class HabitStates(StatesGroup):
    """States for Habit management."""
    waiting_name = State()
    waiting_description = State()
    waiting_icon = State()
    waiting_frequency = State()
    waiting_target = State()
    waiting_reminder_time = State()
    confirm_create = State()
    editing = State()
