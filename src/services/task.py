import structlog
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.task import TaskRepository
from src.models.task import Task

logger = structlog.get_logger(__name__)

class TaskService:
    """Service for managing tasks."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TaskRepository(session)

    async def create_task(self, user_id: int, title: str, description: Optional[str] = None, due_date: Optional[datetime] = None) -> Task:
        """Create a new task."""
        try:
            task = await self.repo.create(
                user_id=user_id,
                title=title,
                description=description,
                due_date=due_date,
                is_completed=False
            )
            await self.session.commit()
            logger.info("Vazifa yaratildi", task_id=task.id, user_id=user_id)
            return task
        except Exception as e:
            await self.session.rollback()
            logger.error("Vazifa yaratishda xatolik", error=str(e))
            raise

    async def get_tasks(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Task]:
        """Get user tasks."""
        return await self.repo.get_by_user_id(user_id, limit, offset)

    async def update_task(self, task_id: int, **kwargs) -> Task:
        """Update an existing task."""
        task = await self.repo.update(task_id, **kwargs)
        await self.session.commit()
        return task

    async def complete_task(self, task_id: int) -> Task:
        """Mark task as completed."""
        task = await self.repo.update(task_id, is_completed=True, completed_at=datetime.utcnow())
        await self.session.commit()
        return task

    async def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        result = await self.repo.delete(task_id)
        await self.session.commit()
        return result

    async def get_today_tasks(self, user_id: int) -> List[Task]:
        """Get tasks due today."""
        return await self.repo.get_due_today(user_id)

    async def get_overdue_tasks(self, user_id: int) -> List[Task]:
        """Get overdue tasks."""
        return await self.repo.get_overdue(user_id)

    async def get_upcoming_tasks(self, user_id: int, days: int = 7) -> List[Task]:
        """Get upcoming tasks."""
        return await self.repo.get_upcoming(user_id, days)

    async def search_tasks(self, user_id: int, query: str) -> List[Task]:
        """Search tasks."""
        return await self.repo.search(user_id, query)

    async def get_task_stats(self, user_id: int) -> Dict[str, Any]:
        """Get task statistics."""
        return await self.repo.get_stats(user_id)

    async def add_subtask(self, parent_id: int, title: str) -> Task:
        """Add a subtask to a task."""
        parent = await self.repo.get_by_id(parent_id)
        if not parent:
            raise ValueError("Asosiy vazifa topilmadi")
        task = await self.repo.create(
            user_id=parent.user_id,
            parent_id=parent_id,
            title=title,
            is_completed=False
        )
        await self.session.commit()
        return task

    async def reorder(self, task_ids: List[int]) -> bool:
        """Reorder tasks."""
        # A simple implementation assuming order is an integer field
        for i, tid in enumerate(task_ids):
            await self.repo.update(tid, order=i)
        await self.session.commit()
        return True

    async def bulk_operations(self, action: str, task_ids: List[int]) -> int:
        """Perform bulk operations."""
        count = 0
        for tid in task_ids:
            if action == "complete":
                await self.repo.update(tid, is_completed=True, completed_at=datetime.utcnow())
                count += 1
            elif action == "delete":
                await self.repo.delete(tid)
                count += 1
        await self.session.commit()
        return count
