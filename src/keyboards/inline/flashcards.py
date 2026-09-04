from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks.factory import FlashcardCB, FlashcardAction
from src.keyboards.builders import pagination_keyboard, back_button

def deck_list_keyboard(decks: list[tuple[int, str]], page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for deck_id, title in decks:
        builder.button(text=f"📚 {title}", callback_data=FlashcardCB(action=FlashcardAction.DECK_DETAIL, id=deck_id).pack())
    
    builder.adjust(1)
    if total_pages > 1:
        pag_kb = pagination_keyboard(module="decks", current_page=page, total_pages=total_pages)
        for row in pag_kb.inline_keyboard:
            builder.row(*row)
            
    builder.row(back_button())
    return builder.as_markup()

def study_keyboard(card_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👀 Javobni ko'rish", callback_data=FlashcardCB(action=FlashcardAction.SHOW_ANSWER, id=card_id).pack())
    builder.button(text="⏹ To'xtatish", callback_data=FlashcardCB(action=FlashcardAction.LIST_DECKS, id=0).pack())
    builder.adjust(1)
    return builder.as_markup()

def review_quality_keyboard(card_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    qualities = [("🔴 Qiyin", 1), ("🟡 O'rtacha", 3), ("🟢 Oson", 4), ("⭐ Juda oson", 5)]
    for text, q in qualities:
        builder.button(text=text, callback_data=f"fc_review:{card_id}:{q}")
    builder.adjust(2, 2)
    return builder.as_markup()
