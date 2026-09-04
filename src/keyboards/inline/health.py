from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks.factory import HealthCB, HealthAction
from src.keyboards.builders import back_button

def health_dashboard_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💧 Suv ichish", callback_data=HealthCB(action=HealthAction.LOG_WATER).pack())
    builder.button(text="🏃‍♂️ Mashg'ulot", callback_data=HealthCB(action=HealthAction.LOG_WORKOUT).pack())
    builder.button(text="😴 Uyqu", callback_data=HealthCB(action=HealthAction.LOG_SLEEP).pack())
    builder.button(text="📊 Statistika", callback_data=HealthCB(action=HealthAction.STATS).pack())
    builder.button(text="⬅️ Orqaga", callback_data="menu:main")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

def log_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    types = [("💧 Suv", "water"), ("🏃‍♂️ Mashq", "workout"), ("😴 Uyqu", "sleep"), ("⚖️ Vazn", "weight")]
    for text, t in types:
        builder.button(text=text, callback_data=f"health_log:{t}")
    builder.adjust(2, 2)
    return builder.as_markup()
