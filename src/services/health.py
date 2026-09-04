import structlog
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.health import HealthRepository
from src.models.health import HealthLog

logger = structlog.get_logger(__name__)

class HealthService:
    """Service for managing health logs."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = HealthRepository(session)

    async def log_health(self, user_id: int, metric_type: str, value: float, notes: Optional[str] = None) -> HealthLog:
        """Log health metric (water/sleep/weight/exercise)."""
        try:
            log = await self.repo.create(
                user_id=user_id,
                metric_type=metric_type,
                value=value,
                notes=notes,
                date=date.today()
            )
            await self.session.commit()
            return log
        except Exception as e:
            await self.session.rollback()
            logger.error("Salomatlik ma'lumotini saqlashda xatolik", error=str(e))
            raise

    async def get_today_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary of today's health logs."""
        return await self.repo.get_summary(user_id, date.today())

    async def get_trend(self, user_id: int, metric_type: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get health trend for a metric."""
        return await self.repo.get_trend(user_id, metric_type, days)

    async def water_progress(self, user_id: int) -> Dict[str, Any]:
        """Get water intake progress."""
        today = date.today()
        logs = await self.repo.get_logs_by_date_and_type(user_id, today, "water")
        total = sum(log.value for log in logs)
        return {"current": total, "target": 2000, "unit": "ml"} # Default target 2L

    async def sleep_stats(self, user_id: int) -> Dict[str, Any]:
        """Get sleep statistics."""
        return await self.repo.get_stats(user_id, "sleep")

    async def exercise_stats(self, user_id: int) -> Dict[str, Any]:
        """Get exercise statistics."""
        return await self.repo.get_stats(user_id, "exercise")
