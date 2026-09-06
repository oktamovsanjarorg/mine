from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.snippet import Snippet

class SnippetRepository(BaseRepository[Snippet]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Snippet)

    async def get_by_language(self, user_id: int, language: str, offset: int = 0, limit: int = 10) -> Sequence[Snippet]:
        stmt = select(Snippet).where(
            Snippet.user_id == user_id,
            Snippet.language == language,
            Snippet.is_deleted == False
        ).order_by(Snippet.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_languages(self, user_id: int) -> list[str]:
        stmt = select(Snippet.language).where(
            Snippet.user_id == user_id,
            Snippet.is_deleted == False
        ).distinct()
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all() if row[0]]

    async def increment_usage(self, snippet_id: int) -> None:
        stmt = update(Snippet).where(Snippet.id == snippet_id).values(usage_count=Snippet.usage_count + 1)
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_by_user_id(self, user_id: int, limit: int = 100, offset: int = 0) -> Sequence[Snippet]:
        return await self.get_all(user_id, offset=offset, limit=limit)
