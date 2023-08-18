import pytest
from unittest.mock import MagicMock, AsyncMock
from aiogram import types

from handlers import start_command


@pytest.mark.asyncio
async def test_start_command():
    message = MagicMock(spec=types.Message)
    message.from_user.first_name = "John"

    # AsyncMock для message.delete()
    delete_mock = AsyncMock()
    message.delete = delete_mock

    await start_command(message)

    message.answer.assert_called_once()
    delete_mock.assert_awaited_once()
