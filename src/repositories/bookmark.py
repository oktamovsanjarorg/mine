from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.bookmark import Bookmark

class BookmarkRepository(BaseRepository[Bookmark]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Bookmark)

    async def get_unread(self, user_id: int, offset: int = 0, limit: int = 10) -> Sequence[Bookmark]:
        stmt = select(Bookmark).where(
            Bookmark.user_id == user_id,
            Bookmark.is_read == False,
            Bookmark.is_deleted == False
        ).order_by(Bookmark.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_favorites(self, user_id: int, offset: int = 0, limit: int = 10) -> Sequence[Bookmark]:
        stmt = select(Bookmark).where(
            Bookmark.user_id == user_id,
            Bookmark.is_favorite == True,
            Bookmark.is_deleted == False
        ).order_by(Bookmark.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def mark_read(self, user_id: int, bookmark_id: int) -> Bookmark | None:
        bookmark = await self.get_by_id(bookmark_id)
        if bookmark and bookmark.user_id == user_id:
            bookmark.is_read = True
            await self.session.flush()
            await self.session.refresh(bookmark)
            return bookmark
        return None

    async def toggle_favorite(self, user_id: int, bookmark_id: int) -> Bookmark | None:
        bookmark = await self.get_by_id(bookmark_id)
        if bookmark and bookmark.user_id == user_id:
            bookmark.is_favorite = not bookmark.is_favorite
            await self.session.flush()
            await self.session.refresh(bookmark)
            return bookmark
        return None

    async def get_unread_count(self, user_id: int) -> int:
        stmt = select(func.count(Bookmark.id)).where(
            Bookmark.user_id == user_id,
            Bookmark.is_read == False,
            Bookmark.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_user_id(self, user_id: int, limit: int = 10, offset: int = 0) -> Sequence[Bookmark]:
        return await self.get_all(user_id, offset=offset, limit=limit)
