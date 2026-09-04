import datetime
from typing import List
from sqlalchemy import ForeignKey, String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, SoftDeleteMixin
from .tag import bookmark_tags

class Bookmark(Base, TimestampMixin, SoftDeleteMixin):
    """Bookmark model."""
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    favicon_url: Mapped[str | None] = mapped_column(Text)
    screenshot_file_id: Mapped[int | None] = mapped_column(ForeignKey("files.id", ondelete="SET NULL"))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship()
    category: Mapped["Category"] = relationship()
    tags: Mapped[List["Tag"]] = relationship(secondary=bookmark_tags, back_populates="bookmarks")
