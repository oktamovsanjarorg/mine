from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks.factory import NoteCB, NoteAction
from src.keyboards.builders import pagination_keyboard, back_button

def note_list_keyboard(notes: list[tuple[int, str, bool]], page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for note_id, title, is_pinned in notes:
        icon = "📌" if is_pinned else "📝"
        builder.button(text=f"{icon} {title}", callback_data=NoteCB(action=NoteAction.DETAIL, id=note_id).pack())
    
    builder.adjust(1)
    
    if total_pages > 1:
        pag_kb = pagination_keyboard(module="notes", current_page=page, total_pages=total_pages)
        for row in pag_kb.inline_keyboard:
            builder.row(*row)
            
    builder.row(back_button())
    return builder.as_markup()

def note_detail_keyboard(note_id: int, is_pinned: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    pin_text = "📍 Unpin" if is_pinned else "📌 Pin"
    builder.button(text="✏️ Tahrirlash", callback_data=NoteCB(action=NoteAction.EDIT, id=note_id).pack())
    builder.button(text=pin_text, callback_data=NoteCB(action=NoteAction.TOGGLE_PIN, id=note_id).pack())
    builder.button(text="🗑 O'chirish", callback_data=NoteCB(action=NoteAction.DELETE, id=note_id).pack())
    builder.button(text="⬅️ Orqaga", callback_data=NoteCB(action=NoteAction.LIST, id=0).pack())
    builder.adjust(2, 1, 1)
    return builder.as_markup()

def note_filter_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    filters = [
        ("📋 Hammasi", "all"), ("📌 Pinned", "pinned"), 
        ("📁 Kategoriya", "category"), ("🏷 Tag", "tag")
    ]
    for text, f in filters:
        builder.button(text=text, callback_data=f"note_filter:{f}")
    builder.adjust(2)
    return builder.as_markup()
