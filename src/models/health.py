import enum
import datetime
from sqlalchemy import ForeignKey, String, Integer, Text, Boolean, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class HealthLogType(str, enum.Enum):
    WATER = "water"
    SLEEP = "sleep"
    WEIGHT = "weight"
    EXERCISE = "exercise"
    STEPS = "steps"
    CALORIES = "calories"
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    MOOD = "mood"

class HealthLog(Base, TimestampMixin):
    """Health tracking log."""
    __tablename__ = "health_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[HealthLogType]
    value: Mapped[float] = mapped_column(Numeric(10, 2))
    unit: Mapped[str | None] = mapped_column(String(50))
    logged_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship()
