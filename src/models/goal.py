import enum
import datetime
from typing import List
from sqlalchemy import ForeignKey, String, Integer, Text, Boolean, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class GoalStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

    def __str__(self) -> str:
        return self.value

class Goal(Base, TimestampMixin):
    """Goal model."""
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    target_value: Mapped[float] = mapped_column(Numeric(15, 2))
    current_value: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    unit: Mapped[str | None] = mapped_column(String(50))
    deadline: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[GoalStatus] = mapped_column(default=GoalStatus.NOT_STARTED)
    icon: Mapped[str | None] = mapped_column(String(50))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    completed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))

    def __init__(self, **kwargs):
        if "target" in kwargs and "target_value" not in kwargs:
            kwargs["target_value"] = kwargs.pop("target")
        if "current" in kwargs and "current_value" not in kwargs:
            kwargs["current_value"] = kwargs.pop("current")
        super().__init__(**kwargs)

    @property
    def target(self) -> float:
        return float(self.target_value) if self.target_value is not None else 0.0

    @target.setter
    def target(self, val: float):
        self.target_value = val

    @property
    def current(self) -> float:
        return float(self.current_value) if self.current_value is not None else 0.0

    @current.setter
    def current(self, val: float):
        self.current_value = val

    milestones: Mapped[List["GoalMilestone"]] = relationship(back_populates="goal", cascade="all, delete-orphan")

class GoalMilestone(Base, TimestampMixin):
    """Goal milestone model."""
    __tablename__ = "goal_milestones"

    id: Mapped[int] = mapped_column(primary_key=True)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    target_value: Mapped[float] = mapped_column(Numeric(15, 2))
    is_reached: Mapped[bool] = mapped_column(Boolean, default=False)
    reached_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))

    goal: Mapped["Goal"] = relationship(back_populates="milestones")
