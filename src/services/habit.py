import structlog
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.habit import HabitRepository
from src.models.habit import Habit, HabitLog

logger = structlog.get_logger(__name__)

class HabitService:
    """Service for managing habits."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = HabitRepository(session)

    async def create_habit(self, user_id: int, title: str, frequency: str = "daily") -> Habit:
        """Create a new habit."""
        try:
            habit = await self.repo.create(
                user_id=user_id,
                title=title,
                frequency=frequency,
                current_streak=0,
                longest_streak=0
            )
            await self.session.commit()
            return habit
        except Exception as e:
            await self.session.rollback()
            logger.error("Odat yaratishda xatolik", error=str(e))
            raise

    async def check_in(self, habit_id: int) -> HabitLog:
        """Check in a habit for today."""
        habit = await self.repo.get_by_id(habit_id)
        if not habit:
            raise ValueError("Odat topilmadi")
            
        log = await self.repo.create_log(habit_id=habit_id, date=date.today())
        await self.update_streaks(habit_id)
        await self.session.commit()
        return log

    async def undo_check_in(self, habit_id: int) -> bool:
        """Undo a habit check in for today."""
        result = await self.repo.delete_log_for_date(habit_id, date.today())
        await self.update_streaks(habit_id)
        await self.session.commit()
        return result

    async def get_today_status(self, user_id: int) -> List[Dict[str, Any]]:
        """Get today's habit status."""
        habits = await self.repo.get_by_user_id(user_id)
        status = []
        for h in habits:
            is_done = await self.repo.is_checked_in_today(h.id)
            status.append({"habit": h, "is_done": is_done})
        return status

    async def update_streaks(self, habit_id: int) -> None:
        """Update current and longest streaks for a habit."""
        streak = await self.repo.calculate_streak(habit_id)
        habit = await self.repo.get_by_id(habit_id)
        longest = max(streak, habit.longest_streak) if habit else streak
        await self.repo.update(habit_id, current_streak=streak, longest_streak=longest)

    async def streak_milestone_notifications(self, user_id: int) -> List[str]:
        """Check for streak milestones and return notifications."""
        habits = await self.repo.get_by_user_id(user_id)
        notifications = []
        for h in habits:
            if h.current_streak in [7, 30, 100, 365]:
                notifications.append(f"🎉 Tabriklaymiz! '{h.title}' odati bo'yicha {h.current_streak} kunlik seriya!")
        return notifications

    async def weekly_reports(self, user_id: int) -> Dict[str, Any]:
        """Generate weekly habit report."""
        return await self.repo.get_weekly_report(user_id)
        
    async def monthly_reports(self, user_id: int) -> Dict[str, Any]:
        """Generate monthly habit report."""
        return await self.repo.get_monthly_report(user_id)

    async def heatmap_data(self, user_id: int) -> Dict[date, int]:
        """Get heatmap data for habits."""
        return await self.repo.get_heatmap_data(user_id)
