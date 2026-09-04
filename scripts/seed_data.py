import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.settings import Settings
from src.infrastructure.database.models import Base, User, Task, Note, Transaction, Habit, Reminder

async def seed():
    settings = Settings()
    engine = create_async_engine(settings.DB_URL)
    session_maker = async_sessionmaker(engine, class_=AsyncSession)

    async with session_maker() as session:
        # Create standard user
        user = User(
            id=uuid.uuid4(),
            telegram_id=123456789,
            full_name="Sanjar",
            username="sanjar_demo",
            is_active=True,
            language_code="uz"
        )
        session.add(user)
        
        # 10 Tasks
        for i in range(10):
            t = Task(
                id=uuid.uuid4(),
                user_id=user.id,
                title=f"Demo vazifa {i+1}",
                description="Bu test uchun kiritilgan vazifa",
                priority="high" if i % 2 == 0 else "medium",
                status="pending"
            )
            session.add(t)

        # 5 Notes
        for i in range(5):
            n = Note(
                id=uuid.uuid4(),
                user_id=user.id,
                title=f"Eslatma {i+1}",
                content="Muhim ma'lumotlar...",
                tags=["ish", "shaxsiy"]
            )
            session.add(n)

        # 15 Transactions
        for i in range(15):
            is_income = i % 3 == 0
            tx = Transaction(
                id=uuid.uuid4(),
                user_id=user.id,
                amount=100000 if is_income else 15000,
                type="income" if is_income else "expense",
                category="Oylik" if is_income else "Oziq-ovqat",
                description="Demo tranzaksiya"
            )
            session.add(tx)

        # 4 Habits
        for i in range(4):
            h = Habit(
                id=uuid.uuid4(),
                user_id=user.id,
                name=f"Odat {i+1}",
                frequency="daily",
                current_streak=i*2,
                longest_streak=i*2+1
            )
            session.add(h)
            
        await session.commit()
        print("✅ Database seeded with rich development data!")

if __name__ == '__main__':
    asyncio.run(seed())
