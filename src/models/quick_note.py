import enum
from sqlalchemy import ForeignKey, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class QuickNoteType(str, enum.Enum):
    TEXT = "text"
    VOICE = "voice"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"

class QuickNote(Base, TimestampMixin):
    """Quick Note model."""
    __tablename__ = "quick_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    type: Mapped[QuickNoteType] = mapped_column(default=QuickNoteType.TEXT)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str | None] = mapped_column(String(50)) # e.g. telegram, web
