from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from src.callbacks.factory import ConfirmCB, PaginationCB, MenuCB

def build_inline_keyboard(buttons: list[list[tuple[str, str]]], row_width: int = 2) -> InlineKeyboardMarkup:
    """Build inline keyboard from list of (text, callback_data) tuples."""
    builder = InlineKeyboardBuilder()
    for row in buttons:
        for text, callback_data in row:
            builder.button(text=text, callback_data=callback_data)
    builder.adjust(row_width)
    return builder.as_markup()

def build_reply_keyboard(buttons: list[list[str]], resize: bool = True, one_time: bool = False) -> ReplyKeyboardMarkup:
    """Build reply keyboard from list of button texts."""
    builder = ReplyKeyboardBuilder()
    for row in buttons:
        for text in row:
            builder.button(text=text)
    builder.adjust(len(buttons[0]) if buttons else 1)
    return builder.as_markup(resize_keyboard=resize, one_time_keyboard=one_time)

def back_button(callback_data: str = 'menu:main') -> InlineKeyboardButton:
    return InlineKeyboardButton(text='⬅️ Orqaga', callback_data=callback_data)

def cancel_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text='❌ Bekor qilish', callback_data='menu:cancel')

def confirm_keyboard(target: str, id: int = 0) -> InlineKeyboardMarkup:
    """Tasdiqlash/bekor qilish keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text='✅ Ha', callback_data=ConfirmCB(target=target, id=id, confirm=True))
    builder.button(text='❌ Yo\'q', callback_data=ConfirmCB(target=target, id=id, confirm=False))
    return builder.as_markup()

def pagination_keyboard(module: str, current_page: int, total_pages: int, extra: str = '') -> InlineKeyboardMarkup:
    """Pagination keyboard: ◀️ page/total ▶️"""
    builder = InlineKeyboardBuilder()
    if current_page > 1:
        builder.button(text='◀️', callback_data=PaginationCB(module=module, page=current_page - 1, extra=extra))
    else:
        builder.button(text=' ', callback_data='ignore')
        
    builder.button(text=f'{current_page}/{total_pages}', callback_data='ignore')
    
    if current_page < total_pages:
        builder.button(text='▶️', callback_data=PaginationCB(module=module, page=current_page + 1, extra=extra))
    else:
        builder.button(text=' ', callback_data='ignore')
    
    builder.adjust(3)
    return builder.as_markup()
