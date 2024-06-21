import json
from typing import Callable, Generator
from unittest.mock import MagicMock, AsyncMock
import pytest
from pytest_mock import MockerFixture
from telegram import Document, File
from telegram.error import NetworkError
from core.repositories.learn_queue_repository import LearnQueueRepository
from bot.handlers.import_history_handler import ImportHistoryHandler


@pytest.mark.asyncio
async def test_call_no_document(import_history_handler: ImportHistoryHandler):
    import_history_handler.document = None
    result = await import_history_handler.call()
    assert result == "No document attached. Please send a JSON file with the /learn command."


@pytest.mark.asyncio
async def test_call_json_decode_error(
        import_history_handler: ImportHistoryHandler,
        mocker: Callable[..., Generator[MockerFixture, None, None]]):
    mocker.patch.object(import_history_handler, 'process_json_file',
                        side_effect=json.JSONDecodeError("Expecting value", "doc", 0))
    result = await import_history_handler.call()
    assert result == "An error occurred: Expecting value: line 1 column 1 (char 0)"


@pytest.mark.asyncio
async def test_process_json_file_invalid_document(
        import_history_handler: ImportHistoryHandler,
        mocker: Callable[..., Generator[MockerFixture, None, None]]):
    mocker.patch.object(import_history_handler,
                        'is_valid_document', return_value=False)
    result = await import_history_handler.process_json_file()
    assert result == "Please send a valid JSON file with the /learn command."


@pytest.mark.asyncio
async def test_process_json_file_download_failure(
        import_history_handler: ImportHistoryHandler,
        mocker: Callable[..., Generator[MockerFixture, None, None]]):
    mocker.patch.object(import_history_handler,
                        'is_valid_document', return_value=True)
    mocker.patch.object(import_history_handler,
                        'download_file', return_value=None)
    result = await import_history_handler.process_json_file()
    assert result == "Failed to download the file."


@pytest.mark.asyncio
async def test_process_json_file_success(
        import_history_handler: ImportHistoryHandler,
        mocker: Callable[..., Generator[MockerFixture, None, None]]):
    telegram_file = MagicMock(spec=File)
    telegram_file.download_as_bytearray = AsyncMock(
        return_value=(
            b'{"messages": [{"id": 1, "date": "2023-01-01", '
            b'"from": "user", "text": "hello world", "type": "message"}]}'
        )
    )

    mocker.patch.object(import_history_handler,
                        'is_valid_document', return_value=True)
    mocker.patch.object(import_history_handler,
                        'download_file', return_value=telegram_file)
    mocker.patch.object(LearnQueueRepository, 'push')

    result = await import_history_handler.process_json_file()
    assert result == "Successfully processed 1 messages from provided JSON file."


@pytest.mark.asyncio
async def test_download_file_retry_success(import_history_handler: ImportHistoryHandler):
    document = MagicMock(spec=Document)
    file = MagicMock(spec=File)
    document.get_file = AsyncMock(return_value=file)
    import_history_handler.document = document

    result = await import_history_handler.download_file(retries=1)
    assert result == file


@pytest.mark.asyncio
async def test_download_file_retry_failure(import_history_handler: ImportHistoryHandler):
    document = MagicMock(spec=Document)
    document.get_file = AsyncMock(side_effect=NetworkError("Network error"))
    import_history_handler.document = document

    result = await import_history_handler.download_file(retries=1, delay=0)
    assert result is None


def test_is_valid_document(import_history_handler: ImportHistoryHandler):
    assert import_history_handler.is_valid_document() is True
    assert import_history_handler.document
    import_history_handler.document.mime_type = 'text/plain'
    assert import_history_handler.is_valid_document() is False


def test_extract_message_data(import_history_handler: ImportHistoryHandler):
    json_data = {
        "messages": [
            {"id": 1, "date": "2023-01-01", "from": "user1",
                "text": "hello world", "type": "message"},
            {"id": 2, "date": "2023-01-01", "from": "pepeground_bot",
                "text": "bot message", "type": "message"},
            {"id": 3, "date": "2023-01-01", "from": "user2",
                "text": "", "type": "message"},
            {"id": 4, "date": "2023-01-01", "from": "user3",
                "text": " ", "type": "message"}
        ]
    }
    result = import_history_handler.extract_message_data(json_data)
    assert len(result["messages"]) == 1
    assert result["messages"][0]["text"] == "hello world"


def test_extract_words(import_history_handler: ImportHistoryHandler):
    text = "hello world"
    result = import_history_handler.extract_words(text)
    assert result == ["hello", "world"]
