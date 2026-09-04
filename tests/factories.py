import factory
from factory.alchemy import SQLAlchemyModelFactory
import uuid
from datetime import datetime, timezone
from src.infrastructure.database.models import User, Task, Note, Transaction, Habit, Reminder
from tests.conftest import async_session

class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = async_session
        sqlalchemy_session_persistence = 'commit'

class UserFactory(BaseFactory):
    class Meta:
        model = User

    id = factory.LazyFunction(uuid.uuid4)
    telegram_id = factory.Sequence(lambda n: 100000000 + n)
    full_name = factory.Faker('name')
    username = factory.Faker('user_name')
    is_active = True
    language_code = "uz"

class TaskFactory(BaseFactory):
    class Meta:
        model = Task

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text')
    status = "pending"
    priority = "medium"

class NoteFactory(BaseFactory):
    class Meta:
        model = Note
        
    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence', nb_words=3)
    content = factory.Faker('paragraph')
    tags = ["test"]

class TransactionFactory(BaseFactory):
    class Meta:
        model = Transaction

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.SubFactory(UserFactory)
    amount = factory.Faker('random_int', min=1000, max=1000000)
    type = "expense"
    category = "Oziq-ovqat"
    description = factory.Faker('sentence')

class HabitFactory(BaseFactory):
    class Meta:
        model = Habit

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.SubFactory(UserFactory)
    name = factory.Faker('word')
    frequency = "daily"
    current_streak = 0
    longest_streak = 0

class ReminderFactory(BaseFactory):
    class Meta:
        model = Reminder

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence')
    remind_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    is_sent = False
