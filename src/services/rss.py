import structlog
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.rss import RSSRepository
from src.models.rss import RSSFeed, RSSItem

logger = structlog.get_logger(__name__)

class RSSParser:
    async def parse(self, url: str) -> List[Dict[str, Any]]:
        return [{"title": "Yangilik", "link": "http://link", "guid": "123"}]

class RSSService:
    """Service for managing RSS feeds."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = RSSRepository(session)
        self.parser = RSSParser()

    async def add_feed(self, user_id: int, url: str) -> RSSFeed:
        """Add a new RSS feed with auto-discovery."""
        try:
            feed = await self.repo.create(user_id=user_id, url=url, title="RSS Feed")
            await self.session.commit()
            return feed
        except Exception as e:
            await self.session.rollback()
            logger.error("RSS qoshishda xatolik", error=str(e))
            raise

    async def check_feed(self, feed_id: int) -> int:
        """Check a feed for new items."""
        feed = await self.repo.get_by_id(feed_id)
        if not feed:
            return 0
            
        items = await self.parser.parse(feed.url)
        new_count = 0
        for item in items:
            exists = await self.repo.item_exists(feed_id, item['guid'])
            if not exists:
                await self.repo.add_item(
                    feed_id=feed_id,
                    title=item['title'],
                    link=item['link'],
                    guid=item['guid']
                )
                new_count += 1
        await self.session.commit()
        return new_count

    async def check_all_feeds(self) -> None:
        """Check all active feeds."""
        feeds = await self.repo.get_all_active()
        for f in feeds:
            await self.check_feed(f.id)

    async def get_unread_items(self, user_id: int) -> List[RSSItem]:
        """Get unread items for user."""
        return await self.repo.get_unread(user_id)

    async def mark_read(self, item_id: int) -> bool:
        """Mark item as read."""
        result = await self.repo.mark_read(item_id)
        await self.session.commit()
        return result
