

from unittest.mock import MagicMock, Mock, PropertyMock, patch
import pytest
from telegram import Update

from bot.handlers.cool_story_handler import CoolStoryHandler
from config import Config
from core.services.story_service import StoryService


@pytest.fixture
def handler(mock_update: Update, mock_session: MagicMock, mock_config: Config):
    with patch.object(CoolStoryHandler, 'words', new_callable=PropertyMock) as mock_words, \
            patch.object(
                CoolStoryHandler, 'full_context', new_callable=PropertyMock
            ) as mock_full_context, \
            patch.object(CoolStoryHandler, 'chat', new_callable=PropertyMock) as mock_chat:

        mock_words.return_value = ["word1", "word2"]
        mock_full_context.return_value = ["context1", "context2"]
        mock_chat.return_value.id = 123

        return CoolStoryHandler(update=mock_update, session=mock_session, config=mock_config)


def test_initialization(handler: CoolStoryHandler):
    assert isinstance(handler.story_service, StoryService)
    assert handler.story_service.words == ["word1", "word2"]
    assert handler.story_service.context == ["context1", "context2"]
    assert handler.story_service.chat_id == 123
    assert handler.story_service.session == handler.session
    assert handler.story_service.end_sentence == handler.config.end_sentence
    assert handler.story_service.sentences == 50


@pytest.mark.asyncio
async def test_call(handler: CoolStoryHandler):
    handler.before = Mock()
    handler.story_service.generate = Mock(return_value="Generated Story")

    result = await handler.call()

    handler.before.assert_called_once()
    handler.story_service.generate.assert_called_once()
    assert result == "Generated Story"
