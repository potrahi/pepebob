import pytest
from unittest.mock import patch
from bot.handlers.set_gab_handler import SetGabHandler
from core.repositories.chat_repository import ChatRepository


@pytest.mark.asyncio
async def test_set_gab_handler_no_level(set_gab_handler: SetGabHandler):
    result = await set_gab_handler.call()
    assert result == "Level is required."


@pytest.mark.asyncio
async def test_set_gab_handler_invalid_level_high(set_gab_handler: SetGabHandler):
    result = await set_gab_handler.call(51)
    assert result == "0-50 allowed, Dude!"


@pytest.mark.asyncio
async def test_set_gab_handler_invalid_level_low(set_gab_handler: SetGabHandler):
    result = await set_gab_handler.call(-1)
    assert result == "0-50 allowed, Dude!"


@pytest.mark.asyncio
@patch.object(ChatRepository, 'update_random_chance')
async def test_set_gab_handler_valid_level(mock_update_random_chance, set_gab_handler: SetGabHandler):
    mock_update_random_chance.return_value = None
    result = await set_gab_handler.call(25)
    mock_update_random_chance.assert_called_once_with(
        set_gab_handler.session, set_gab_handler.chat.id, 25)
    assert result == "Ya wohl, Lord Helmet! Setting gab to 25"
