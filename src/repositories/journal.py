from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.journal import JournalEntry

class JournalRepository(BaseRepository[JournalEntry]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, JournalEntry)

    async def get_by_date(self, user_id: int, target_date: date) -> JournalEntry | None:
        stmt = select(JournalEntry).where(
            JournalEntry.user_id == user_id,
            JournalEntry.date == target_date,
            JournalEntry.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_mood_data(self, user_id: int, date_from: date, date_to: date) -> list[dict]:
        stmt = select(JournalEntry.date, JournalEntry.mood).where(
            JournalEntry.user_id == user_id,
            JournalEntry.is_deleted == False,
            JournalEntry.date >= date_from,
            JournalEntry.date <= date_to,
            JournalEntry.mood.is_not(None)
        ).order_by(JournalEntry.date.asc())
        result = await self.session.execute(stmt)
        return [{"date": row[0], "mood": row[1]} for row in result.all()]

    async def toggle_favorite(self, user_id: int, target_date: date) -> JournalEntry | None:
        entry = await self.get_by_date(user_id, target_date)
        if entry:
            entry.is_favorite = not entry.is_favorite
            await self.session.flush()
            await self.session.refresh(entry)
            return entry
        return None
