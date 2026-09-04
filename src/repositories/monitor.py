from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.monitor import WebMonitor, MonitorLog

class MonitorRepository(BaseRepository[WebMonitor]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, WebMonitor)

    async def get_active_monitors(self) -> list[WebMonitor]:
        stmt = select(WebMonitor).where(
            WebMonitor.is_active == True,
            WebMonitor.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_log(self, monitor_id: int, old_value: str | None, new_value: str | None, changed: bool) -> MonitorLog:
        log = MonitorLog(monitor_id=monitor_id, old_value=old_value, new_value=new_value, changed=changed)
        self.session.add(log)
        await self.session.flush()
        await self.session.refresh(log)
        return log

    async def get_logs(self, monitor_id: int, limit: int = 10) -> list[MonitorLog]:
        stmt = select(MonitorLog).where(
            MonitorLog.monitor_id == monitor_id
        ).order_by(MonitorLog.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def increment_error(self, monitor_id: int, error_msg: str) -> None:
        monitor = await self.get_by_id(monitor_id)
        if monitor:
            monitor.error_count += 1
            monitor.last_error = error_msg
            if monitor.error_count > 5:
                monitor.is_active = False
            await self.session.flush()

    async def reset_errors(self, monitor_id: int) -> None:
        monitor = await self.get_by_id(monitor_id)
        if monitor:
            monitor.error_count = 0
            monitor.last_error = None
            await self.session.flush()
