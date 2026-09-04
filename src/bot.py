"""Bot instance, dispatcher, and router setup."""
import structlog
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from src.config import settings

logger = structlog.get_logger()

def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

def create_dispatcher() -> Dispatcher:
    storage = RedisStorage.from_url(settings.redis_fsm_url)
    dp = Dispatcher(storage=storage)
    return dp

def register_routers(dp: Dispatcher) -> None:
    """Register all handler routers."""
    from src.handlers import guest, common, tasks, notes, reminders, finance, habits, health
    from src.handlers import journal, bookmarks, goals, flashcards, contacts, snippets
    from src.handlers import files, monitors, rss, pomodoro, ai_chat, quick_notes, tools
    from src.handlers import export as export_handler, admin

    routers = [
        guest.router,
        common.router, tasks.router, notes.router, reminders.router,
        finance.router, habits.router, health.router, journal.router,
        bookmarks.router, goals.router, flashcards.router, contacts.router,
        snippets.router, files.router, monitors.router, rss.router,
        pomodoro.router, ai_chat.router, quick_notes.router, tools.router,
        export_handler.router, admin.router,
    ]
    for r in routers:
        dp.include_router(r)
    logger.info('Routers registered', count=len(routers))

def register_middlewares(dp: Dispatcher) -> None:
    """Register all middlewares."""
    from src.core.database import session_factory
    from src.middlewares.database import DatabaseMiddleware
    from src.middlewares.auth import AuthMiddleware
    from src.middlewares.throttle import ThrottleMiddleware
    from src.middlewares.logging import LoggingMiddleware
    from src.middlewares.error_handler import ErrorHandlerMiddleware
    from src.middlewares.i18n import I18nMiddleware

    # Order matters: outer middleware runs first
    dp.update.outer_middleware(ErrorHandlerMiddleware())
    dp.update.outer_middleware(LoggingMiddleware())
    dp.update.middleware(DatabaseMiddleware(session_factory))
    dp.update.middleware(AuthMiddleware())
    dp.update.middleware(ThrottleMiddleware())
    dp.update.middleware(I18nMiddleware())
    logger.info('Middlewares registered')
