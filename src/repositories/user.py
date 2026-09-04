from typing import Sequence, Type
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_or_create_by_telegram_id(self, telegram_id: int, first_name: str, username: str | None, last_name: str | None) -> tuple[User, bool]:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            return user, False
        user = User(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username,
            last_name=last_name
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user, True

    async def update_last_active(self, user_id: int) -> None:
        stmt = update(User).where(User.id == user_id).values(last_active=datetime.now(timezone.utc))
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_admins(self) -> list[User]:
        stmt = select(User).where(User.is_admin == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_users(self) -> list[User]:
        stmt = select(User).where(User.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_settings(self, user_id: int, **settings) -> User | None:
        return await self.update(user_id, **settings)
