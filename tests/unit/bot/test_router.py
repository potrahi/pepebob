from typing import Callable, Generator
from unittest.mock import MagicMock, patch, AsyncMock
from sqlalchemy.orm import Session
import pytest
from pytest_mock import MockerFixture
from telegram import Chat, Update, Document, Message
from telegram.ext import Application, CallbackContext
from bot.router import Router
from bot.handlers import (
    import_history_handler, message_handler,
)
from bot.handlers.generic_handler import GenericHandler
from config import Config


def test_router_init(router: Router, mock_config: Config, mock_session: Session):
    assert router.config == mock_config
    assert router.session == mock_session
    assert isinstance(router.application, Application)


def test_router_add_handlers(router: Router):
    with patch.object(router.application, 'add_handler') as mock_add_handler:
        router.add_handlers()
        assert mock_add_handler.call_count == 8


@pytest.mark.asyncio
async def test_handle_command(
        router: Router, mock_update: Update, mock_session: Session,
        mock_config: Config, mocker: Callable[..., Generator[MockerFixture, None, None]]):
    handler_class = MagicMock(spec=GenericHandler)
    handler_class.__name__ = "TestHandler"
    handler_instance = handler_class.return_value
    handler_instance.call = AsyncMock(return_value="Response")

    mocker.patch.object(router, 'send_response')
    mocker.patch.object(
        router, 'handle_command',
        wraps=router.handle_command
    )

    await router.handle_command(mock_update, MagicMock(spec=CallbackContext), handler_class)

    handler_class.assert_called_once_with(
        mock_update, mock_session, mock_config)
    handler_instance.call.assert_called_once()
    router.send_response.assert_called_once()


@pytest.mark.asyncio
async def test_import_history(
        router: Router, mock_update: Update,
        mocker: Callable[..., Generator[MockerFixture, None, None]]):
    # Create the mock objects
    mock_message = MagicMock(spec=Message)
    mock_document = MagicMock(spec=Document)
    mock_message.document = mock_document
    mock_chat = MagicMock(spec=Chat)
    mock_chat.id = 456
    mock_message.chat = mock_chat

    # Create a new Update instance with the mock message
    mock_update = Update(update_id=1, message=mock_message)

    # Create a MagicMock for CallbackContext
    mock_callback_context = MagicMock(spec=CallbackContext)

    mocker.patch.object(router, 'handle_command')

    await router.import_history(mock_update, mock_callback_context)

    assert mock_update.message is not None
    router.handle_command.assert_called_once_with(
        mock_update, mock_callback_context,
        import_history_handler.ImportHistoryHandler,
        document=mock_update.message.document
    )


@pytest.mark.asyncio
async def test_set_gab_valid_level(router: Router, mocker):
    # Create the mock objects
    mock_chat = MagicMock(spec=Chat)
    mock_chat.id = 123
    mock_message = MagicMock(spec=Message)
    mock_message.text = "/set_gab 25"
    mock_message.chat_id = mock_chat.id
    mock_message.chat = mock_chat

    # Create a new Update instance with the mock message
    mock_update = Update(update_id=1, message=mock_message)

    # Create a MagicMock for CallbackContext
    mock_context = MagicMock(spec=CallbackContext)
    mock_context.args = ["25"]

    # Patch the router's send_response method
    mocker.patch.object(router, 'send_response')

    # Call the method under test
    await router.set_gab(mock_update, mock_context)

    # Assert the send_response method was called once with the correct arguments
    router.send_response.assert_called_once_with(
        mock_context, mock_chat.id, "Ya wohl, Lord Helmet! Setting gab to 25"
    )


@pytest.mark.asyncio
async def test_set_gab_invalid_level(router: Router, mocker):
    # Create the mock objects
    mock_chat = MagicMock(spec=Chat)
    mock_chat.id = 123
    mock_message = MagicMock(spec=Message)
    mock_message.text = "/set_gab 100"
    mock_message.chat_id = mock_chat.id
    mock_message.chat = mock_chat

    # Create a new Update instance with the mock message
    mock_update = Update(update_id=1, message=mock_message)

    # Create a MagicMock for CallbackContext
    mock_context = MagicMock(spec=CallbackContext)
    mock_context.args = ["100"]

    # Patch the router's send_response method
    mocker.patch.object(router, 'send_response')

    # Call the method under test
    await router.set_gab(mock_update, mock_context)

    # Assert the send_response method was called once with the correct arguments
    router.send_response.assert_called_once_with(
        mock_context, mock_chat.id, "0-50 allowed, Dude!"
    )


@pytest.mark.asyncio
async def test_handle_message(router: Router, mocker):
    # Create the mock objects
    mock_chat = MagicMock(spec=Chat)
    mock_chat.id = 123
    mock_message = MagicMock(spec=Message)
    mock_message.chat_id = mock_chat.id
    mock_message.chat = mock_chat

    # Create a new Update instance with the mock message
    mock_update = Update(update_id=1, message=mock_message)

    # Create a MagicMock for CallbackContext
    mock_callback_context = MagicMock(spec=CallbackContext)

    # Create a mock handler instance
    handler_instance = MagicMock(spec=message_handler.MessageHandler)
    handler_instance.call = AsyncMock(return_value="Response")

    # Patch the MessageHandler and the router's send_response method
    mocker.patch('bot.handlers.message_handler.MessageHandler',
                 return_value=handler_instance)
    mocker.patch.object(router, 'send_response')

    # Call the method under test
    await router.handle_message(mock_update, mock_callback_context)

    # Assert the handler's call method was called once
    handler_instance.call.assert_called_once()

    # Assert the send_response method was called once with the correct arguments
    router.send_response.assert_called_once_with(
        mock_callback_context, mock_chat.id, "Response"
    )
