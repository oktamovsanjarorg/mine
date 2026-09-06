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
            PomodoroSession.ended_at.is_(None)
        ).order_by(PomodoroSession.started_at.desc()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_active(self, user_id: int) -> PomodoroSession | None:
        return await self.get_active_session(user_id)

    async def get_all_active(self) -> list[PomodoroSession]:
        stmt = select(PomodoroSession).where(
            PomodoroSession.ended_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_today_sessions(self, user_id: int, target_date: date) -> list[PomodoroSession]:
        stmt = select(PomodoroSession).where(
            PomodoroSession.user_id == user_id,
            func.date(PomodoroSession.started_at) == target_date,
            PomodoroSession.ended_at.is_not(None)
        ).order_by(PomodoroSession.started_at.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_stats(self, user_id: int, date_from: datetime | None = None, date_to: datetime | None = None) -> dict:
        stmt = select(
            func.count(PomodoroSession.id),
            func.coalesce(func.sum(PomodoroSession.duration_minutes), 0)
        ).where(
            PomodoroSession.user_id == user_id,
            PomodoroSession.completed == True
        )
        if date_from:
            stmt = stmt.where(PomodoroSession.started_at >= date_from)
        if date_to:
            stmt = stmt.where(PomodoroSession.started_at <= date_to)

        result = await self.session.execute(stmt)
        row = result.first()
        count = row[0] if row else 0
        total_duration = row[1] if row else 0
        return {
            "session_count": count or 0,
            "total_duration": total_duration or 0,
            "completed_sessions": count or 0,
            "total_minutes": total_duration or 0
        }
