from aiogram.fsm.state import State, StatesGroup

class ExportStates(StatesGroup):
    """States for Export management."""
    choosing_module = State()
    choosing_format = State()
    confirming = State()
