import structlog
import aiohttp
from bs4 import BeautifulSoup
from lxml import html as lxml_html
from typing import Optional

logger = structlog.get_logger(__name__)

class WebScraperClient:
    """Web scraper using aiohttp and BeautifulSoup4."""

    async def fetch_html(self, url: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    response.raise_for_status()
                    return await response.text()
        except Exception as e:
            logger.error("WebScraper fetch_html failed", url=url, error=str(e))
            raise

    def extract_text(self, html: str, css_selector: str = "", xpath: str = "") -> str:
        try:
            if xpath:
                tree = lxml_html.fromstring(html)
                elements = tree.xpath(xpath)
                return " ".join([elem.text_content().strip() for elem in elements if hasattr(elem, "text_content")])
            
            if css_selector:
                soup = BeautifulSoup(html, "html.parser")
                elements = soup.select(css_selector)
                return " ".join([elem.get_text(strip=True) for elem in elements])
            
            # Default to full text if no selector
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text(separator=" ", strip=True)
        except Exception as e:
            logger.error("WebScraper extract_text failed", error=str(e))
            return ""

scraper_client = WebScraperClient()
