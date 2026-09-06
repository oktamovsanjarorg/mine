import pytest
from unittest.mock import AsyncMock
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.handlers.common import cmd_start, cmd_help

@pytest.mark.asyncio
async def test_cmd_start(mock_bot):
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock()
    message.from_user.first_name = "Sanjar"
    message.from_user.full_name = "Sanjar"
    message.from_user.id = 7537966029
    message.answer = AsyncMock()
    
    await cmd_start(message)
    assert message.answer.call_count >= 1
    args = message.answer.call_args_list[0][0][0]
    assert "Assalomu alaykum" in args or "Salom" in args

@pytest.mark.asyncio
async def test_cmd_help(mock_bot):
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    
    await cmd_help(message)
    message.answer.assert_called_once()
