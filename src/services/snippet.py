import structlog
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.snippet import SnippetRepository
from src.models.snippet import Snippet

logger = structlog.get_logger(__name__)

class SnippetService:
    """Service for managing text snippets."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SnippetRepository(session)

    async def create_snippet(self, user_id: int, name: str, content: str) -> Snippet:
        """Create a new snippet."""
        try:
            snippet = await self.repo.create(
                user_id=user_id,
                name=name,
                content=content,
                usage_count=0
            )
            await self.session.commit()
            return snippet
        except Exception as e:
            await self.session.rollback()
            logger.error("Parcha yaratishda xatolik", error=str(e))
            raise

    async def get_snippets(self, user_id: int, limit: int = 100) -> List[Snippet]:
        """Get user snippets."""
        return await self.repo.get_by_user_id(user_id, limit)

    async def search(self, user_id: int, query: str) -> List[Snippet]:
        """Search snippets."""
        return await self.repo.search(user_id, query)

    async def increment_usage(self, snippet_id: int) -> Snippet:
        """Increment usage count for a snippet."""
        snippet = await self.repo.get_by_id(snippet_id)
        if not snippet:
            raise ValueError("Parcha topilmadi")
            
        updated = await self.repo.update(snippet_id, usage_count=snippet.usage_count + 1)
        await self.session.commit()
        return updated

    async def format_for_copy(self, snippet_id: int) -> str:
        """Format snippet for easy copying in Telegram."""
        snippet = await self.repo.get_by_id(snippet_id)
        if not snippet:
            raise ValueError("Parcha topilmadi")
        return f"```\n{snippet.content}\n```"
