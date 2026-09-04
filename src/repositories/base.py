from typing import Any, Generic, TypeVar, Type, Sequence
from sqlalchemy import select, func, delete, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

logger = structlog.get_logger()
T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def create(self, **kwargs: Any) -> T:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> T | None:
        return await self.session.get(self.model, id)

    async def get_all(self, user_id: int, offset: int = 0, limit: int = 10, order_by: str = 'created_at', desc: bool = True) -> Sequence[T]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        if hasattr(self.model, 'is_deleted'):
            stmt = stmt.where(self.model.is_deleted == False)
        
        order_col = getattr(self.model, order_by, None)
        if order_col is not None:
            if desc:
                stmt = stmt.order_by(order_col.desc())
            else:
                stmt = stmt.order_by(order_col.asc())
        
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, id: int, **kwargs: Any) -> T | None:
        instance = await self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.session.flush()
            await self.session.refresh(instance)
        return instance

    async def delete(self, id: int) -> bool:
        instance = await self.get_by_id(id)
        if instance:
            await self.session.delete(instance)
            await self.session.flush()
            return True
        return False

    async def soft_delete(self, id: int) -> bool:
        if hasattr(self.model, 'is_deleted'):
            instance = await self.get_by_id(id)
            if instance:
                instance.is_deleted = True
                if hasattr(self.model, 'deleted_at'):
                    from datetime import datetime, timezone
                    instance.deleted_at = datetime.now(timezone.utc)
                await self.session.flush()
                return True
        return False

    async def count(self, user_id: int, **filters: Any) -> int:
        stmt = select(func.count()).select_from(self.model).where(self.model.user_id == user_id)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def exists(self, **filters: Any) -> bool:
        stmt = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0

    async def get_or_create(self, defaults: dict, **filters: Any) -> tuple[T, bool]:
        stmt = select(self.model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        instance = result.scalars().first()
        if instance:
            return instance, False
        params = {**filters, **defaults}
        instance = self.model(**params)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance, True

    async def bulk_create(self, items: list[dict]) -> list[T]:
        instances = [self.model(**item) for item in items]
        self.session.add_all(instances)
        await self.session.flush()
        return instances

    async def bulk_update(self, ids: list[int], **kwargs: Any) -> int:
        stmt = update(self.model).where(self.model.id.in_(ids)).values(**kwargs)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

    async def filter_by(self, user_id: int, offset: int = 0, limit: int = 10, **filters: Any) -> Sequence[T]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search(self, user_id: int, query: str, fields: list[str], offset: int = 0, limit: int = 10) -> Sequence[T]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        or_conditions = []
        for field in fields:
            or_conditions.append(getattr(self.model, field).ilike(f"%{query}%"))
        if or_conditions:
            stmt = stmt.where(or_(*or_conditions))
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
