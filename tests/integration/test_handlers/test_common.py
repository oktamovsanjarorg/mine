import pytest
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.api.handlers.common import cmd_start, cmd_help

@pytest.mark.asyncio
async def test_cmd_start(mock_bot):
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock()
    message.from_user.full_name = "Sanjar"
    message.answer = AsyncMock()
    
    await cmd_start(message)
    message.answer.assert_called_once()
    args = message.answer.call_args[0][0]
    assert "Assalomu alaykum" in args or "Salom" in args

@pytest.mark.asyncio
async def test_cmd_help(mock_bot):
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    
    await cmd_help(message)
    message.answer.assert_called_once()
