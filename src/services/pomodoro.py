import structlog
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.pomodoro import PomodoroRepository
from src.models.pomodoro import PomodoroSession, PomodoroType

logger = structlog.get_logger(__name__)

class PomodoroService:
    """Service for managing Pomodoro sessions."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PomodoroRepository(session)

    async def start_session(self, user_id: int, duration_minutes: int = 25, task_id: Optional[int] = None, session_type: PomodoroType = PomodoroType.WORK) -> PomodoroSession:
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
                type=session_type,
                started_at=datetime.now(timezone.utc),
                completed=False,
                interrupted=False
            )
            await self.session.commit()
            return session
        except Exception as e:
            await self.session.rollback()
            logger.error("Pomodoro boshlashda xatolik", error=str(e))
            raise

    async def end_session(self, session_id: int, status: str = "completed") -> Optional[PomodoroSession]:
        """End a Pomodoro session."""
        completed = (status == "completed")
        interrupted = (status == "interrupted")
        session = await self.repo.update(
            session_id,
            ended_at=datetime.now(timezone.utc),
            completed=completed,
            interrupted=interrupted
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
        now = datetime.now(timezone.utc)
        for s in active_sessions:
            started = s.started_at
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            elapsed = (now - started).total_seconds() / 60
            if elapsed >= s.duration_minutes:
                await self.end_session(s.id, status="completed")
                try:
                    await bot.send_message(
                        chat_id=s.user_id,
                        text="🍅 <b>Pomodoro vaqti tugadi!</b> Ajoyib mehnat qildingiz, endi 5 daqiqa dam oling.",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error("Xabar yuborishda xatolik", error=str(e))

