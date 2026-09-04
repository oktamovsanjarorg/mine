import structlog
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.ai_chat import AIChatRepository
from src.models.ai_chat import Conversation, Message

logger = structlog.get_logger(__name__)

class AIProvider:
    async def generate_response(self, prompt: str, context: List[Dict[str, str]], provider_name: str) -> str:
        return f"AI javobi ({provider_name}) ko'rinishida..."

class AIChatService:
    """Service for AI chat and conversations."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AIChatRepository(session)
        self.ai = AIProvider()

    async def quick_ask(self, question: str, provider: str = "openai") -> str:
        """Quick question without saving context."""
        return await self.ai.generate_response(question, [], provider)

    async def start_conversation(self, user_id: int, title: str) -> Conversation:
        """Start a new conversation."""
        try:
            conv = await self.repo.create_conversation(user_id=user_id, title=title)
            await self.session.commit()
            return conv
        except Exception as e:
            await self.session.rollback()
            logger.error("Suhbat yaratishda xatolik", error=str(e))
            raise

    async def send_message(self, conversation_id: int, text: str, provider: str = "openai") -> str:
        """Send message with context sliding window."""
        try:
            # Save user message
            await self.repo.add_message(conversation_id, role="user", content=text)
            
            # Get recent context (sliding window)
            recent_msgs = await self.repo.get_recent_messages(conversation_id, limit=10)
            context = [{"role": m.role, "content": m.content} for m in recent_msgs]
            
            # Generate response
            response = await self.ai.generate_response(text, context, provider)
            
            # Save bot message
            await self.repo.add_message(conversation_id, role="assistant", content=response)
            await self.session.commit()
            
            return response
        except Exception as e:
            await self.session.rollback()
            logger.error("Xabar yuborishda xatolik", error=str(e))
            raise

    async def image_analysis(self, image_bytes: bytes, prompt: str) -> str:
        """Analyze image with AI."""
        return "Rasmda qiziqarli narsalar bor."

    async def voice_generation(self, text: str) -> bytes:
        """Generate voice from text."""
        return b"voice data"

    async def multi_provider_switching(self, conversation_id: int, provider: str) -> bool:
        """Switch provider for conversation."""
        await self.repo.update_conversation(conversation_id, current_provider=provider)
        await self.session.commit()
        return True
