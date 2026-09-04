import structlog
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.bookmark import BookmarkRepository
from src.models.bookmark import Bookmark
# Placeholder for URLMetaClient
class URLMetaClient:
    async def fetch_metadata(self, url: str):
        return {"title": "Sayt sarlavhasi", "description": "Sayt haqida qisqacha ma'lumot"}

logger = structlog.get_logger(__name__)

class BookmarkService:
    """Service for managing bookmarks."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = BookmarkRepository(session)
        self.meta_client = URLMetaClient()

    async def save_bookmark(self, user_id: int, url: str) -> Bookmark:
        """Save a bookmark with automatic URL metadata fetching."""
        try:
            meta = await self.meta_client.fetch_metadata(url)
            bookmark = await self.repo.create(
                user_id=user_id,
                url=url,
                title=meta.get("title", url),
                description=meta.get("description", ""),
                is_read=False,
                is_favorite=False
            )
            await self.session.commit()
            return bookmark
        except Exception as e:
            await self.session.rollback()
            logger.error("Xatcho'pni saqlashda xatolik", error=str(e))
            raise

    async def get_bookmarks(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Bookmark]:
        """Get user bookmarks."""
        return await self.repo.get_by_user_id(user_id, limit, offset)

    async def mark_read(self, bookmark_id: int) -> Bookmark:
        """Mark bookmark as read."""
        bookmark = await self.repo.update(bookmark_id, is_read=True)
        await self.session.commit()
        return bookmark

    async def toggle_favorite(self, bookmark_id: int) -> Bookmark:
        """Toggle favorite status of a bookmark."""
        bookmark = await self.repo.get_by_id(bookmark_id)
        if not bookmark:
            raise ValueError("Xatcho'p topilmadi")
        
        updated = await self.repo.update(bookmark_id, is_favorite=not bookmark.is_favorite)
        await self.session.commit()
        return updated

    async def search(self, user_id: int, query: str) -> List[Bookmark]:
        """Search bookmarks."""
        return await self.repo.search(user_id, query)
