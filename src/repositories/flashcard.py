from typing import Sequence
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.flashcard import Flashcard, FlashcardDeck, FlashcardReview

class FlashcardRepository(BaseRepository[Flashcard]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Flashcard)

    async def get_decks(self, user_id: int) -> list[FlashcardDeck]:
        stmt = select(FlashcardDeck).where(
            FlashcardDeck.user_id == user_id,
            FlashcardDeck.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_cards(self, deck_id: int, offset: int = 0, limit: int = 10) -> Sequence[Flashcard]:
        stmt = select(Flashcard).where(
            Flashcard.deck_id == deck_id,
            Flashcard.is_deleted == False
        ).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_due_cards(self, deck_id: int, target_date: date, limit: int = 50) -> list[Flashcard]:
        stmt = select(Flashcard).where(
            Flashcard.deck_id == deck_id,
            Flashcard.is_deleted == False,
            Flashcard.next_review <= target_date
        ).order_by(Flashcard.next_review.asc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_card_sm2(self, card_id: int, easiness_factor: float, interval: int, repetitions: int, next_review: date) -> Flashcard | None:
        card = await self.get_by_id(card_id)
        if card:
            card.easiness_factor = easiness_factor
            card.interval = interval
            card.repetitions = repetitions
            card.next_review = next_review
            await self.session.flush()
            await self.session.refresh(card)
        return card

    async def add_review(self, card_id: int, quality: int) -> FlashcardReview:
        review = FlashcardReview(card_id=card_id, quality=quality)
        self.session.add(review)
        await self.session.flush()
        await self.session.refresh(review)
        return review

    async def get_deck_stats(self, deck_id: int) -> dict:
        total_stmt = select(func.count(Flashcard.id)).where(Flashcard.deck_id == deck_id, Flashcard.is_deleted == False)
        due_stmt = select(func.count(Flashcard.id)).where(Flashcard.deck_id == deck_id, Flashcard.is_deleted == False, Flashcard.next_review <= date.today())
        mastered_stmt = select(func.count(Flashcard.id)).where(Flashcard.deck_id == deck_id, Flashcard.is_deleted == False, Flashcard.interval > 21)
        learning_stmt = select(func.count(Flashcard.id)).where(Flashcard.deck_id == deck_id, Flashcard.is_deleted == False, Flashcard.interval <= 21)

        total = (await self.session.execute(total_stmt)).scalar() or 0
        due = (await self.session.execute(due_stmt)).scalar() or 0
        mastered = (await self.session.execute(mastered_stmt)).scalar() or 0
        learning = (await self.session.execute(learning_stmt)).scalar() or 0

        return {
            "total": total,
            "due": due,
            "mastered": mastered,
            "learning": learning
        }
