import pytest
from src.services.habit import HabitService

@pytest.fixture
def habit_service(async_session):
    return HabitService(async_session)

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
