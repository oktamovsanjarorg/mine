import datetime
from typing import List
from sqlalchemy import ForeignKey, String, Integer, Text, Boolean, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class FlashcardDeck(Base, TimestampMixin):
    """Flashcard deck model."""
    __tablename__ = "flashcard_decks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    cards: Mapped[List["Flashcard"]] = relationship(back_populates="deck", cascade="all, delete-orphan")

class Flashcard(Base, TimestampMixin):
    """Flashcard model with SM-2 spaced repetition fields."""
    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(primary_key=True)
    deck_id: Mapped[int] = mapped_column(ForeignKey("flashcard_decks.id", ondelete="CASCADE"))
    front: Mapped[str] = mapped_column(Text)
    back: Mapped[str] = mapped_column(Text)
    
    # SM-2 fields
    easiness_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval: Mapped[int] = mapped_column(Integer, default=0)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    next_review: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    last_reviewed: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)

    def __init__(self, **kwargs):
        if "repetition" in kwargs and "repetitions" not in kwargs:
            kwargs["repetitions"] = kwargs.pop("repetition")
        super().__init__(**kwargs)

    @property
    def repetition(self) -> int:
        return self.repetitions

    @repetition.setter
    def repetition(self, val: int):
        self.repetitions = val

    deck: Mapped["FlashcardDeck"] = relationship(back_populates="cards")
    reviews: Mapped[List["FlashcardReview"]] = relationship(back_populates="card", cascade="all, delete-orphan")

class FlashcardReview(Base, TimestampMixin):
    """Flashcard review log."""
    __tablename__ = "flashcard_reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("flashcards.id", ondelete="CASCADE"))
    quality: Mapped[int] = mapped_column(Integer) # 0-5
    reviewed_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    card: Mapped["Flashcard"] = relationship(back_populates="reviews")

# Aliases for backward compatibility
Deck = FlashcardDeck
Card = Flashcard

