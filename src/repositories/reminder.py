from typing import Sequence
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.reminder import Reminder

class ReminderRepository(BaseRepository[Reminder]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Reminder)

    async def get_active(self, user_id: int, offset: int = 0, limit: int = 10) -> Sequence[Reminder]:
        stmt = select(Reminder).where(
            Reminder.user_id == user_id,
            Reminder.is_active == True,
            Reminder.is_deleted == False
        ).order_by(Reminder.remind_at.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_due_reminders(self, before: datetime) -> list[Reminder]:
        stmt = select(Reminder).where(
            Reminder.is_active == True,
            Reminder.is_deleted == False,
            Reminder.remind_at <= before
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def snooze(self, user_id: int, reminder_id: int, new_time: datetime) -> Reminder | None:
        reminder = await self.get_by_id(reminder_id)
        if reminder and reminder.user_id == user_id:
            reminder.remind_at = new_time
            reminder.is_active = True
            await self.session.flush()
            await self.session.refresh(reminder)
            return reminder
        return None

    async def deactivate(self, user_id: int, reminder_id: int) -> Reminder | None:
        reminder = await self.get_by_id(reminder_id)
        if reminder and reminder.user_id == user_id:
            reminder.is_active = False
            await self.session.flush()
            await self.session.refresh(reminder)
            return reminder
        return None

    async def get_all_active(self) -> list[Reminder]:
        stmt = select(Reminder).where(
            Reminder.is_active == True,
            Reminder.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
