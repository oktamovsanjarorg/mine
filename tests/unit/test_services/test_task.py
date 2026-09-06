import pytest
from src.services.task import TaskService

@pytest.fixture
def task_service(async_session):
    return TaskService(async_session)

@pytest.mark.asyncio
async def test_create_task(task_service, test_user):
    task = await task_service.create_task(
        user_id=test_user.id,
        title="Test Task",
        description="Description",
        priority="high"
    )
    assert task.title == "Test Task"
    assert task.status in ("pending", "todo")
    assert str(task.priority) == "high"

@pytest.mark.asyncio
async def test_get_tasks(task_service, test_user):
    for i in range(3):
        await task_service.create_task(user_id=test_user.id, title=f"Task {i}")
    
    tasks = await task_service.get_user_tasks(user_id=test_user.id)
    assert len(tasks) == 3

@pytest.mark.asyncio
async def test_complete_task(task_service, test_user):
    task = await task_service.create_task(user_id=test_user.id, title="Test Task")
    completed = await task_service.complete_task(task.id)
    assert completed.status == "completed"

@pytest.mark.asyncio
async def test_delete_task(task_service, test_user):
    task = await task_service.create_task(user_id=test_user.id, title="Test Task")
    result = await task_service.delete_task(task.id)
    assert result is True
    
    tasks = await task_service.get_user_tasks(user_id=test_user.id)
    assert len(tasks) == 0
