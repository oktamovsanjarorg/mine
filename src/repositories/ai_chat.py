from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.ai_chat import AIConversation, AIMessage

class AIChatRepository(BaseRepository[AIConversation]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIConversation)

    async def get_active_conversation(self, user_id: int) -> AIConversation | None:
        stmt = select(AIConversation).where(
            AIConversation.user_id == user_id,
            AIConversation.is_active == True
        ).order_by(AIConversation.created_at.desc()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_messages(self, conversation_id: int, limit: int = 50) -> list[AIMessage]:
        stmt = select(AIMessage).where(
            AIMessage.conversation_id == conversation_id
        ).order_by(AIMessage.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())
        messages.reverse()  # Return in chronological order
        return messages

    async def add_message(self, conversation_id: int, role: str, content: str, tokens: int = 0) -> AIMessage:
        msg = AIMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens=tokens
        )
        self.session.add(msg)
        await self.session.flush()
        await self.session.refresh(msg)
        return msg

    async def update_conversation_stats(self, conversation_id: int, tokens: int, message_count: int) -> None:
        conv = await self.get_by_id(conversation_id)
        if conv:
            conv.total_tokens += tokens
            conv.message_count += message_count
            await self.session.flush()
