import datetime
from typing import List
from sqlalchemy import BigInteger, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, SoftDeleteMixin

class User(Base, TimestampMixin, SoftDeleteMixin):
    """User model for storing Telegram users."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(10), default='uz')
    timezone: Mapped[str] = mapped_column(String(50), default='Asia/Tashkent')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_provider: Mapped[str] = mapped_column(String(50), default='gemini')
    daily_digest_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    daily_digest_time: Mapped[str] = mapped_column(String(10), default='08:00')
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    default_currency: Mapped[str] = mapped_column(String(10), default='UZS')
    theme: Mapped[str | None] = mapped_column(String(50))
    last_active_at: Mapped[datetime.datetime | None]

    categories: Mapped[List["Category"]] = relationship(back_populates="user")
    tags: Mapped[List["Tag"]] = relationship(back_populates="user")
    tasks: Mapped[List["Task"]] = relationship(back_populates="user")
    notes: Mapped[List["Note"]] = relationship(back_populates="user")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="user")
