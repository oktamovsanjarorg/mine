from aiogram import Router

from .guest import router as guest_router
from .common import router as common_router
from .tasks import router as tasks_router
from .notes import router as notes_router
from .reminders import router as reminders_router
from .finance import router as finance_router
from .habits import router as habits_router
from .health import router as health_router
from .journal import router as journal_router
from .bookmarks import router as bookmarks_router
from .goals import router as goals_router
from .flashcards import router as flashcards_router
from .contacts import router as contacts_router
from .snippets import router as snippets_router
from .files import router as files_router
from .monitors import router as monitors_router
from .rss import router as rss_router
from .pomodoro import router as pomodoro_router
from .ai_chat import router as ai_chat_router
from .quick_notes import router as quick_notes_router
from .tools import router as tools_router
from .export import router as export_router
from .admin import router as admin_router


def setup_handlers() -> Router:
    """Register all routers and return the main router."""
    main_router = Router()
    
    main_router.include_routers(
        guest_router,
        common_router,
        tasks_router,
        notes_router,
        reminders_router,
        finance_router,
        habits_router,
        health_router,
        journal_router,
        bookmarks_router,
        goals_router,
        flashcards_router,
        contacts_router,
        snippets_router,
        files_router,
        monitors_router,
        rss_router,
        pomodoro_router,
        ai_chat_router,
        quick_notes_router,
        tools_router,
        export_router,
        admin_router,
    )
    
    return main_router
