import structlog
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Any

logger = structlog.get_logger(__name__)

class URLMetaClient:
    """URL metadata extractor."""

    async def fetch_metadata(self, url: str) -> Dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    response.raise_for_status()
                    html = await response.text()
            
            soup = BeautifulSoup(html, "html.parser")
            
            title = soup.title.string if soup.title else ""
            
            desc_tag = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
            description = desc_tag["content"] if desc_tag and desc_tag.has_attr("content") else ""
            
            image_tag = soup.find("meta", property="og:image")
            image = image_tag["content"] if image_tag and image_tag.has_attr("content") else ""
            
            icon_tag = soup.find("link", rel="shortcut icon") or soup.find("link", rel="icon")
            favicon = icon_tag["href"] if icon_tag and icon_tag.has_attr("href") else ""
            if favicon and not favicon.startswith("http"):
                from urllib.parse import urljoin
                favicon = urljoin(url, favicon)
                
            return {
                "title": title.strip() if title else "",
                "description": description.strip() if description else "",
                "image": image,
                "favicon": favicon
            }
        except Exception as e:
            logger.error("URLMeta fetch_metadata failed", url=url, error=str(e))
            return {"title": "", "description": "", "image": "", "favicon": ""}

url_meta_client = URLMetaClient()
