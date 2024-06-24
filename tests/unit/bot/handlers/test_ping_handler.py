import pytest
from bot.handlers.ping_handler import PingHandler


@pytest.mark.asyncio
async def test_ping_handler_call(ping_handler: PingHandler):
    result = await ping_handler.call()
    assert result == "Pong."
