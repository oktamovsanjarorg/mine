from sqlalchemy import ForeignKey, String, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, SoftDeleteMixin

class FileRecord(Base, TimestampMixin, SoftDeleteMixin):
    """File record model."""
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    telegram_file_id: Mapped[str] = mapped_column(String(255))
    file_name: Mapped[str | None] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(50))
    mime_type: Mapped[str | None] = mapped_column(String(255))
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    storage_path: Mapped[str | None] = mapped_column(Text)
    thumbnail_path: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    description: Mapped[str | None] = mapped_column(Text)
    checksum: Mapped[str | None] = mapped_column(String(255))

    category: Mapped["Category"] = relationship()

    def __init__(self, **kwargs):
        if "filename" in kwargs and "file_name" not in kwargs:
            kwargs["file_name"] = kwargs.pop("filename")
        if "path" in kwargs and "storage_path" not in kwargs:
            kwargs["storage_path"] = kwargs.pop("path")
        if "size" in kwargs and "file_size" not in kwargs:
            kwargs["file_size"] = kwargs.pop("size")
        if "content_type" in kwargs and "mime_type" not in kwargs:
            kwargs["mime_type"] = kwargs.pop("content_type")
        if "telegram_file_id" not in kwargs:
            kwargs["telegram_file_id"] = kwargs.get("storage_path") or "local"
        super().__init__(**kwargs)
