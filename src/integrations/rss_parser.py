import structlog
import feedparser
import asyncio
from typing import Dict, Any, List

logger = structlog.get_logger(__name__)

class RSSParserClient:
    """RSS/Atom parser using feedparser."""

    async def parse_feed(self, url: str) -> Dict[str, Any]:
        try:
            def _parse():
                return feedparser.parse(url)
            
            feed = await asyncio.to_thread(_parse)
            if feed.bozo:
                logger.warning("Feed parsing bozo exception", url=url, exception=str(feed.bozo_exception))
            
            items = []
            for entry in feed.entries:
                items.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "description": entry.get("description", ""),
                    "published": entry.get("published", ""),
                    "guid": entry.get("id", entry.get("link", ""))
                })
                
            return {
                "title": feed.feed.get("title", ""),
                "description": feed.feed.get("description", ""),
                "link": feed.feed.get("link", ""),
                "items": items
            }
        except Exception as e:
            logger.error("RSS parse_feed failed", url=url, error=str(e))
            raise

    async def get_new_items(self, url: str, last_guid: str) -> List[Dict[str, Any]]:
        feed_data = await self.parse_feed(url)
        new_items = []
        for item in feed_data.get("items", []):
            if item["guid"] == last_guid:
                break
            new_items.append(item)
        return new_items

rss_client = RSSParserClient()
