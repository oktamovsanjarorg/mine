"""Bot entry point — python -m src"""
import asyncio
import structlog
from aiogram import Bot, Dispatcher
from src.bot import create_bot, create_dispatcher, register_routers, register_middlewares
from src.core.database import init_db, close_db
from src.core.redis import create_redis_pool, close_redis
from src.core.storage import init_storage, close_storage
from src.core.scheduler import init_scheduler, shutdown_scheduler
from src.config import settings

logger = structlog.get_logger()


async def on_startup(dispatcher: Dispatcher, bot: Bot) -> None:
    """Startup hook."""
    await init_db()
    await create_redis_pool()
    try:
        await init_storage()
    except Exception as e:
        logger.warning("MinIO storage init warning", error=str(e))
    scheduler = init_scheduler()
    
    # 1. Automated Reminders Worker (every 30 seconds)
    async def check_due_reminders():
        from src.core.database import session_factory
        from src.repositories.reminder import ReminderRepository
        from datetime import datetime, timezone, timedelta
        if not session_factory:
            return
        try:
            async with session_factory() as session:
                repo = ReminderRepository(session)
                now = datetime.now(timezone.utc)
                due_reminders = await repo.get_due_reminders(before=now)
                for rem in due_reminders:
                    try:
                        await bot.send_message(
                            chat_id=rem.user_id,
                            text=(
                                f"⏰ <b>ESLATMA VAQTI KELDI!</b>\n\n"
                                f"📌 <b>{rem.title}</b>\n"
                                f"🕒 Belgilangan vaqt: {rem.remind_at.strftime('%Y-%m-%d %H:%M')}"
                            ),
                            parse_mode="HTML"
                        )
                        if str(rem.repeat_type) in ("daily", "DAILY"):
                            rem.remind_at = rem.remind_at + timedelta(days=1)
                        elif str(rem.repeat_type) in ("weekly", "WEEKLY"):
                            rem.remind_at = rem.remind_at + timedelta(weeks=1)
                        else:
                            rem.is_active = False
                        rem.last_triggered_at = now
                        await session.flush()
                    except Exception as e:
                        logger.error("Failed to deliver reminder", reminder_id=rem.id, error=str(e))
                await session.commit()
        except Exception as e:
            logger.error("Error in reminder worker", error=str(e))

    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    scheduler.add_job(check_due_reminders, IntervalTrigger(seconds=30), id="reminder_worker", replace_existing=True)

    # 2. 10-degree sharp weather alert (daily at 20:00)
    async def daily_weather_check():
        from src.integrations.weather import weather_client
        from src.handlers.guest import OWNER_ID
        should_alert, alert_msg = await weather_client.check_temperature_difference("Tashkent", threshold=10.0)
        if should_alert:
            try:
                await bot.send_message(chat_id=OWNER_ID, text=alert_msg)
            except Exception as e:
                logger.error("Failed to send weather alert", error=str(e))

    scheduler.add_job(daily_weather_check, CronTrigger(hour=20, minute=0, timezone="Asia/Tashkent"), id="weather_alert", replace_existing=True)


    register_middlewares(dispatcher)
    register_routers(dispatcher)
    logger.info("Bot started successfully", mode=settings.bot_mode)


async def on_shutdown(dispatcher: Dispatcher, bot: Bot) -> None:
    """Shutdown hook."""
    shutdown_scheduler()
    await close_storage()
    await close_redis()
    await close_db()
    logger.info("Bot shutdown complete")


async def main() -> None:
    """Main application loop."""
    structlog.configure(
        processors=[structlog.dev.ConsoleRenderer()] if settings.log_level == 'DEBUG' 
        else [structlog.processors.JSONRenderer()],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(structlog, settings.log_level, 20)),
    )
    
    bot = create_bot()
    dp = create_dispatcher()
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    if settings.bot_mode == 'webhook':
        from src.api.app import create_app
        import uvicorn
        app = create_app(bot, dp)
        config = uvicorn.Config(app, host='0.0.0.0', port=8000)
        server = uvicorn.Server(config)
        await server.serve()
    else:
        try:
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        finally:
            await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
