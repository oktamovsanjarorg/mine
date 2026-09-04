import pytest
from src.core.services.habit import HabitService
from src.infrastructure.repositories.habit import HabitRepository
from datetime import datetime, timedelta, timezone

@pytest.fixture
def habit_service(async_session):
    repo = HabitRepository(async_session)
    return HabitService(repo)

@pytest.mark.asyncio
async def test_create_habit(habit_service, test_user):
    habit = await habit_service.create_habit(test_user.id, "Kitob o'qish", "daily")
    assert habit.name == "Kitob o'qish"
    assert habit.current_streak == 0

@pytest.mark.asyncio
async def test_check_in_streak(habit_service, test_user):
    habit = await habit_service.create_habit(test_user.id, "Suv ichish", "daily")
    
    res1 = await habit_service.check_in(habit.id)
    assert res1.current_streak == 1
    
    # Simulate next day for streak test (in reality, repo logic handles date diffs)
    # This requires mocking date or directly updating db for strict unit testing
