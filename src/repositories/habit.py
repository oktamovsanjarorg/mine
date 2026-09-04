from typing import Sequence
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.habit import Habit, HabitLog

class HabitRepository(BaseRepository[Habit]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Habit)

    async def get_active_habits(self, user_id: int) -> list[Habit]:
        stmt = select(Habit).where(
            Habit.user_id == user_id,
            Habit.is_active == True,
            Habit.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_today_logs(self, user_id: int, habit_id: int, target_date: date) -> HabitLog | None:
        stmt = select(HabitLog).join(Habit).where(
            Habit.user_id == user_id,
            HabitLog.habit_id == habit_id,
            HabitLog.date == target_date
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def check_in(self, habit_id: int, target_date: date, count: int, note: str | None) -> HabitLog:
        stmt = select(HabitLog).where(
            HabitLog.habit_id == habit_id,
            HabitLog.date == target_date
        )
        result = await self.session.execute(stmt)
        log = result.scalars().first()
        
        if log:
            log.count = count
            log.note = note
        else:
            log = HabitLog(habit_id=habit_id, date=target_date, count=count, note=note)
            self.session.add(log)
            
        await self.session.flush()
        await self.session.refresh(log)
        return log

    async def get_logs_range(self, habit_id: int, date_from: date, date_to: date) -> list[HabitLog]:
        stmt = select(HabitLog).where(
            HabitLog.habit_id == habit_id,
            HabitLog.date >= date_from,
            HabitLog.date <= date_to
        ).order_by(HabitLog.date.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_streak(self, habit_id: int, current_streak: int, best_streak: int, total_completions: int) -> None:
        habit = await self.get_by_id(habit_id)
        if habit:
            habit.current_streak = current_streak
            habit.best_streak = best_streak
            habit.total_completions = total_completions
            await self.session.flush()
