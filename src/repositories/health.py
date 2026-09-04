from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.health import HealthLog

class HealthRepository(BaseRepository[HealthLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, HealthLog)

    async def get_by_type_and_date(self, user_id: int, type_: str, target_date: date) -> list[HealthLog]:
        stmt = select(HealthLog).where(
            HealthLog.user_id == user_id,
            HealthLog.type == type_,
            func.date(HealthLog.logged_at) == target_date
        ).order_by(HealthLog.logged_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_today_water(self, user_id: int, target_date: date) -> int:
        stmt = select(func.sum(HealthLog.value)).where(
            HealthLog.user_id == user_id,
            HealthLog.type == 'water',
            func.date(HealthLog.logged_at) == target_date
        )
        result = await self.session.execute(stmt)
        return int(result.scalar() or 0)

    async def get_range(self, user_id: int, type_: str, date_from: date, date_to: date) -> list[HealthLog]:
        stmt = select(HealthLog).where(
            HealthLog.user_id == user_id,
            HealthLog.type == type_,
            func.date(HealthLog.logged_at) >= date_from,
            func.date(HealthLog.logged_at) <= date_to
        ).order_by(HealthLog.logged_at.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest(self, user_id: int, type_: str) -> HealthLog | None:
        stmt = select(HealthLog).where(
            HealthLog.user_id == user_id,
            HealthLog.type == type_
        ).order_by(HealthLog.logged_at.desc()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()
