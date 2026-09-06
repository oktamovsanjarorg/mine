"""Export Repository for serializing user data."""
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task
from src.models.note import Note
from src.models.finance import Transaction
from src.models.habit import Habit
from src.models.reminder import Reminder


class ExportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_user_data(self, user_id: int) -> Dict[str, Any]:
        """Fetch all user domain records."""
        tasks = (await self.session.execute(select(Task).where(Task.user_id == user_id))).scalars().all()
        notes = (await self.session.execute(select(Note).where(Note.user_id == user_id))).scalars().all()
        txs = (await self.session.execute(select(Transaction).where(Transaction.user_id == user_id))).scalars().all()
        habits = (await self.session.execute(select(Habit).where(Habit.user_id == user_id))).scalars().all()
        reminders = (await self.session.execute(select(Reminder).where(Reminder.user_id == user_id))).scalars().all()

        return {
            "tasks": [
                {"id": t.id, "title": t.title, "description": t.description, "status": str(t.status), "created_at": str(t.created_at)}
                for t in tasks
            ],
            "notes": [
                {"id": n.id, "title": n.title, "content": n.content, "created_at": str(n.created_at)}
                for n in notes
            ],
            "transactions": [
                {"id": x.id, "amount": float(x.amount), "type": str(x.type), "description": x.description, "date": str(x.date)}
                for x in txs
            ],
            "habits": [
                {"id": h.id, "name": h.name, "frequency": str(h.frequency), "current_streak": h.current_streak}
                for h in habits
            ],
            "reminders": [
                {"id": r.id, "title": r.title, "remind_at": str(r.remind_at), "is_sent": r.is_sent}
                for r in reminders
            ]
        }

    async def get_module_data(self, user_id: int, module: str) -> List[Dict[str, Any]]:
        """Fetch data for a specific module."""
        all_data = await self.get_all_user_data(user_id)
        return all_data.get(module, [])
