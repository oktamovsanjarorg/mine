"""Bot entry point — python -m src"""
import asyncio
import structlog
from src.bot import create_bot, create_dispatcher, register_routers, register_middlewares
from src.core.database import init_db, close_db
from src.core.redis import create_redis_pool, close_redis
from src.core.storage import init_storage, close_storage
from src.core.scheduler import init_scheduler, shutdown_scheduler
from src.config import settings

logger = structlog.get_logger()

async def on_startup(bot, dp):
    await init_db()
    await create_redis_pool()
    await init_storage()
    scheduler = await init_scheduler()
    scheduler.start()
    register_middlewares(dp)
    register_routers(dp)
    # Load active reminders, schedule recurring jobs
    logger.info('Bot started successfully', mode=settings.bot_mode)

async def on_shutdown(bot, dp):
    await shutdown_scheduler()
    await close_storage()
    await close_redis()
    await close_db()
    logger.info('Bot shutdown complete')

async def main():
    # Configure structlog
    structlog.configure(
        processors=[structlog.dev.ConsoleRenderer()] if settings.log_level == 'DEBUG' 
        else [structlog.processors.JSONRenderer()],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(structlog, settings.log_level, 20)),
    )
    
    bot = create_bot()
    dp = create_dispatcher()
    
    dp.startup.register(lambda: on_startup(bot, dp))
    dp.shutdown.register(lambda: on_shutdown(bot, dp))
    
    if settings.bot_mode == 'webhook':
        # FastAPI webhook mode
        from src.api.app import create_app
        import uvicorn
        app = create_app(bot, dp)
        config = uvicorn.Config(app, host='0.0.0.0', port=8000)
        server = uvicorn.Server(config)
        await server.serve()
    else:
        # Polling mode
        try:
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        finally:
            await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
