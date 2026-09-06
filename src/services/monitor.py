import hashlib
import httpx
import structlog
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.monitor import MonitorRepository
from src.models.monitor import WebMonitor, Monitor

logger = structlog.get_logger(__name__)

class WebScraper:
    async def get_content(self, url: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                res = await client.get(url)
                snippet = res.text[:100].strip().replace("\n", " ")
                content_hash = hashlib.md5(res.content).hexdigest()[:8]
                return f"HTTP {res.status_code} | Hash: {content_hash} | {snippet}"
        except Exception as e:
            return f"Xatolik: {str(e)}"

class MonitorService:
    """Service for website monitoring."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = MonitorRepository(session)
        self.scraper = WebScraper()

    async def get_user_monitors(self, user_id: int) -> List[WebMonitor]:
        return await self.repo.get_by_user_id(user_id)

    async def create_monitor(self, user_id: int, url: str, name: str) -> WebMonitor:
        """Create a new monitor."""
        try:
            content = await self.scraper.get_content(url)
            monitor = await self.repo.create(
                user_id=user_id,
                url=url,
                name=name,
                last_value=content,
                is_active=True
            )
            await self.session.commit()
            return monitor
        except Exception as e:
            await self.session.rollback()
            logger.error("Monitor yaratishda xatolik", error=str(e))
            raise

    async def delete_monitor(self, monitor_id: int) -> bool:
        res = await self.repo.delete(monitor_id)
        await self.session.commit()
        return res

    async def check_monitor(self, monitor_id: int) -> tuple[bool, str]:
        """Check monitor with web scraper diff detection."""
        monitor = await self.repo.get_by_id(monitor_id)
        if not monitor or not monitor.is_active:
            return False, "Monitor topilmadi yoki nofaol"
            
        new_content = await self.scraper.get_content(monitor.url)
        changed = new_content != monitor.last_value
        if changed:
            await self.repo.update(monitor_id, last_value=new_content)
            await self.session.commit()
            return True, f"O'zgarish aniqlandi:\n{new_content}"
        return False, f"O'zgarish yo'q (Holat: {new_content})"

    async def check_all_monitors(self) -> List[dict]:
        """Check all active monitors and return alerts."""
        monitors = await self.repo.get_all_active()
        alerts = []
        for m in monitors:
            has_changed, msg = await self.check_monitor(m.id)
            if has_changed:
                alerts.append({"user_id": m.user_id, "message": f"🔔 Sayt o'zgardi: {m.name} ({m.url})\n{msg}"})
        return alerts

    async def alert_on_changes(self, bot) -> None:
        """Send alerts for changed monitors."""
        alerts = await self.check_all_monitors()
        for alert in alerts:
            try:
                await bot.send_message(
                    chat_id=alert["user_id"],
                    text=alert["message"]
                )
            except Exception as e:
                logger.error("Ogohlantirish yuborishda xatolik", error=str(e))

