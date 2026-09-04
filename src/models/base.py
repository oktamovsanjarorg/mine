import datetime
from sqlalchemy import DateTime, func, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 models."""
    pass

class TimestampMixin:
    """Mixin for adding created_at and updated_at timestamps."""
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

class SoftDeleteMixin:
    """Mixin for adding soft delete functionality."""
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
