import structlog
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.goal import GoalRepository
from src.models.goal import Goal

logger = structlog.get_logger(__name__)

class GoalService:
    """Service for managing goals."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = GoalRepository(session)

    async def create_goal(self, user_id: int, title: str, target: float, unit: str, deadline: datetime) -> Goal:
        """Create a new goal."""
        try:
            goal = await self.repo.create(
                user_id=user_id,
                title=title,
                target=target,
                current=0.0,
                unit=unit,
                deadline=deadline,
                status="active"
            )
            await self.session.commit()
            return goal
        except Exception as e:
            await self.session.rollback()
            logger.error("Maqsad yaratishda xatolik", error=str(e))
            raise

    async def update_progress(self, goal_id: int, amount: float) -> Goal:
        """Update goal progress."""
        goal = await self.repo.get_by_id(goal_id)
        if not goal:
            raise ValueError("Maqsad topilmadi")
            
        new_current = goal.current + amount
        status = "completed" if new_current >= goal.target else goal.status
        updated = await self.repo.update(goal_id, current=new_current, status=status)
        await self.session.commit()
        return updated

    async def milestones_check(self, goal_id: int) -> List[str]:
        """Check for milestones."""
        goal = await self.repo.get_by_id(goal_id)
        if not goal:
            return []
            
        progress = goal.current / goal.target if goal.target > 0 else 0
        milestones = []
        if progress >= 0.5 and progress < 0.6:
            milestones.append("🎉 Maqsadning yarmi bajarildi!")
        elif progress >= 1.0:
            milestones.append("🏆 Maqsadga erishildi!")
        return milestones

    async def calculate_daily_target(self, goal_id: int) -> float:
        """Calculate daily target to reach the goal by deadline."""
        goal = await self.repo.get_by_id(goal_id)
        if not goal or not goal.deadline:
            return 0.0
            
        days_left = (goal.deadline.date() - datetime.utcnow().date()).days
        if days_left <= 0:
            return 0.0
            
        remaining = goal.target - goal.current
        return max(0.0, remaining / days_left)

    async def complete(self, goal_id: int) -> Goal:
        """Mark goal as completed."""
        goal = await self.repo.update(goal_id, status="completed")
        await self.session.commit()
        return goal
        
    async def pause(self, goal_id: int) -> Goal:
        """Pause a goal."""
        goal = await self.repo.update(goal_id, status="paused")
        await self.session.commit()
        return goal
        
    async def resume(self, goal_id: int) -> Goal:
        """Resume a paused goal."""
        goal = await self.repo.update(goal_id, status="active")
        await self.session.commit()
        return goal
