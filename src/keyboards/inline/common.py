from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks.factory import ConfirmCB, MenuCB
from src.keyboards.builders import back_button

def confirm_delete_keyboard(target: str, id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha, o'chirish", callback_data=ConfirmCB(target=target, id=id, confirm=True))
    builder.button(text="❌ Bekor qilish", callback_data=ConfirmCB(target=target, id=id, confirm=False))
    return builder.as_markup()

def yes_no_keyboard(target: str, id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha", callback_data=ConfirmCB(target=target, id=id, confirm=True))
    builder.button(text="❌ Yo'q", callback_data=ConfirmCB(target=target, id=id, confirm=False))
    return builder.as_markup()

def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(back_button())
    return builder.as_markup()

def back_button_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(back_button(callback_data=callback_data))
    return builder.as_markup()

def priority_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    priorities = [("🟢 Past", 1), ("🟡 O'rtacha", 2), ("🟠 Yuqori", 3), ("🔴 Muhim", 4), ("⚫ Shoshilinch", 5)]
    for text, level in priorities:
        builder.button(text=text, callback_data=f"priority:{level}")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

def status_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    statuses = [("⏳ Kutilmoqda", "pending"), ("▶️ Jarayonda", "in_progress"), ("✅ Bajarildi", "done")]
    for text, status in statuses:
        builder.button(text=text, callback_data=f"status:{status}")
    builder.adjust(2, 1)
    return builder.as_markup()

def category_select_keyboard(categories: list[tuple[int, str]], cat_type: str, selected_id: int = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat_id, name in categories:
        text = f"✅ {name}" if cat_id == selected_id else name
        builder.button(text=text, callback_data=f"cat:{cat_type}:{cat_id}")
    builder.button(text="➕ Yangi kategoriya", callback_data=f"cat:{cat_type}:new")
    builder.adjust(2)
    return builder.as_markup()

def tag_select_keyboard(tags: list[tuple[int, str]], selected_ids: list[int] = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    selected = selected_ids or []
    for tag_id, name in tags:
        text = f"✅ {name}" if tag_id in selected else name
        builder.button(text=text, callback_data=f"tag:{tag_id}")
    builder.button(text="➕ Yangi teg", callback_data="tag:new")
    builder.button(text="✅ Tasdiqlash", callback_data="tag:confirm")
    builder.adjust(3)
    return builder.as_markup()

def date_quick_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    dates = [("Bugun", "today"), ("Ertaga", "tomorrow"), ("Bu hafta", "this_week"), ("Bu oy", "this_month"), ("Boshqa", "other")]
    for text, cb in dates:
        builder.button(text=text, callback_data=f"date:{cb}")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

def time_quick_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    times = ["08:00", "09:00", "10:00", "12:00", "14:00", "18:00", "20:00", "22:00"]
    for t in times:
        builder.button(text=t, callback_data=f"time:{t}")
    builder.button(text="Boshqa", callback_data="time:other")
    builder.adjust(4, 4, 1)
    return builder.as_markup()
