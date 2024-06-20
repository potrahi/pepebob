from datetime import datetime
from unittest.mock import MagicMock, Mock, PropertyMock, patch
from telegram import (
    Message, MessageEntity, User, Chat as TelegramChat)
from core.repositories.chat_repository import ChatRepository
from core.entities.chat_entity import Chat
from conftest import TestGenericHandler


def test_is_chat_changed(handler: TestGenericHandler):
    with patch.object(
            TestGenericHandler, 'chat_name', new_callable=PropertyMock
    ) as mock_chat_name, \
            patch.object(
                TestGenericHandler, 'telegram_id', new_callable=PropertyMock
    ) as mock_telegram_id, \
            patch.object(
                TestGenericHandler, 'migration_id', new_callable=PropertyMock
    ) as mock_migration_id:
        mock_chat_name.return_value = "Old Name"
        handler.chat.name = "New Name"
        mock_telegram_id.return_value = 123
        mock_migration_id.return_value = 798

        assert handler.is_chat_changed


def test_is_private(handler: TestGenericHandler):
    assert handler.is_private


def test_is_random_answer(handler: TestGenericHandler):
    handler.chat.random_chance = 100
    assert handler.is_random_answer


def test_is_reply_to_bot(handler: TestGenericHandler):
    assert handler.message

    reply_user = User(id=456, first_name='Bot',
                      is_bot=True, username="TestBot")
    reply_chat = TelegramChat(id=789, type='private')
    reply_message = Message(
        message_id=2, date=datetime.now(), chat=reply_chat,
        from_user=reply_user, text="Reply message"
    )

    message_mock = Mock()
    type(message_mock).reply_to_message = PropertyMock(
        return_value=reply_message)
    handler.message = message_mock

    assert handler.is_reply_to_bot


def test_has_anchors(handler: TestGenericHandler):
    assert handler.message

    # Mock the message to include the anchor text
    message_mock = Mock()
    type(message_mock).text = PropertyMock(return_value="hello there")
    handler.message = message_mock

    # Assert that has_anchors returns True
    assert handler.has_anchors


def test_has_entities(handler: TestGenericHandler):
    assert handler.message

    # Create a mock message entity
    mock_entities = (MessageEntity(type="mention", offset=0, length=6),)

    # Mock the entities property
    message_mock = Mock()
    type(message_mock).entities = PropertyMock(return_value=mock_entities)
    handler.message = message_mock

    # Assert that has_entities returns True
    assert handler.has_entities


def test_is_edition(handler: TestGenericHandler):
    assert handler.message

    # Create a mock message
    message_mock = Mock()
    type(message_mock).edit_date = PropertyMock(return_value=datetime.now())
    handler.message = message_mock

    # Assert that is_edition returns True
    assert handler.is_edition


def test_has_text(handler: TestGenericHandler):
    assert handler.has_text


def test_is_mentioned(handler: TestGenericHandler):
    assert handler.message

    # Create a mock message
    message_mock = Mock()
    type(message_mock).text = PropertyMock(return_value="@testbot")
    handler.message = message_mock

    # Assert that is_mentioned returns True
    assert handler.is_mentioned


def test_is_command(handler: TestGenericHandler):
    assert handler.message

    # Create a mock message
    message_mock = Mock()
    type(message_mock).text = PropertyMock(return_value="/start")
    handler.message = message_mock

    # Assert that is_command returns True
    assert handler.is_command


def test_get_words(handler: TestGenericHandler):
    words = handler.get_words("This is a test sentence.")
    assert words == ["this", "is", "a", "test", "sentence."]


def test_chat(handler: TestGenericHandler):
    chat_entity = Chat(id=1, telegram_id=456, chat_type="chat", name="Test Chat")
    
    with patch('core.repositories.chat_repository.ChatRepository.get_or_create_by', return_value=chat_entity):
        assert handler.chat == chat_entity


def test_telegram_id(handler: TestGenericHandler):
    assert handler.telegram_id == 456


def test_migration_id(handler: TestGenericHandler):
    assert handler.migration_id == 456


def test_chat_type(handler: TestGenericHandler):
    assert handler.chat_type == "chat"


def test_chat_name(handler: TestGenericHandler):
    assert handler.chat_name == "Test Chat"


def test_from_username(handler: TestGenericHandler):
    assert handler.message
    
    # Create a mock user
    user_mock = Mock(spec=User)
    type(user_mock).username = PropertyMock(return_value="Test")
    
    # Create a mock message
    message_mock = Mock(spec=Message)
    type(message_mock).from_user = PropertyMock(return_value=user_mock)
    
    handler.message = message_mock

    # Assert that from_username returns "Test"
    assert handler.from_username == "Test"


def test_get_context(handler: TestGenericHandler):
    handler.context_repository.get_context = MagicMock(
        return_value=["context1", "context2"]
    )
    
    with patch('random.sample', return_value=["context1", "context2"]):
        context = handler.get_context(2)
        assert context == ["context1", "context2"]


def test_context(handler: TestGenericHandler):
    handler.context_repository.get_context = MagicMock(
        return_value=["context1", "context2"]
    )
    
    with patch('random.sample', return_value=["context1", "context2"]):
        context = handler.context
        assert context == ["context1", "context2"]


def test_full_context(handler: TestGenericHandler):
    handler.context_repository.get_context = MagicMock(
        return_value=["context1", "context2"]
    )
    
    with patch('random.sample', return_value=["context1", "context2"]):
        full_context = handler.full_context
        assert full_context == ["context1", "context2"]


def test_words(handler: TestGenericHandler):
    words = handler.words
    assert words == ["test", "message"]


def test_text(handler: TestGenericHandler):
    assert handler.text == "Test message"


def test_chat_context(handler: TestGenericHandler):
    with patch.object(TestGenericHandler, 'chat', new_callable=PropertyMock) as mock_chat:
        mock_chat.return_value = Chat(id=1)
        assert handler.chat_context == "chat_context/1"
