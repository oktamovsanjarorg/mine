import pytest
from src.services.pomodoro import PomodoroService
from src.models.pomodoro import PomodoroType

@pytest.fixture
def pomodoro_service(async_session):
    return PomodoroService(async_session)

@pytest.mark.asyncio
async def test_start_and_end_pomodoro(pomodoro_service, test_user):
    session = await pomodoro_service.start_session(test_user.id, duration_minutes=25, session_type=PomodoroType.WORK)
    assert session.id is not None
    assert session.duration_minutes == 25
    assert session.completed is False
    assert session.status == "active"

    active = await pomodoro_service.get_active_session(test_user.id)
    assert active is not None
    assert active.id == session.id

    ended = await pomodoro_service.end_session(session.id, status="completed")
    assert ended.completed is True
    assert ended.status == "completed"

    active_after = await pomodoro_service.get_active_session(test_user.id)
    assert active_after is None

    stats = await pomodoro_service.stats(test_user.id)
    assert stats["completed_sessions"] == 1
    assert stats["total_minutes"] == 25
