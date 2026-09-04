from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks.factory import TaskCB, TaskAction
from src.keyboards.builders import pagination_keyboard, back_button

def task_list_keyboard(tasks: list[tuple[int, str, bool]], page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for task_id, title, is_done in tasks:
        icon = "✅" if is_done else "⏳"
        builder.button(text=f"{icon} {title}", callback_data=TaskCB(action=TaskAction.DETAIL, id=task_id).pack())
    
    builder.adjust(1)
    
    if total_pages > 1:
        pag_kb = pagination_keyboard(module="tasks", current_page=page, total_pages=total_pages)
        for row in pag_kb.inline_keyboard:
            builder.row(*row)
            
    builder.row(back_button())
    return builder.as_markup()

def task_detail_keyboard(task_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Tahrirlash", callback_data=TaskCB(action=TaskAction.EDIT, id=task_id).pack())
    builder.button(text="✅ Bajarildi", callback_data=TaskCB(action=TaskAction.COMPLETE, id=task_id).pack())
    builder.button(text="🗑 O'chirish", callback_data=TaskCB(action=TaskAction.DELETE, id=task_id).pack())
    builder.button(text="⏰ Eslatma", callback_data=TaskCB(action=TaskAction.REMINDER, id=task_id).pack())
    builder.button(text="📎 Subtask", callback_data=TaskCB(action=TaskAction.SUBTASK, id=task_id).pack())
    builder.button(text="⬅️ Orqaga", callback_data=TaskCB(action=TaskAction.LIST, id=0).pack())
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()

def task_filter_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    filters = [
        ("📋 Hammasi", "all"), ("🔴 Muhim", "important"), 
        ("⏰ Bugungi", "today"), ("✅ Bajarilgan", "completed"), 
        ("📁 Kategoriya", "category")
    ]
    for text, f in filters:
        builder.button(text=text, callback_data=f"task_filter:{f}")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

def task_edit_keyboard(task_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    fields = [
        ("✏️ Nomi", "title"), ("📝 Tavsif", "desc"), 
        ("🔢 Muhimlik", "priority"), ("📅 Muddat", "deadline"), 
        ("📁 Kategoriya", "category")
    ]
    for text, field in fields:
        builder.button(text=text, callback_data=f"task_edit:{task_id}:{field}")
    builder.button(text="⬅️ Orqaga", callback_data=TaskCB(action=TaskAction.DETAIL, id=task_id).pack())
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()
