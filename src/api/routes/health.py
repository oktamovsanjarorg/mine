from fastapi import APIRouter, Depends
from sqlalchemy import text
from src.api.dependencies import DbSession
from src.db.redis import get_redis
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check(session: DbSession):
    """Check health of dependent services (DB, Redis)."""
    status = {
        "status": "ok",
        "db": "unknown",
        "redis": "unknown"
    }
    
    # Check DB
    try:
        await session.execute(text("SELECT 1"))
        status["db"] = "ok"
    except Exception as e:
        logger.error("Health DB check failed", error=str(e))
        status["db"] = "error"
        status["status"] = "degraded"

    # Check Redis
    try:
        redis = await get_redis()
        await redis.ping()
        status["redis"] = "ok"
    except Exception as e:
        logger.error("Health Redis check failed", error=str(e))
        status["redis"] = "error"
        status["status"] = "degraded"
        
    return status
