import structlog
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.reminder import ReminderRepository
from src.models.reminder import Reminder
import re

logger = structlog.get_logger(__name__)

class ReminderService:
    """Service for managing reminders."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ReminderRepository(session)

    async def create_reminder(self, user_id: int, title: str, remind_at: datetime) -> Reminder:
        """Create a new reminder."""
        try:
            reminder = await self.repo.create(
                user_id=user_id,
                title=title,
                remind_at=remind_at,
                is_active=True
            )
            await self.session.commit()
            logger.info("Eslatma o'rnatildi", reminder_id=reminder.id)
            return reminder
        except Exception as e:
            await self.session.rollback()
            logger.error("Eslatma yaratishda xatolik", error=str(e))
            raise

    async def snooze_reminder(self, reminder_id: int, minutes: int = 15) -> Reminder:
        """Snooze a reminder."""
        reminder = await self.repo.get_by_id(reminder_id)
        if not reminder:
            raise ValueError("Eslatma topilmadi")
        
        new_time = datetime.utcnow() + timedelta(minutes=minutes)
        updated = await self.repo.update(reminder_id, remind_at=new_time, is_active=True)
        await self.session.commit()
        return updated

    async def deactivate(self, reminder_id: int) -> Reminder:
        """Deactivate a reminder."""
        updated = await self.repo.update(reminder_id, is_active=False)
        await self.session.commit()
        return updated

    async def trigger_reminder(self, reminder_id: int, bot) -> bool:
        """Trigger reminder with bot notification."""
        reminder = await self.repo.get_by_id(reminder_id)
        if not reminder or not reminder.is_active:
            return False
            
        try:
            await bot.send_message(
                chat_id=reminder.user_id,
                text=f"⏰ Eslatma: {reminder.title}"
            )
            await self.deactivate(reminder_id)
            return True
        except Exception as e:
            logger.error("Eslatmani yuborishda xatolik", error=str(e), reminder_id=reminder_id)
            return False

    async def load_all_active_reminders(self) -> List[Reminder]:
        """Load all active reminders."""
        return await self.repo.get_active_reminders()

    async def parse_time_input(self, text: str) -> Optional[datetime]:
        """Parse time input with natural language support."""
        text = text.lower()
        now = datetime.utcnow()
        
        if "ertaga" in text:
            return now + timedelta(days=1)
        elif "bugun" in text:
            return now + timedelta(hours=1)
        
        match = re.search(r'(\d+)\s+(daqiqa|soat|kun)', text)
        if match:
            val = int(match.group(1))
            unit = match.group(2)
            if unit == "daqiqa":
                return now + timedelta(minutes=val)
            elif unit == "soat":
                return now + timedelta(hours=val)
            elif unit == "kun":
                return now + timedelta(days=val)
                
        return None
