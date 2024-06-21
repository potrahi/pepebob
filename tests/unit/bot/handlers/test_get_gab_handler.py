from unittest.mock import Mock, MagicMock, PropertyMock, patch
import pytest
from telegram import Update
from bot.handlers.get_gab_handler import GetGabHandler
from config import Config


@pytest.fixture
def handler(mock_update: Update, mock_session: MagicMock, mock_config: Config):
    return GetGabHandler(update=mock_update, session=mock_session, config=mock_config)

@pytest.mark.asyncio
async def test_call(handler: GetGabHandler):
    handler.before = Mock()  # Mock the before method

    mock_chat = MagicMock()
    type(mock_chat).random_chance = PropertyMock(return_value=42)
    
    with patch.object(GetGabHandler, 'chat', new_callable=PropertyMock, return_value=mock_chat):
        result = await handler.call()

        handler.before.assert_called_once()
        assert result == "Pizdlivost level is on 42"
