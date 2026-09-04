from fastapi import APIRouter, Request, Depends, BackgroundTasks
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from src.config import settings
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter()

def get_bot(request: Request) -> Bot:
    return request.app.state.bot

def get_dp(request: Request) -> Dispatcher:
    return request.app.state.dp

@router.post(settings.WEBHOOK_PATH)
async def bot_webhook(
    update_data: dict,
    bot: Bot = Depends(get_bot),
    dp: Dispatcher = Depends(get_dp)
):
    """Receive Telegram Webhook."""
    try:
        update = Update(**update_data)
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        logger.error("Failed to process webhook update", error=str(e))
        return {"status": "error", "message": str(e)}

@router.get(settings.WEBHOOK_PATH)
async def check_webhook():
    return {"status": "Webhook endpoint is active."}
