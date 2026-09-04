import enum
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, SoftDeleteMixin

class CategoryType(str, enum.Enum):
    task = "task"
    finance = "finance"
    note = "note"
    bookmark = "bookmark"
    file = "file"
    snippet = "snippet"
    contact = "contact"
    general = "general"

class Category(Base, TimestampMixin, SoftDeleteMixin):
    """Category model for organizing items."""
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint('user_id', 'name', 'type', name='uq_user_category_name_type'),
        Index('ix_user_id_type', 'user_id', 'type'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    icon: Mapped[str | None] = mapped_column(String(50))
    color: Mapped[str | None] = mapped_column(String(20))
    type: Mapped[CategoryType]
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(back_populates="categories")
    parent: Mapped[Optional["Category"]] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[List["Category"]] = relationship(back_populates="parent")
    tasks: Mapped[List["Task"]] = relationship(back_populates="category")
