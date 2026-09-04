from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks.factory import GoalCB, GoalAction
from src.keyboards.builders import pagination_keyboard, back_button

def goal_list_keyboard(goals: list[tuple[int, str]], page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for goal_id, title in goals:
        builder.button(text=f"🎯 {title}", callback_data=GoalCB(action=GoalAction.DETAIL, id=goal_id).pack())
    
    builder.adjust(1)
    if total_pages > 1:
        pag_kb = pagination_keyboard(module="goals", current_page=page, total_pages=total_pages)
        for row in pag_kb.inline_keyboard:
            builder.row(*row)
            
    builder.row(back_button())
    return builder.as_markup()

def goal_detail_keyboard(goal_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📈 Progress qo'shish", callback_data=GoalCB(action=GoalAction.ADD_PROGRESS, id=goal_id).pack())
    builder.button(text="✏️ Tahrirlash", callback_data=GoalCB(action=GoalAction.EDIT, id=goal_id).pack())
    builder.button(text="🗑 O'chirish", callback_data=GoalCB(action=GoalAction.DELETE, id=goal_id).pack())
    builder.button(text="⬅️ Orqaga", callback_data=GoalCB(action=GoalAction.LIST, id=0).pack())
    builder.adjust(1, 2, 1)
    return builder.as_markup()
