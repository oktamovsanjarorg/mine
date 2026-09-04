from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import math
from typing import List, Any

class Paginator:
    """Paginator helper for Telegram bot pagination keyboards."""
    def __init__(self, items: List[Any], page: int, per_page: int, total: int):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total

    @property
    def total_pages(self) -> int:
        """Calculate the total number of pages."""
        return max(1, math.ceil(self.total / self.per_page))

    @property
    def has_next(self) -> bool:
        """Check if there is a next page."""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """Check if there is a previous page."""
        return self.page > 1

    def get_pagination_keyboard(self, callback_prefix: str, extra: str = '') -> InlineKeyboardMarkup | None:
        """Build the pagination inline keyboard markup."""
        if self.total_pages <= 1:
            return None

        builder = InlineKeyboardBuilder()
        extra_str = f":{extra}" if extra else ""
        
        if self.has_prev:
            builder.button(text="⬅️ Oldingi", callback_data=f"{callback_prefix}:{self.page - 1}{extra_str}")
            
        builder.button(text=f"{self.page}/{self.total_pages}", callback_data="ignore")
        
        if self.has_next:
            builder.button(text="Keyingi ➡️", callback_data=f"{callback_prefix}:{self.page + 1}{extra_str}")
            
        # Adjust layout based on presence of prev/next buttons
        builder.adjust(3 if self.has_prev and self.has_next else 2)
        return builder.as_markup()
