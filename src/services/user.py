import structlog
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.user import UserRepository
from src.models.user import User

logger = structlog.get_logger(__name__)

class UserService:
    """Service for managing users."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)

    async def register_user(self, telegram_id: int, username: Optional[str] = None, full_name: Optional[str] = None) -> User:
        """Register a new user or return existing."""
        try:
            user = await self.repo.get_by_telegram_id(telegram_id)
            if user:
                return user
            
            user = await self.repo.create(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
                language_code="uz"
            )
            await self.session.commit()
            logger.info("Yangi foydalanuvchi ro'yxatdan o'tdi", telegram_id=telegram_id)
            return user
        except Exception as e:
            await self.session.rollback()
            logger.error("Foydalanuvchini ro'yxatdan o'tkazishda xatolik", error=str(e))
            raise

    async def get_profile(self, telegram_id: int) -> Optional[User]:
        """Get user profile."""
        return await self.repo.get_by_telegram_id(telegram_id)

    async def update_settings(self, telegram_id: int, settings: Dict[str, Any]) -> User:
        """Update user settings."""
        user = await self.repo.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError("Foydalanuvchi topilmadi")
        
        updated_user = await self.repo.update(user.id, **settings)
        await self.session.commit()
        return updated_user

    async def toggle_notifications(self, telegram_id: int, enabled: bool) -> User:
        """Toggle user notifications."""
        return await self.update_settings(telegram_id, {"notifications_enabled": enabled})

    async def is_admin(self, telegram_id: int) -> bool:
        """Check if user is admin."""
        user = await self.repo.get_by_telegram_id(telegram_id)
        return user is not None and user.is_admin

    async def set_timezone(self, telegram_id: int, timezone: str) -> User:
        """Set user timezone."""
        return await self.update_settings(telegram_id, {"timezone": timezone})
