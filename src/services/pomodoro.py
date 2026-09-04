import structlog
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.pomodoro import PomodoroRepository
from src.models.pomodoro import PomodoroSession

logger = structlog.get_logger(__name__)

class PomodoroService:
    """Service for managing Pomodoro sessions."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PomodoroRepository(session)

    async def start_session(self, user_id: int, duration_minutes: int = 25, task_id: Optional[int] = None) -> PomodoroSession:
        """Start a new Pomodoro session."""
        try:
            # End any active session
            active = await self.get_active_session(user_id)
            if active:
                await self.end_session(active.id, status="interrupted")
                
            session = await self.repo.create(
                user_id=user_id,
                duration_minutes=duration_minutes,
                task_id=task_id,
                started_at=datetime.utcnow(),
                status="active"
            )
            await self.session.commit()
            return session
        except Exception as e:
            await self.session.rollback()
            logger.error("Pomodoro boshlashda xatolik", error=str(e))
            raise

    async def end_session(self, session_id: int, status: str = "completed") -> PomodoroSession:
        """End a Pomodoro session."""
        session = await self.repo.update(
            session_id,
            ended_at=datetime.utcnow(),
            status=status
        )
        await self.session.commit()
        return session

    async def get_active_session(self, user_id: int) -> Optional[PomodoroSession]:
        """Get currently active session."""
        return await self.repo.get_active(user_id)

    async def stats(self, user_id: int) -> Dict[str, Any]:
        """Get pomodoro statistics."""
        return await self.repo.get_stats(user_id)

    async def scheduler_integration(self, bot) -> None:
        """Scheduler integration to check completed sessions and notify."""
        active_sessions = await self.repo.get_all_active()
        now = datetime.utcnow()
        for s in active_sessions:
            elapsed = (now - s.started_at).total_seconds() / 60
            if elapsed >= s.duration_minutes:
                await self.end_session(s.id, status="completed")
                try:
                    await bot.send_message(
                        chat_id=s.user_id,
                        text="🍅 Pomodoro vaqti tugadi! Dam oling."
                    )
                except Exception as e:
                    logger.error("Xabar yuborishda xatolik", error=str(e))
