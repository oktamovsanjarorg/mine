from typing import Sequence
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.note import Note

class NoteRepository(BaseRepository[Note]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Note)

    async def get_by_user_id(self, user_id: int, limit: int = 100, offset: int = 0) -> Sequence[Note]:
        return await self.get_all(user_id=user_id, offset=offset, limit=limit)

    async def search(self, user_id: int, query: str) -> Sequence[Note]:
        from sqlalchemy import or_
        stmt = select(Note).where(
            Note.user_id == user_id,
            Note.is_deleted == False,
            or_(Note.title.ilike(f"%{query}%"), Note.content.ilike(f"%{query}%"))
        ).order_by(Note.created_at.desc())
        res = await self.session.execute(stmt)
        return res.scalars().all()


    async def get_pinned(self, user_id: int) -> list[Note]:
        stmt = select(Note).where(
            Note.user_id == user_id,
            Note.is_pinned == True,
            Note.is_deleted == False
        ).order_by(Note.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_archived(self, user_id: int, offset: int = 0, limit: int = 10) -> Sequence[Note]:
        stmt = select(Note).where(
            Note.user_id == user_id,
            Note.is_archived == True,
            Note.is_deleted == False
        ).order_by(Note.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search_fulltext(self, user_id: int, query: str, offset: int = 0, limit: int = 10) -> Sequence[Note]:
        # Using PostgreSQL to_tsvector for full-text search
        stmt = select(Note).where(
            Note.user_id == user_id,
            Note.is_deleted == False,
            text("to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', :query)")
        ).params(query=query).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def pin_note(self, user_id: int, note_id: int) -> Note | None:
        note = await self.get_by_id(note_id)
        if note and note.user_id == user_id:
            note.is_pinned = True
            await self.session.flush()
            await self.session.refresh(note)
            return note
        return None

    async def unpin_note(self, user_id: int, note_id: int) -> Note | None:
        note = await self.get_by_id(note_id)
        if note and note.user_id == user_id:
            note.is_pinned = False
            await self.session.flush()
            await self.session.refresh(note)
            return note
        return None

    async def archive_note(self, user_id: int, note_id: int) -> Note | None:
        note = await self.get_by_id(note_id)
        if note and note.user_id == user_id:
            note.is_archived = True
            await self.session.flush()
            await self.session.refresh(note)
            return note
        return None
