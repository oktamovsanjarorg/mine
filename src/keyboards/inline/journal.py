from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks.factory import JournalCB, JournalAction
from src.keyboards.builders import back_button

def mood_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    moods = [("😢", "sad"), ("😐", "neutral"), ("😊", "good"), ("😄", "happy"), ("🤩", "awesome")]
    for emoji, mood in moods:
        builder.button(text=emoji, callback_data=JournalCB(action=JournalAction.LOG_MOOD, extra=mood).pack())
    builder.adjust(5)
    return builder.as_markup()

def energy_level_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.button(text=f"{i} ⚡", callback_data=f"journal_energy:{i}")
    builder.adjust(5)
    return builder.as_markup()
