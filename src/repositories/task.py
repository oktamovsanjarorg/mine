from typing import Sequence
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, update, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.task import Task

class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Task)

    async def get_by_status(self, user_id: int, status: str, offset: int = 0, limit: int = 10) -> Sequence[Task]:
        stmt = select(Task).options(selectinload(Task.tags), selectinload(Task.category)).where(
            Task.user_id == user_id,
            Task.status == status,
            Task.is_deleted == False
        ).order_by(Task.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_priority(self, user_id: int, priority: int, offset: int = 0, limit: int = 10) -> Sequence[Task]:
        stmt = select(Task).options(selectinload(Task.tags), selectinload(Task.category)).where(
            Task.user_id == user_id,
            Task.priority == priority,
            Task.is_deleted == False
        ).order_by(Task.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_today_tasks(self, user_id: int, timezone_str: str) -> list[Task]:
        # Approximate by comparing date part or just simple range
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        stmt = select(Task).options(selectinload(Task.tags), selectinload(Task.category)).where(
            Task.user_id == user_id,
            Task.is_deleted == False,
            Task.due_date >= today_start,
            Task.due_date < today_end
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_overdue_tasks(self, user_id: int, timezone_str: str) -> list[Task]:
        now = datetime.now(timezone.utc)
        stmt = select(Task).options(selectinload(Task.tags), selectinload(Task.category)).where(
            Task.user_id == user_id,
            Task.is_deleted == False,
            Task.status != 'done',
            Task.due_date < now
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_upcoming_tasks(self, user_id: int, days: int, timezone_str: str) -> list[Task]:
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=days)
        stmt = select(Task).options(selectinload(Task.tags), selectinload(Task.category)).where(
            Task.user_id == user_id,
            Task.is_deleted == False,
            Task.status != 'done',
            Task.due_date >= now,
            Task.due_date <= future
        ).order_by(Task.due_date.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_category(self, user_id: int, category_id: int, offset: int = 0, limit: int = 10) -> Sequence[Task]:
        stmt = select(Task).options(selectinload(Task.tags), selectinload(Task.category)).where(
            Task.user_id == user_id,
            Task.category_id == category_id,
            Task.is_deleted == False
        ).order_by(Task.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_subtasks(self, user_id: int, parent_id: int) -> list[Task]:
        stmt = select(Task).options(selectinload(Task.tags), selectinload(Task.category)).where(
            Task.user_id == user_id,
            Task.parent_id == parent_id,
            Task.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def complete_task(self, user_id: int, task_id: int) -> Task | None:
        task = await self.get_by_id(task_id)
        if task and task.user_id == user_id:
            task.status = 'done'
            task.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            await self.session.refresh(task)
            return task
        return None

    async def get_stats(self, user_id: int) -> dict:
        stmt = select(Task.status, func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.is_deleted == False
        ).group_by(Task.status)
        result = await self.session.execute(stmt)
        stats_raw = dict(result.all())
        
        total = sum(stats_raw.values())
        done = stats_raw.get('done', 0)
        pending = stats_raw.get('pending', 0)
        in_progress = stats_raw.get('in_progress', 0)
        
        now = datetime.now(timezone.utc)
        overdue_stmt = select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.is_deleted == False,
            Task.status != 'done',
            Task.due_date < now
        )
        overdue = (await self.session.execute(overdue_stmt)).scalar_one()

        return {
            "total": total,
            "done": done,
            "pending": pending,
            "in_progress": in_progress,
            "overdue": overdue
        }

    async def search_tasks(self, user_id: int, query: str, offset: int = 0, limit: int = 10) -> Sequence[Task]:
        stmt = select(Task).options(selectinload(Task.tags), selectinload(Task.category)).where(
            Task.user_id == user_id,
            Task.is_deleted == False,
            or_(Task.title.ilike(f"%{query}%"), Task.description.ilike(f"%{query}%"))
        ).order_by(Task.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
