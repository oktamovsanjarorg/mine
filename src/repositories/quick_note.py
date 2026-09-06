from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.quick_note import QuickNote

class QuickNoteRepository(BaseRepository[QuickNote]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, QuickNote)

    async def get_pinned(self, user_id: int) -> list[QuickNote]:
        stmt = select(QuickNote).where(
            QuickNote.user_id == user_id,
            QuickNote.is_pinned == True
        ).order_by(QuickNote.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent(self, user_id: int, limit: int = 15) -> list[QuickNote]:
        stmt = select(QuickNote).where(
            QuickNote.user_id == user_id
        ).order_by(QuickNote.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search(self, user_id: int, query: str, limit: int = 10) -> list[QuickNote]:
        stmt = select(QuickNote).where(
            QuickNote.user_id == user_id,
            QuickNote.content.ilike(f"%{query}%")
        ).order_by(QuickNote.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def toggle_pin(self, note_id: int) -> bool:
        note = await self.get_by_id(note_id)
        if note:
            note.is_pinned = not note.is_pinned
            await self.session.flush()
            return note.is_pinned
        return False
