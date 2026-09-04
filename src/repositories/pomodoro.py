from datetime import date, datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.pomodoro import PomodoroSession

class PomodoroRepository(BaseRepository[PomodoroSession]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PomodoroSession)

    async def get_active_session(self, user_id: int) -> PomodoroSession | None:
        stmt = select(PomodoroSession).where(
            PomodoroSession.user_id == user_id,
            PomodoroSession.end_time.is_(None)
        ).order_by(PomodoroSession.start_time.desc()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_today_sessions(self, user_id: int, target_date: date) -> list[PomodoroSession]:
        stmt = select(PomodoroSession).where(
            PomodoroSession.user_id == user_id,
            func.date(PomodoroSession.start_time) == target_date,
            PomodoroSession.end_time.is_not(None)
        ).order_by(PomodoroSession.start_time.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_stats(self, user_id: int, date_from: datetime, date_to: datetime) -> dict:
        stmt = select(func.count(PomodoroSession.id), func.sum(PomodoroSession.duration)).where(
            PomodoroSession.user_id == user_id,
            PomodoroSession.start_time >= date_from,
            PomodoroSession.start_time <= date_to,
            PomodoroSession.end_time.is_not(None)
        )
        result = await self.session.execute(stmt)
        count, total_duration = result.first() or (0, 0)
        return {
            "session_count": count or 0,
            "total_duration": total_duration or 0
        }
