import datetime
from typing import List
from sqlalchemy import ForeignKey, String, Integer, Text, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class RSSFeed(Base, TimestampMixin):
    """RSS feed model."""
    __tablename__ = "rss_feeds"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(Text)
    check_interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    last_checked_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_new: Mapped[bool] = mapped_column(Boolean, default=True)
    max_items: Mapped[int] = mapped_column(Integer, default=100)

    items: Mapped[List["RSSItem"]] = relationship(back_populates="feed", cascade="all, delete-orphan")

class RSSItem(Base, TimestampMixin):
    """RSS item model."""
    __tablename__ = "rss_items"
    __table_args__ = (
        UniqueConstraint('feed_id', 'guid', name='uq_rss_feed_guid'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    feed_id: Mapped[int] = mapped_column(ForeignKey("rss_feeds.id", ondelete="CASCADE"))
    guid: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(255))
    link: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=False)
    fetched_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    feed: Mapped["RSSFeed"] = relationship(back_populates="items")
