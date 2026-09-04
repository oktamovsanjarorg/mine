import structlog
from datetime import date
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.stats import StatsRepository

logger = structlog.get_logger(__name__)

class StatsService:
    """Service for generating statistics and reports."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = StatsRepository(session)

    async def generate_daily_digest(self, user_id: int) -> str:
        """Generate a daily digest message."""
        stats = await self.repo.get_daily_stats(user_id, date.today())
        tasks = stats.get('tasks_completed', 0)
        habits = stats.get('habits_done', 0)
        
        return f"📊 Bugungi hisobot:\n✅ Bajarilgan vazifalar: {tasks}\n🌱 Qilingan odatlar: {habits}\nBarakalla! Davom eting! 🚀"

    async def get_global_stats(self) -> Dict[str, Any]:
        """Get system global stats (for admin)."""
        return await self.repo.get_global_stats()

    async def productivity_score(self, user_id: int) -> int:
        """Calculate productivity score (0-100)."""
        return await self.repo.calculate_productivity_score(user_id)

    async def activity_heatmap(self, user_id: int) -> Dict[date, int]:
        """Get activity heatmap data."""
        return await self.repo.get_activity_heatmap(user_id)
