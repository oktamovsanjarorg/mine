from aiogram.fsm.state import State, StatesGroup

class FlashcardStates(StatesGroup):
    """States for Flashcard management."""
    creating_deck_name = State()
    creating_deck_description = State()
    adding_card_front = State()
    adding_card_back = State()
    adding_card_hint = State()
    studying = State()
    reviewing = State()
