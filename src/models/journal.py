import datetime
from sqlalchemy import ForeignKey, String, Integer, Text, Boolean, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class JournalEntry(Base, TimestampMixin):
    """Journal entry model."""
    __tablename__ = "journal_entries"
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uq_user_journal_date'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    mood: Mapped[int | None] = mapped_column(Integer) # 1-5
    energy_level: Mapped[int | None] = mapped_column(Integer) # 1-5
    weather: Mapped[str | None] = mapped_column(String(100))
    location: Mapped[str | None] = mapped_column(String(255))
    date: Mapped[datetime.date] = mapped_column(Date)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship()
