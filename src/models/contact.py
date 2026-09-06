import datetime
from sqlalchemy import ForeignKey, String, Text, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, SoftDeleteMixin

class Contact(Base, TimestampMixin, SoftDeleteMixin):
    """Contact model."""
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    telegram_username: Mapped[str | None] = mapped_column(String(255))
    birthday: Mapped[datetime.date | None] = mapped_column(Date)
    company: Mapped[str | None] = mapped_column(String(255))
    position: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    birthday_reminder: Mapped[bool] = mapped_column(Boolean, default=False)

    category: Mapped["Category"] = relationship()

    def __init__(self, **kwargs):
        if "first_name" in kwargs and "name" not in kwargs:
            kwargs["name"] = kwargs.pop("first_name")
        super().__init__(**kwargs)

    @property
    def first_name(self) -> str:
        return self.name

    @first_name.setter
    def first_name(self, val: str):
        self.name = val
