from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any
from aiogram import Bot
from sqlalchemy import select, func
from src.api.dependencies import DbSession, ApiKey
from src.db.models import User
import structlog
import asyncio

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])

class BroadcastMessage(BaseModel):
    text: str
    user_ids: List[int] = []

def get_bot(request: Request) -> Bot:
    return request.app.state.bot

@router.get("/stats", dependencies=[Depends(ApiKey)])
async def get_stats(session: DbSession) -> Dict[str, Any]:
    """Get bot statistics."""
    try:
        user_count = await session.scalar(select(func.count(User.id)))
        active_users = await session.scalar(select(func.count(User.id)).where(User.is_active == True))
        
        return {
            "total_users": user_count or 0,
            "active_users": active_users or 0
        }
    except Exception as e:
        logger.error("Admin get_stats failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/broadcast", dependencies=[Depends(ApiKey)])
async def broadcast_message(
    message: BroadcastMessage,
    session: DbSession,
    bot: Bot = Depends(get_bot)
) -> Dict[str, Any]:
    """Broadcast a message to users."""
    try:
        target_users = message.user_ids
        if not target_users:
            # Broadcast to all active users
            result = await session.execute(select(User.telegram_id).where(User.is_active == True))
            target_users = [row[0] for row in result.all()]
        
        success_count = 0
        for user_id in target_users:
            try:
                await bot.send_message(user_id, message.text)
                success_count += 1
                await asyncio.sleep(0.05) # Rate limit protection
            except Exception as e:
                logger.warning("Broadcast failed for user", user_id=user_id, error=str(e))
                
        return {"status": "ok", "sent": success_count, "total": len(target_users)}
    except Exception as e:
        logger.error("Admin broadcast failed", error=str(e))
        raise HTTPException(status_code=500, detail="Broadcast failed")
