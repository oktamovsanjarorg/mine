import enum
import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, Text, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, SoftDeleteMixin
from .tag import task_tags

class TaskPriority(str, enum.Enum):
    LOWEST = "lowest"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    HIGHEST = "highest"

    def __str__(self) -> str:
        return self.value

class TaskStatus(str, enum.Enum):
    TODO = "todo"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    def __str__(self) -> str:
        return self.value



class Task(Base, TimestampMixin, SoftDeleteMixin):
    """Task model."""
    __tablename__ = "tasks"
    __table_args__ = (
        Index('ix_user_id_status', 'user_id', 'status'),
        Index('ix_user_id_due_date', 'user_id', 'due_date'),
        Index('ix_user_id_priority', 'user_id', 'priority'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[TaskPriority] = mapped_column(default=TaskPriority.MEDIUM)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.TODO)
    due_date: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    reminder_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id", ondelete="SET NULL"))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    estimated_minutes: Mapped[int | None] = mapped_column(Integer)
    recurrence_rule: Mapped[str | None] = mapped_column(String(255))

    @property
    def is_completed(self) -> bool:
        return self.status in (TaskStatus.DONE, "done", "completed")

    @is_completed.setter
    def is_completed(self, value: bool):
        self.status = TaskStatus.DONE if value else TaskStatus.TODO


    user: Mapped["User"] = relationship(back_populates="tasks")
    category: Mapped[Optional["Category"]] = relationship(back_populates="tasks")
    parent: Mapped[Optional["Task"]] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[List["Task"]] = relationship(back_populates="parent")
    tags: Mapped[List["Tag"]] = relationship(secondary=task_tags, back_populates="tasks")
