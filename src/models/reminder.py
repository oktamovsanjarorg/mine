import enum
import datetime
from sqlalchemy import ForeignKey, String, Integer, Text, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class RepeatType(str, enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class Reminder(Base, TimestampMixin):
    """Reminder model."""
    __tablename__ = "reminders"
    __table_args__ = (
        Index('ix_is_active_remind_at', 'is_active', 'remind_at'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str | None] = mapped_column(Text)
    remind_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    repeat_type: Mapped[RepeatType] = mapped_column(default=RepeatType.NONE)
    repeat_interval: Mapped[int | None] = mapped_column(Integer)
    repeat_end_date: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_triggered_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))

    @property
    def is_sent(self) -> bool:
        return not self.is_active

    @is_sent.setter
    def is_sent(self, value: bool):
        self.is_active = not value


    user: Mapped["User"] = relationship()
    task: Mapped["Task"] = relationship()
