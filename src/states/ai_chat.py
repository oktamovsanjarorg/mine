from aiogram.fsm.state import State, StatesGroup

class AIChatStates(StatesGroup):
    """States for AI Chat management."""
    chatting = State()
    waiting_system_prompt = State()
    choosing_provider = State()
