from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks.factory import AIChatCB, AIChatAction
from src.keyboards.builders import pagination_keyboard, back_button

def ai_conversations_keyboard(conversations: list[tuple[int, str]], page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for conv_id, title in conversations:
        builder.button(text=f"💬 {title}", callback_data=AIChatCB(action=AIChatAction.SELECT_CHAT, id=conv_id).pack())
    
    builder.button(text="➕ Yangi Chat", callback_data=AIChatCB(action=AIChatAction.NEW_CHAT, id=0).pack())
    builder.adjust(1)
    
    if total_pages > 1:
        pag_kb = pagination_keyboard(module="ai_chats", current_page=page, total_pages=total_pages)
        for row in pag_kb.inline_keyboard:
            builder.row(*row)
            
    builder.row(back_button())
    return builder.as_markup()

def ai_chat_settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🤖 Modelni o'zgartirish", callback_data=AIChatCB(action=AIChatAction.SETTINGS, id=0).pack())
    builder.button(text="⬅️ Orqaga", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()
