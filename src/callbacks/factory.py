from aiogram.filters.callback_data import CallbackData

class TaskCB(CallbackData, prefix='task'):
    """Task callback data factory."""
    action: str  # list, view, create, edit, delete, complete, subtask, category
    id: int = 0
    page: int = 1
    status: str = ''
    priority: int = 0

class NoteCB(CallbackData, prefix='note'):
    """Note callback data factory."""
    action: str
    id: int = 0
    page: int = 1

class FinanceCB(CallbackData, prefix='fin'):
    """Finance callback data factory."""
    action: str
    id: int = 0
    page: int = 1
    period: str = ''

class HabitCB(CallbackData, prefix='habit'):
    """Habit callback data factory."""
    action: str
    id: int = 0

class HealthCB(CallbackData, prefix='health'):
    """Health callback data factory."""
    action: str
    id: int = 0
    log_type: str = ''

class JournalCB(CallbackData, prefix='journal'):
    """Journal callback data factory."""
    action: str
    date: str = ''

class BookmarkCB(CallbackData, prefix='bm'):
    """Bookmark callback data factory."""
    action: str
    id: int = 0
    page: int = 1

class GoalCB(CallbackData, prefix='goal'):
    """Goal callback data factory."""
    action: str
    id: int = 0

class FlashcardCB(CallbackData, prefix='fc'):
    """Flashcard callback data factory."""
    action: str
    deck_id: int = 0
    card_id: int = 0
    quality: int = 0

class ContactCB(CallbackData, prefix='contact'):
    """Contact callback data factory."""
    action: str
    id: int = 0
    page: int = 1

class SnippetCB(CallbackData, prefix='snip'):
    """Snippet callback data factory."""
    action: str
    id: int = 0
    page: int = 1
    lang: str = ''

class FileCB(CallbackData, prefix='file'):
    """File callback data factory."""
    action: str
    id: int = 0
    page: int = 1
    file_type: str = ''

class MonitorCB(CallbackData, prefix='mon'):
    """Monitor callback data factory."""
    action: str
    id: int = 0

class RSSCB(CallbackData, prefix='rss'):
    """RSS callback data factory."""
    action: str
    feed_id: int = 0
    item_id: int = 0
    page: int = 1

class PomodoroCB(CallbackData, prefix='pomo'):
    """Pomodoro callback data factory."""
    action: str
    session_id: int = 0
    pomo_type: str = ''

class AIChatCB(CallbackData, prefix='ai'):
    """AI Chat callback data factory."""
    action: str
    conv_id: int = 0

class MenuCB(CallbackData, prefix='menu'):
    """Menu callback data factory."""
    action: str

class PaginationCB(CallbackData, prefix='page'):
    """Pagination callback data factory."""
    module: str
    page: int = 1
    extra: str = ''

class ConfirmCB(CallbackData, prefix='confirm'):
    """Confirmation callback data factory."""
    action: str  # yes, no
    target: str
    id: int = 0

class SettingsCB(CallbackData, prefix='set'):
    """Settings callback data factory."""
    action: str
    value: str = ''

class CategoryCB(CallbackData, prefix='cat'):
    """Category callback data factory."""
    action: str
    id: int = 0
    cat_type: str = ''
