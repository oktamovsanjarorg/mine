from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher
from src.api.routes import router as api_router
from src.config import settings
import structlog

logger = structlog.get_logger(__name__)

def create_app(bot: Bot, dp: Dispatcher) -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="SanjarBot API",
        description="API for SanjarBot Telegram Bot",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )

    # State
    app.state.bot = bot
    app.state.dp = dp

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(api_router)

    @app.on_event("startup")
    async def on_startup():
        logger.info("FastAPI starting up", webhook_url=settings.WEBHOOK_URL)
        if settings.USE_WEBHOOK:
            await bot.set_webhook(
                url=settings.WEBHOOK_URL,
                drop_pending_updates=True,
                secret_token=settings.WEBHOOK_SECRET
            )

    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info("FastAPI shutting down")
        if settings.USE_WEBHOOK:
            await bot.delete_webhook()

    return app
