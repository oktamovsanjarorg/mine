import structlog
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.note import NoteRepository
from src.models.note import Note

logger = structlog.get_logger(__name__)

class NoteService:
    """Service for managing notes."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = NoteRepository(session)

    async def create_note(self, user_id: int, title: str, content: str) -> Note:
        """Create a new note."""
        try:
            note = await self.repo.create(
                user_id=user_id,
                title=title,
                content=content,
                is_pinned=False,
                is_archived=False
            )
            await self.session.commit()
            logger.info("Eslatma yaratildi", note_id=note.id, user_id=user_id)
            return note
        except Exception as e:
            await self.session.rollback()
            logger.error("Eslatma yaratishda xatolik", error=str(e))
            raise

    async def get_notes(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Note]:
        """Get user notes."""
        return await self.repo.get_by_user_id(user_id, limit, offset)

    async def update_note(self, note_id: int, **kwargs) -> Note:
        """Update an existing note."""
        note = await self.repo.update(note_id, **kwargs)
        await self.session.commit()
        return note

    async def delete_note(self, note_id: int) -> bool:
        """Delete a note."""
        result = await self.repo.delete(note_id)
        await self.session.commit()
        return result

    async def pin(self, note_id: int) -> Note:
        """Pin a note."""
        return await self.update_note(note_id, is_pinned=True)

    async def unpin(self, note_id: int) -> Note:
        """Unpin a note."""
        return await self.update_note(note_id, is_pinned=False)

    async def archive(self, note_id: int) -> Note:
        """Archive a note."""
        return await self.update_note(note_id, is_archived=True)

    async def search_notes(self, user_id: int, query: str) -> List[Note]:
        """Search notes with fulltext."""
        return await self.repo.search(user_id, query)

    async def export_note(self, note_id: int) -> str:
        """Export note to text."""
        note = await self.repo.get_by_id(note_id)
        if not note:
            raise ValueError("Eslatma topilmadi")
        return f"{note.title}\n\n{note.content}"

    async def word_count(self, note_id: int) -> int:
        """Get word count of a note."""
        note = await self.repo.get_by_id(note_id)
        if not note:
            return 0
        return len(note.content.split())
