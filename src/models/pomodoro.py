import enum
import datetime
from sqlalchemy import ForeignKey, String, Integer, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class PomodoroType(str, enum.Enum):
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"

class PomodoroSession(Base, TimestampMixin):
    """Pomodoro session model."""
    __tablename__ = "pomodoro_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id", ondelete="SET NULL"))
    type: Mapped[PomodoroType]
    duration_minutes: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    interrupted: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)

    task: Mapped["Task"] = relationship()

    def __init__(self, **kwargs):
        if "status" in kwargs:
            st = kwargs.pop("status")
            if st == "completed":
                kwargs["completed"] = True
                kwargs["interrupted"] = False
            elif st == "interrupted":
                kwargs["completed"] = False
                kwargs["interrupted"] = True
            elif st == "active":
                kwargs["completed"] = False
                kwargs["interrupted"] = False
        if "type" not in kwargs:
            kwargs["type"] = PomodoroType.WORK
        super().__init__(**kwargs)

    @property
    def status(self) -> str:
        if self.ended_at is None:
            return "active"
        if self.completed:
            return "completed"
        if self.interrupted:
            return "interrupted"
        return "finished"

    @status.setter
    def status(self, val: str) -> None:
        if val == "completed":
            self.completed = True
            self.interrupted = False
        elif val == "interrupted":
            self.completed = False
            self.interrupted = True
        elif val == "active":
            self.completed = False
            self.interrupted = False

    @property
    def start_time(self):
        return self.started_at

    @property
    def end_time(self):
        return self.ended_at

    @property
    def duration(self):
        return self.duration_minutes

