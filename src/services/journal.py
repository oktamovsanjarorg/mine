import structlog
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.journal import JournalRepository
from src.models.journal import JournalEntry

logger = structlog.get_logger(__name__)

class JournalService:
    """Service for managing journal entries."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = JournalRepository(session)

    async def write_entry(self, user_id: int, content: str, mood: Optional[str] = None) -> JournalEntry:
        """Write a new journal entry."""
        try:
            entry = await self.repo.create(
                user_id=user_id,
                content=content,
                mood=mood,
                created_at=datetime.utcnow()
            )
            await self.session.commit()
            return entry
        except Exception as e:
            await self.session.rollback()
            logger.error("Jurnal yozuvini saqlashda xatolik", error=str(e))
            raise

    async def get_entry(self, entry_id: int) -> Optional[JournalEntry]:
        """Get a specific journal entry."""
        return await self.repo.get_by_id(entry_id)

    async def mood_trend(self, user_id: int, days: int = 30) -> Dict[str, int]:
        """Get mood trend over time."""
        return await self.repo.get_mood_trend(user_id, days)

    async def writing_stats(self, user_id: int) -> Dict[str, Any]:
        """Get journal writing statistics."""
        return await self.repo.get_writing_stats(user_id)

    async def search(self, user_id: int, query: str) -> List[JournalEntry]:
        """Search journal entries."""
        return await self.repo.search(user_id, query)

    async def ai_monthly_summary_integration(self, user_id: int, year: int, month: int) -> str:
        """Generate monthly summary using AI (mock implementation)."""
        entries = await self.repo.get_monthly_entries(user_id, year, month)
        if not entries:
            return "Bu oy uchun yozuvlar yo'q."
        
        # Placeholder for AI integration
        return f"{year}-{month} uchun xulosa: Siz bu oy {len(entries)} ta yozuv qoldirdingiz."
