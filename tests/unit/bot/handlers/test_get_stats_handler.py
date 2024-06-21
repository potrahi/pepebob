from unittest.mock import Mock, MagicMock, patch, PropertyMock
import pytest
from telegram import Update
from bot.handlers.get_stats_handler import GetStatsHandler
from core.repositories.pair_repository import PairRepository
from config import Config


@pytest.fixture
def handler(mock_update: Update, mock_session: MagicMock, mock_config: Config):
    return GetStatsHandler(update=mock_update, session=mock_session, config=mock_config)

@pytest.mark.asyncio
async def test_call(handler: GetStatsHandler):
    handler.before = Mock()  # Mock the before method

    mock_chat = MagicMock()
    mock_chat.id = 123
    
    with patch.object(GetStatsHandler, 'chat', new_callable=PropertyMock, return_value=mock_chat):
        with patch.object(PairRepository, 'get_pairs_count', return_value=42) as mock_get_pairs_count:
            result = await handler.call()

            handler.before.assert_called_once()
            mock_get_pairs_count.assert_called_once_with(handler.session, 123)
            assert result == "Known pairs in this chat: 42."
