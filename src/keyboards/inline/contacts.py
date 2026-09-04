from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks.factory import ContactCB, ContactAction
from src.keyboards.builders import pagination_keyboard, back_button

def contact_list_keyboard(contacts: list[tuple[int, str]], page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for contact_id, name in contacts:
        builder.button(text=f"👤 {name}", callback_data=ContactCB(action=ContactAction.DETAIL, id=contact_id).pack())
    
    builder.adjust(1)
    if total_pages > 1:
        pag_kb = pagination_keyboard(module="contacts", current_page=page, total_pages=total_pages)
        for row in pag_kb.inline_keyboard:
            builder.row(*row)
            
    builder.row(back_button())
    return builder.as_markup()

def contact_detail_keyboard(contact_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Tahrirlash", callback_data=ContactCB(action=ContactAction.EDIT, id=contact_id).pack())
    builder.button(text="🗑 O'chirish", callback_data=ContactCB(action=ContactAction.DELETE, id=contact_id).pack())
    builder.button(text="⬅️ Orqaga", callback_data=ContactCB(action=ContactAction.LIST, id=0).pack())
    builder.adjust(2, 1)
    return builder.as_markup()

def birthdays_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎂 Tug'ilgan kunlar", callback_data=ContactCB(action=ContactAction.BIRTHDAYS, id=0).pack())
    return builder.as_markup()
