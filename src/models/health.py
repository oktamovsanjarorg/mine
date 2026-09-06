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

    def __str__(self) -> str:
        return self.value

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

    def __init__(self, **kwargs):
        if "metric_type" in kwargs and "type" not in kwargs:
            kwargs["type"] = kwargs.pop("metric_type")
        if "date" in kwargs and "logged_at" not in kwargs:
            d = kwargs.pop("date")
            kwargs["logged_at"] = datetime.datetime.combine(d, datetime.time.min) if isinstance(d, datetime.date) else d
        if "logged_at" not in kwargs:
            kwargs["logged_at"] = datetime.datetime.utcnow()
        super().__init__(**kwargs)

    user: Mapped["User"] = relationship()
