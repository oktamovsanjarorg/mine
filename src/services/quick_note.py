import structlog
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.quick_note import QuickNoteRepository
from src.models.quick_note import QuickNote

logger = structlog.get_logger(__name__)

class QuickNoteService:
    """Service for managing quick notes."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = QuickNoteRepository(session)

    async def create(self, user_id: int, content: str) -> QuickNote:
        """Create a new quick note."""
        try:
            note = await self.repo.create(
                user_id=user_id,
                content=content,
                is_pinned=False
            )
            await self.session.commit()
            return note
        except Exception as e:
            await self.session.rollback()
            logger.error("Tezkor eslatma yaratishda xatolik", error=str(e))
            raise

    async def get_pinned(self, user_id: int) -> List[QuickNote]:
        """Get pinned quick notes."""
        return await self.repo.get_pinned(user_id)

    async def get_recent(self, user_id: int, limit: int = 10) -> List[QuickNote]:
        """Get recent quick notes."""
        return await self.repo.get_recent(user_id, limit)

    async def search(self, user_id: int, query: str) -> List[QuickNote]:
        """Search quick notes."""
        return await self.repo.search(user_id, query)
