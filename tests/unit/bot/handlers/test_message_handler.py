from typing import Callable, Generator
from unittest.mock import MagicMock, PropertyMock
import pytest
from pytest_mock import MockerFixture
from bot.handlers.message_handler import MessageHandler


@pytest.mark.asyncio
async def test_call_no_text_or_edition(
        message_handler: MessageHandler,
        mocker: Callable[..., Generator[MockerFixture, None, None]]):
    mocker.patch.object(type(message_handler), 'has_text',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'is_edition',
                        new_callable=PropertyMock, return_value=True)
    result = await message_handler.call()
    assert result is None


@pytest.mark.asyncio
async def test_call_process_message(
        message_handler: MessageHandler,
        mocker: Callable[..., Generator[MockerFixture, None, None]]):
    mocker.patch.object(type(message_handler), 'before')
    mocker.patch.object(type(message_handler), 'has_text',
                        new_callable=PropertyMock, return_value=True)
    mocker.patch.object(type(message_handler), 'is_edition',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(message_handler, 'learn')
    mocker.patch.object(message_handler, 'context_repository')
    mock_story_service = mocker.patch.object(
        message_handler, 'story_service', new_callable=MagicMock)
    mocker.patch.object(
        message_handler, 'should_generate_story', return_value=True)
    mock_story_service.generate.return_value = "Generated story"

    result = await message_handler.call()
    assert result == "Generated story"


@pytest.mark.asyncio
async def test_call_no_story_service(
        message_handler: MessageHandler,
        mocker: Callable[..., Generator[MockerFixture, None, None]]):
    mocker.patch.object(type(message_handler), 'before')
    mocker.patch.object(type(message_handler), 'has_text',
                        new_callable=PropertyMock, return_value=True)
    mocker.patch.object(type(message_handler), 'is_edition',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(message_handler, 'learn')
    mocker.patch.object(message_handler, 'context_repository')
    mocker.patch.object(message_handler, 'story_service', None)

    result = await message_handler.call()
    assert result is None


@pytest.mark.asyncio
async def test_call_no_story_generated(
        message_handler: MessageHandler,
        mocker: Callable[..., Generator[MockerFixture, None, None]]):
    mocker.patch.object(type(message_handler), 'before')
    mocker.patch.object(type(message_handler), 'has_text',
                        new_callable=PropertyMock, return_value=True)
    mocker.patch.object(type(message_handler), 'is_edition',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(message_handler, 'learn')
    mocker.patch.object(message_handler, 'context_repository')
    mocker.patch.object(message_handler, 'story_service',
                        new_callable=MagicMock)
    mocker.patch.object(
        message_handler, 'should_generate_story', return_value=False)

    result = await message_handler.call()
    assert result is None


def test_learn_sync(
        message_handler: MessageHandler,
        mocker: Callable[..., Generator[MockerFixture, None, None]]):
    mocker.patch.object(message_handler, 'config')
    mocker.patch.object(message_handler, 'learn_service')
    message_handler.config.bot.async_learn = False

    message_handler.learn()
    message_handler.learn_service.learn_pair.assert_called_once()


def test_learn_async(
        message_handler: MessageHandler,
        mocker: Callable[..., Generator[MockerFixture, None, None]]):
    mocker.patch.object(message_handler, 'config')
    mocker.patch.object(message_handler, 'learn_service')
    mock_push = mocker.patch(
        'core.repositories.learn_queue_repository.LearnQueueRepository.push')
    message_handler.config.bot.async_learn = True

    message_handler.learn()
    mock_push.assert_called_once_with(
        message_handler.words, message_handler.chat.id)


def test_should_generate_story(
        message_handler: MessageHandler,
        mocker: Callable[..., Generator[MockerFixture, None, None]]):
    mocker.patch.object(type(message_handler), 'is_reply_to_bot',
                        new_callable=PropertyMock, return_value=True)
    assert message_handler.should_generate_story() == True

    mocker.patch.object(type(message_handler), 'is_reply_to_bot',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'is_mentioned',
                        new_callable=PropertyMock, return_value=True)
    assert message_handler.should_generate_story() == True

    mocker.patch.object(type(message_handler), 'is_reply_to_bot',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'is_mentioned',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'is_private',
                        new_callable=PropertyMock, return_value=True)
    assert message_handler.should_generate_story() == True

    mocker.patch.object(type(message_handler), 'is_reply_to_bot',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'is_mentioned',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'is_private',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'has_anchors',
                        new_callable=PropertyMock, return_value=True)
    assert message_handler.should_generate_story() == True

    mocker.patch.object(type(message_handler), 'is_reply_to_bot',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'is_mentioned',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'is_private',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'has_anchors',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'is_random_answer',
                        new_callable=PropertyMock, return_value=True)
    assert message_handler.should_generate_story() == True

    mocker.patch.object(type(message_handler), 'is_reply_to_bot',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'is_mentioned',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'is_private',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'has_anchors',
                        new_callable=PropertyMock, return_value=False)
    mocker.patch.object(type(message_handler), 'is_random_answer',
                        new_callable=PropertyMock, return_value=False)
    assert message_handler.should_generate_story() == False
