from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, Text, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, SoftDeleteMixin
from .tag import note_tags

class Note(Base, TimestampMixin, SoftDeleteMixin):
    """Note model."""
    __tablename__ = "notes"
    __table_args__ = (
        Index('ix_user_id_is_pinned', 'user_id', 'is_pinned'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(50), default="text")
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    color: Mapped[str | None] = mapped_column(String(20))
    word_count: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(back_populates="notes")
    category: Mapped[Optional["Category"]] = relationship()
    tags: Mapped[List["Tag"]] = relationship(secondary=note_tags, back_populates="notes")
