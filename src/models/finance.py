import enum
import datetime
from sqlalchemy import ForeignKey, String, Integer, Text, Boolean, Date, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, SoftDeleteMixin

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

    def __str__(self) -> str:
        return self.value

class Transaction(Base, TimestampMixin, SoftDeleteMixin):
    """Transaction model for finance tracking."""
    __tablename__ = "transactions"
    __table_args__ = (
        Index('ix_user_id_date', 'user_id', 'date'),
        Index('ix_transaction_user_type', 'user_id', 'type'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[TransactionType]
    amount: Mapped[float] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(10), default="UZS")
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    description: Mapped[str | None] = mapped_column(String(255))
    date: Mapped[datetime.date] = mapped_column(Date)
    payment_method: Mapped[str | None] = mapped_column(String(100))
    location: Mapped[str | None] = mapped_column(String(255))
    receipt_file_id: Mapped[int | None] = mapped_column(ForeignKey("files.id", ondelete="SET NULL"))
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="transactions")
    category: Mapped["Category"] = relationship()

class Budget(Base, TimestampMixin):
    """Budget model."""
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(10), default="UZS")
    period: Mapped[str] = mapped_column(String(50))
    start_date: Mapped[datetime.date] = mapped_column(Date)
    end_date: Mapped[datetime.date] = mapped_column(Date)
    alert_threshold: Mapped[int] = mapped_column(Integer, default=80)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class RecurringTransaction(Base, TimestampMixin):
    """Recurring Transaction model."""
    __tablename__ = "recurring_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[TransactionType]
    amount: Mapped[float] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(10), default="UZS")
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    description: Mapped[str | None] = mapped_column(String(255))
    frequency: Mapped[str] = mapped_column(String(50))
    next_date: Mapped[datetime.date] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
