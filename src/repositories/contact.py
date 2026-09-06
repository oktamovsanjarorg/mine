from datetime import date, timedelta
from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.contact import Contact

class ContactRepository(BaseRepository[Contact]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Contact)

    async def get_upcoming_birthdays(self, user_id: int, days: int) -> list[Contact]:
        today = date.today()
        future = today + timedelta(days=days)
        
        # Simple extraction logic for PostgreSQL, assuming birthday is stored as Date
        stmt = select(Contact).where(
            Contact.user_id == user_id,
            Contact.is_deleted == False,
            Contact.birthday.is_not(None)
        )
        # Note: True advanced birthday logic across year bounds in SQL can be complex,
        # but a basic filter in Python can be used if SQL is too dialect-specific.
        result = await self.session.execute(stmt)
        contacts = result.scalars().all()
        
        upcoming = []
        for c in contacts:
            if c.birthday:
                # Replace year to current year to compare
                try:
                    c_bday_this_year = c.birthday.replace(year=today.year)
                except ValueError: # leap year 29 Feb
                    c_bday_this_year = c.birthday.replace(year=today.year, month=3, day=1)
                
                if c_bday_this_year < today:
                    try:
                        c_bday_this_year = c.birthday.replace(year=today.year + 1)
                    except ValueError:
                        c_bday_this_year = c.birthday.replace(year=today.year + 1, month=3, day=1)
                
                if today <= c_bday_this_year <= future:
                    upcoming.append(c)
        return upcoming

    async def get_today_birthdays(self, user_id: int, today: date) -> list[Contact]:
        stmt = select(Contact).where(
            Contact.user_id == user_id,
            Contact.is_deleted == False,
            extract('month', Contact.birthday) == today.month,
            extract('day', Contact.birthday) == today.day
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_favorites(self, user_id: int) -> list[Contact]:
        stmt = select(Contact).where(
            Contact.user_id == user_id,
            Contact.is_favorite == True,
            Contact.is_deleted == False
        ).order_by(Contact.name.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: int, limit: int = 100, offset: int = 0) -> list[Contact]:
        return list(await self.get_all(user_id, offset=offset, limit=limit, order_by="name", desc=False))
