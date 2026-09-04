import structlog
from datetime import date
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.contact import ContactRepository
from src.models.contact import Contact

logger = structlog.get_logger(__name__)

class ContactService:
    """Service for managing contacts."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ContactRepository(session)

    async def create_contact(self, user_id: int, name: str, phone: str, email: Optional[str] = None, birthday: Optional[date] = None) -> Contact:
        """Create a new contact."""
        try:
            contact = await self.repo.create(
                user_id=user_id,
                name=name,
                phone=phone,
                email=email,
                birthday=birthday
            )
            await self.session.commit()
            return contact
        except Exception as e:
            await self.session.rollback()
            logger.error("Kontakt yaratishda xatolik", error=str(e))
            raise

    async def get_contacts(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Contact]:
        """Get user contacts."""
        return await self.repo.get_by_user_id(user_id, limit, offset)

    async def get_upcoming_birthdays(self, user_id: int, days: int = 7) -> List[Contact]:
        """Get upcoming birthdays."""
        return await self.repo.get_upcoming_birthdays(user_id, days)

    async def search(self, user_id: int, query: str) -> List[Contact]:
        """Search contacts."""
        return await self.repo.search(user_id, query)

    async def vcard_export(self, contact_id: int) -> str:
        """Export contact as vCard."""
        contact = await self.repo.get_by_id(contact_id)
        if not contact:
            raise ValueError("Kontakt topilmadi")
            
        vcard = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"FN:{contact.name}",
            f"TEL:{contact.phone}"
        ]
        if contact.email:
            vcard.append(f"EMAIL:{contact.email}")
        if contact.birthday:
            vcard.append(f"BDAY:{contact.birthday.strftime('%Y-%m-%d')}")
        vcard.append("END:VCARD")
        
        return "\n".join(vcard)

    async def vcard_import(self, user_id: int, vcard_data: str) -> List[Contact]:
        """Import contacts from vCard."""
        # Minimalistic parsing
        imported = []
        name = phone = email = birthday = None
        for line in vcard_data.split('\n'):
            line = line.strip()
            if line.startswith('FN:'):
                name = line[3:]
            elif line.startswith('TEL:'):
                phone = line[4:]
            elif line.startswith('EMAIL:'):
                email = line[6:]
            elif line.startswith('BDAY:'):
                try:
                    birthday = date.fromisoformat(line[5:])
                except:
                    pass
            elif line == 'END:VCARD' and name and phone:
                imported.append(await self.create_contact(user_id, name, phone, email, birthday))
                name = phone = email = birthday = None
        return imported
