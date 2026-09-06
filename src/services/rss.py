import structlog
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.rss import RSSRepository
from src.models.rss import RSSFeed, RSSItem
from src.integrations.rss_parser import rss_client

logger = structlog.get_logger(__name__)

class RSSService:
    """Service for managing RSS feeds."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = RSSRepository(session)
        self.parser = rss_client

    async def get_user_feeds(self, user_id: int) -> List[RSSFeed]:
        """Get all feeds for user."""
        return await self.repo.get_by_user_id(user_id)

    async def add_feed(self, user_id: int, url: str) -> RSSFeed:
        """Add a new RSS feed with auto-discovery and initial item fetch."""
        try:
            # Parse feed to verify and extract title
            feed_data = await self.parser.parse_feed(url)
            title = feed_data.get("title") or url.replace("https://", "").replace("http://", "").split("/")[0]
            description = feed_data.get("description")

            feed = await self.repo.create(
                user_id=user_id,
                url=url,
                title=title,
                description=description,
                is_active=True
            )
            
            # Fetch latest items immediately
            for item in feed_data.get("items", [])[:10]:
                await self.repo.add_item(
                    feed_id=feed.id,
                    guid=item.get("guid") or item.get("link") or item.get("title"),
                    title=item.get("title", "Sarlavhasiz"),
                    link=item.get("link", ""),
                    description=item.get("description")
                )

            await self.session.commit()
            return feed
        except Exception as e:
            await self.session.rollback()
            logger.error("RSS qoshishda xatolik", error=str(e))
            raise

    async def delete_feed(self, feed_id: int) -> bool:
        """Delete RSS feed."""
        res = await self.repo.delete(feed_id)
        await self.session.commit()
        return res

    async def check_feed(self, feed_id: int) -> int:
        """Check a feed for new items."""
        feed = await self.repo.get_by_id(feed_id)
        if not feed:
            return 0
            
        try:
            feed_data = await self.parser.parse_feed(feed.url)
            items = feed_data.get("items", [])
            new_count = 0
            for item in items:
                guid = item.get("guid") or item.get("link") or item.get("title")
                exists = await self.repo.item_exists(feed_id, guid)
                if not exists:
                    await self.repo.add_item(
                        feed_id=feed_id,
                        guid=guid,
                        title=item.get("title", "Sarlavhasiz"),
                        link=item.get("link", ""),
                        description=item.get("description")
                    )
                    new_count += 1
            await self.session.commit()
            return new_count
        except Exception as e:
            logger.error("RSS tekshirishda xato", feed_id=feed_id, error=str(e))
            return 0

    async def check_all_feeds(self) -> int:
        """Check all active feeds."""
        feeds = await self.repo.get_all_active()
        total_new = 0
        for f in feeds:
            total_new += await self.check_feed(f.id)
        return total_new

    async def get_unread_items(self, user_id: int, limit: int = 10) -> List[RSSItem]:
        """Get unread items for user."""
        return list(await self.repo.get_unread(user_id, limit=limit))

    async def mark_read(self, item_id: int) -> bool:
        """Mark item as read."""
        result = await self.repo.mark_read(item_id)
        await self.session.commit()
        return result is not None

