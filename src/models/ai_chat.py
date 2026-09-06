import datetime
from typing import List
from sqlalchemy import ForeignKey, String, Integer, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class AIConversation(Base, TimestampMixin):
    """AI Conversation model."""
    __tablename__ = "ai_conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str | None] = mapped_column(String(255))
    provider: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(100))
    system_prompt: Mapped[str | None] = mapped_column(Text)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    messages: Mapped[List["AIMessage"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")

class AIMessage(Base, TimestampMixin):
    """AI Message model."""
    __tablename__ = "ai_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("ai_conversations.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(50)) # user, assistant, system
    content: Mapped[str] = mapped_column(Text)
    tokens: Mapped[int | None] = mapped_column(Integer)

    conversation: Mapped["AIConversation"] = relationship(back_populates="messages")

# Aliases for backward compatibility
Conversation = AIConversation
Message = AIMessage

