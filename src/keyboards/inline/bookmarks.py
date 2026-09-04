from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks.factory import BookmarkCB, BookmarkAction
from src.keyboards.builders import pagination_keyboard, back_button

def bookmark_list_keyboard(bookmarks: list[tuple[int, str]], page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for bm_id, title in bookmarks:
        builder.button(text=f"🔖 {title}", callback_data=BookmarkCB(action=BookmarkAction.DETAIL, id=bm_id).pack())
    
    builder.adjust(1)
    if total_pages > 1:
        pag_kb = pagination_keyboard(module="bookmarks", current_page=page, total_pages=total_pages)
        for row in pag_kb.inline_keyboard:
            builder.row(*row)
            
    builder.row(back_button())
    return builder.as_markup()

def bookmark_detail_keyboard(bm_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 Ochish", callback_data=BookmarkCB(action=BookmarkAction.OPEN, id=bm_id).pack())
    builder.button(text="✏️ Tahrirlash", callback_data=BookmarkCB(action=BookmarkAction.EDIT, id=bm_id).pack())
    builder.button(text="🗑 O'chirish", callback_data=BookmarkCB(action=BookmarkAction.DELETE, id=bm_id).pack())
    builder.button(text="⬅️ Orqaga", callback_data=BookmarkCB(action=BookmarkAction.LIST, id=0).pack())
    builder.adjust(2, 1, 1)
    return builder.as_markup()

def bookmark_filter_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    filters = [("📋 Hammasi", "all"), ("📁 Kategoriya", "category"), ("🏷 Tag", "tag")]
    for text, f in filters:
        builder.button(text=text, callback_data=f"bookmark_filter:{f}")
    builder.adjust(2, 1)
    return builder.as_markup()
