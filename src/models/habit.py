import enum
import datetime
from typing import List
from sqlalchemy import ForeignKey, String, Integer, Text, Boolean, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class HabitFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

    def __str__(self) -> str:
        return self.value

class Habit(Base, TimestampMixin):
    """Habit tracking model."""
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(50))
    color: Mapped[str | None] = mapped_column(String(20))
    frequency: Mapped[HabitFrequency]
    target_count: Mapped[int] = mapped_column(Integer, default=1)
    custom_interval: Mapped[str | None] = mapped_column(String(50))
    reminder_time: Mapped[str | None] = mapped_column(String(10))
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    best_streak: Mapped[int] = mapped_column(Integer, default=0)
    total_completions: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


    def __init__(self, **kwargs):
        if "title" in kwargs and "name" not in kwargs:
            kwargs["name"] = kwargs.pop("title")
        if "longest_streak" in kwargs and "best_streak" not in kwargs:
            kwargs["best_streak"] = kwargs.pop("longest_streak")
        super().__init__(**kwargs)

    @property
    def title(self) -> str:
        return self.name

    @title.setter
    def title(self, value: str):
        self.name = value

    @property
    def longest_streak(self) -> int:
        return self.best_streak

    @longest_streak.setter
    def longest_streak(self, value: int):
        self.best_streak = value


    logs: Mapped[List["HabitLog"]] = relationship(back_populates="habit", cascade="all, delete-orphan")

class HabitLog(Base, TimestampMixin):
    """Habit completion log."""
    __tablename__ = "habit_logs"
    __table_args__ = (
        UniqueConstraint('habit_id', 'date', name='uq_habit_date'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id", ondelete="CASCADE"))
    date: Mapped[datetime.date] = mapped_column(Date)
    count: Mapped[int] = mapped_column(Integer, default=1)
    note: Mapped[str | None] = mapped_column(Text)

    habit: Mapped["Habit"] = relationship(back_populates="logs")
