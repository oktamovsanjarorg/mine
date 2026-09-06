from typing import Sequence
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.rss import RSSFeed, RSSItem

class RSSRepository(BaseRepository[RSSFeed]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RSSFeed)

    async def get_active_feeds(self) -> list[RSSFeed]:
        stmt = select(RSSFeed).where(
            RSSFeed.is_active == True
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_active(self) -> list[RSSFeed]:
        return await self.get_active_feeds()

    async def get_by_user_id(self, user_id: int) -> list[RSSFeed]:
        stmt = select(RSSFeed).where(
            RSSFeed.user_id == user_id
        ).order_by(RSSFeed.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def item_exists(self, feed_id: int, guid: str) -> bool:
        stmt = select(RSSItem).where(RSSItem.feed_id == feed_id, RSSItem.guid == guid)
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    async def get_unread(self, user_id: int, limit: int = 10) -> Sequence[RSSItem]:
        stmt = select(RSSItem).join(RSSFeed).where(
            RSSFeed.user_id == user_id,
            RSSItem.is_read == False
        ).order_by(RSSItem.fetched_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_item(self, feed_id: int, guid: str, title: str, link: str, description: str | None = None, published_at: datetime | None = None) -> RSSItem | None:
        stmt = select(RSSItem).where(RSSItem.guid == guid)
        result = await self.session.execute(stmt)
        if result.scalars().first():
            return None
            
        item = RSSItem(
            feed_id=feed_id,
            guid=guid,
            title=title,
            link=link,
            description=description,
            published_at=published_at
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_unread_items(self, feed_id: int, offset: int = 0, limit: int = 10) -> Sequence[RSSItem]:
        stmt = select(RSSItem).where(
            RSSItem.feed_id == feed_id,
            RSSItem.is_read == False
        ).order_by(RSSItem.published_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def mark_read(self, item_id: int) -> RSSItem | None:
        stmt = select(RSSItem).where(RSSItem.id == item_id)
        result = await self.session.execute(stmt)
        item = result.scalars().first()
        if item:
            item.is_read = True
            await self.session.flush()
            await self.session.refresh(item)
            return item
        return None

    async def mark_all_read(self, feed_id: int) -> int:
        stmt = update(RSSItem).where(
            RSSItem.feed_id == feed_id,
            RSSItem.is_read == False
        ).values(is_read=True)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

    async def get_saved_items(self, user_id: int, offset: int = 0, limit: int = 10) -> Sequence[RSSItem]:
        stmt = select(RSSItem).join(RSSFeed).where(
            RSSFeed.user_id == user_id,
            RSSItem.is_saved == True
        ).order_by(RSSItem.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
