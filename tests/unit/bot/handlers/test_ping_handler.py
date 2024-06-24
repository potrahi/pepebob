from sqlalchemy.orm import Session
from telegram import Update
import pytest
from bot.handlers.ping_handler import PingHandler
from config import Config

@pytest.fixture
def ping_handler(mock_update: Update, mock_session: Session, mock_config: Config):
    return PingHandler(update=mock_update, session=mock_session, config=mock_config)

@pytest.mark.asyncio
async def test_ping_handler_call(ping_handler: PingHandler):
    result = await ping_handler.call()
    assert result == "Pong."
