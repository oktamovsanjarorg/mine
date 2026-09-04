from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks.factory import HabitCB, HabitAction
from src.keyboards.builders import back_button

def habit_list_keyboard(habits: list[tuple[int, str]], today_logs: list[int]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for habit_id, title in habits:
        status = "✅" if habit_id in today_logs else "⬜"
        builder.button(text=f"{status} {title}", callback_data=HabitCB(action=HabitAction.DETAIL, id=habit_id).pack())
        builder.button(text="[+]", callback_data=HabitCB(action=HabitAction.CHECK, id=habit_id).pack())
    builder.adjust(2)
    builder.row(back_button("menu:main"))
    return builder.as_markup()

def habit_detail_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Belgilash", callback_data=HabitCB(action=HabitAction.CHECK, id=habit_id).pack())
    builder.button(text="📊 Statistika", callback_data=HabitCB(action=HabitAction.STATS, id=habit_id).pack())
    builder.button(text="✏️ Tahrirlash", callback_data=HabitCB(action=HabitAction.EDIT, id=habit_id).pack())
    builder.button(text="🗑 O'chirish", callback_data=HabitCB(action=HabitAction.DELETE, id=habit_id).pack())
    builder.button(text="⬅️ Orqaga", callback_data=HabitCB(action=HabitAction.LIST, id=0).pack())
    builder.adjust(2, 2, 1)
    return builder.as_markup()

def habit_checkin_keyboard(habits: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for habit_id, title in habits:
        builder.button(text=f"✅ {title}", callback_data=HabitCB(action=HabitAction.CHECK, id=habit_id).pack())
    builder.adjust(1)
    builder.row(back_button("menu:main"))
    return builder.as_markup()

def frequency_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    frequencies = [("Har kuni", "daily"), ("Har hafta", "weekly"), ("Boshqa", "custom")]
    for text, f in frequencies:
        builder.button(text=text, callback_data=f"habit_freq:{f}")
    builder.adjust(2, 1)
    return builder.as_markup()
