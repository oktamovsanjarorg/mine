"""Statistics Repository for aggregating cross-module user statistics."""
from datetime import date, datetime
from typing import Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task
from src.models.habit import HabitLog, Habit
from src.models.finance import Transaction
from src.models.note import Note
from src.models.user import User


class StatsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_daily_stats(self, user_id: int, target_date: date) -> Dict[str, Any]:
        """Get user statistics for a given day."""
        # Completed tasks
        tasks_stmt = select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.status == "completed",
            func.date(Task.updated_at) == target_date
        )
        tasks_res = await self.session.execute(tasks_stmt)
        tasks_completed = tasks_res.scalar() or 0

        # Habits checked in
        habits_stmt = select(func.count(HabitLog.id)).join(Habit).where(
            Habit.user_id == user_id,
            HabitLog.date == target_date
        )
        habits_res = await self.session.execute(habits_stmt)
        habits_done = habits_res.scalar() or 0

        return {
            "tasks_completed": tasks_completed,
            "habits_done": habits_done,
            "date": target_date
        }

    async def get_global_stats(self) -> Dict[str, Any]:
        """Get system-wide total statistics."""
        users_cnt = (await self.session.execute(select(func.count(User.id)))).scalar() or 0
        tasks_cnt = (await self.session.execute(select(func.count(Task.id)))).scalar() or 0
        notes_cnt = (await self.session.execute(select(func.count(Note.id)))).scalar() or 0
        tx_cnt = (await self.session.execute(select(func.count(Transaction.id)))).scalar() or 0
        
        return {
            "total_users": users_cnt,
            "total_tasks": tasks_cnt,
            "total_notes": notes_cnt,
            "total_transactions": tx_cnt
        }

    async def calculate_productivity_score(self, user_id: int) -> int:
        """Calculate productivity score (0-100)."""
        stats = await self.get_daily_stats(user_id, date.today())
        score = (stats["tasks_completed"] * 25) + (stats["habits_done"] * 25)
        return min(max(score, 10), 100)

    async def get_activity_heatmap(self, user_id: int) -> Dict[date, int]:
        """Get daily activity count map."""
        today = date.today()
        daily = await self.get_daily_stats(user_id, today)
        return {today: daily["tasks_completed"] + daily["habits_done"]}
