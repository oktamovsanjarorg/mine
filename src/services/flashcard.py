import structlog
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.flashcard import FlashcardRepository
from src.models.flashcard import Deck, Card

logger = structlog.get_logger(__name__)

class FlashcardService:
    """Service for managing flashcards and decks (SM-2 Algorithm)."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = FlashcardRepository(session)

    async def create_deck(self, user_id: int, name: str, description: Optional[str] = None) -> Deck:
        """Create a new deck."""
        try:
            deck = await self.repo.create_deck(user_id=user_id, name=name, description=description)
            await self.session.commit()
            return deck
        except Exception as e:
            await self.session.rollback()
            logger.error("To'plam yaratishda xatolik", error=str(e))
            raise

    async def add_card(self, deck_id: int, front: str, back: str) -> Card:
        """Add a card to a deck."""
        try:
            card = await self.repo.create_card(
                deck_id=deck_id,
                front=front,
                back=back,
                interval=0,
                repetition=0,
                easiness_factor=2.5,
                next_review=datetime.utcnow()
            )
            await self.session.commit()
            return card
        except Exception as e:
            await self.session.rollback()
            logger.error("Karta qo'shishda xatolik", error=str(e))
            raise

    async def get_due_cards(self, user_id: int, limit: int = 50) -> List[Card]:
        """Get cards due for review."""
        return await self.repo.get_due_cards(user_id, limit)

    async def review_card(self, card_id: int, quality: int) -> Card:
        """Review a card with full SM-2 algorithm calculation. Quality 0-5."""
        card = await self.repo.get_card_by_id(card_id)
        if not card:
            raise ValueError("Karta topilmadi")

        if quality < 0 or quality > 5:
            raise ValueError("Sifat 0-5 oralig'ida bo'lishi kerak")

        if quality >= 3:
            if card.repetition == 0:
                interval = 1
            elif card.repetition == 1:
                interval = 6
            else:
                interval = round(card.interval * card.easiness_factor)
            repetition = card.repetition + 1
        else:
            repetition = 0
            interval = 1

        easiness_factor = card.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        easiness_factor = max(1.3, easiness_factor)
        
        next_review = datetime.utcnow() + timedelta(days=interval)

        updated_card = await self.repo.update_card(
            card_id,
            interval=interval,
            repetition=repetition,
            easiness_factor=easiness_factor,
            next_review=next_review
        )
        await self.session.commit()
        return updated_card

    async def deck_stats(self, deck_id: int) -> Dict[str, Any]:
        """Get deck statistics."""
        return await self.repo.get_deck_stats(deck_id)

    async def generate_cards_ai(self, deck_id: int, text: str) -> List[Card]:
        """Generate cards from text using AI (Mock)."""
        # Placeholder AI logic
        cards = []
        sentences = text.split('.')
        for s in sentences:
            if len(s.strip()) > 10:
                front = s.strip()
                back = "AI yordamida javob: " + s[:10]
                cards.append(await self.add_card(deck_id, front, back))
        return cards
