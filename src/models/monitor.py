import datetime
from typing import List
from sqlalchemy import ForeignKey, String, Integer, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class WebMonitor(Base, TimestampMixin):
    """Web monitor model."""
    __tablename__ = "web_monitors"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(Text)
    css_selector: Mapped[str | None] = mapped_column(Text)
    xpath: Mapped[str | None] = mapped_column(Text)
    check_interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    last_value: Mapped[str | None] = mapped_column(Text)
    last_checked_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    last_changed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text)
    notify_on_change: Mapped[bool] = mapped_column(Boolean, default=True)

    logs: Mapped[List["MonitorLog"]] = relationship(back_populates="monitor", cascade="all, delete-orphan")

class MonitorLog(Base, TimestampMixin):
    """Monitor log model."""
    __tablename__ = "monitor_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("web_monitors.id", ondelete="CASCADE"))
    value: Mapped[str | None] = mapped_column(Text)
    status_code: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    checked_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    monitor: Mapped["WebMonitor"] = relationship(back_populates="logs")

# Alias for backward compatibility
Monitor = WebMonitor

