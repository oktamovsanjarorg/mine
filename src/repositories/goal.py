from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.goal import Goal

class GoalRepository(BaseRepository[Goal]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Goal)

    async def get_by_status(self, user_id: int, status: str, offset: int = 0, limit: int = 10) -> Sequence[Goal]:
        stmt = select(Goal).where(
            Goal.user_id == user_id,
            Goal.status == status,
            Goal.is_deleted == False
        ).order_by(Goal.deadline.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_progress(self, user_id: int, goal_id: int, new_value: float) -> Goal | None:
        goal = await self.get_by_id(goal_id)
        if goal and goal.user_id == user_id:
            goal.current_progress = new_value
            if goal.current_progress >= goal.target_value:
                goal.status = 'completed'
            await self.session.flush()
            await self.session.refresh(goal)
            return goal
        return None

    async def complete_goal(self, user_id: int, goal_id: int) -> Goal | None:
        goal = await self.get_by_id(goal_id)
        if goal and goal.user_id == user_id:
            goal.status = 'completed'
            goal.current_progress = goal.target_value
            await self.session.flush()
            await self.session.refresh(goal)
            return goal
        return None

    async def get_active_goals(self, user_id: int) -> list[Goal]:
        stmt = select(Goal).where(
            Goal.user_id == user_id,
            Goal.status == 'in_progress',
            Goal.is_deleted == False
        ).order_by(Goal.deadline.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
