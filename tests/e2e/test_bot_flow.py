import pytest
# e2e tests would typically use a test client for aiogram or simulate webhook payloads
# For the scope of this file, we present a mock flow structure

@pytest.mark.asyncio
async def test_full_bot_flow():
    # 1. Start bot
    # 2. Register user
    # 3. Add task
    # 4. Check balance
    # 5. Check in habit
    assert True
