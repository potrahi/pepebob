"""
This module contains unit tests for the ChatType class.
"""

from core.enums.chat_types import ChatType


def test_chat_type_chat():
    """
    Test the from_str method with the 'chat' string.
    """
    assert ChatType.from_str("chat") == 0


def test_chat_type_faction():
    """
    Test the from_str method with the 'faction' string.
    """
    assert ChatType.from_str("faction") == 1


def test_chat_type_supergroup():
    """
    Test the from_str method with the 'supergroup' string.
    """
    assert ChatType.from_str("supergroup") == 2


def test_chat_type_channel():
    """
    Test the from_str method with the 'channel' string.
    """
    assert ChatType.from_str("channel") == 3


def test_chat_type_invalid():
    """
    Test the from_str method with an invalid string.
    """
    assert ChatType.from_str("invalid") == 0


def test_chat_type_empty():
    """
    Test the from_str method with an empty string.
    """
    assert ChatType.from_str("") == 0


def test_chat_type_none():
    """
    Test the from_str method with None.
    """
    assert ChatType.from_str(None) == 0 # type: ignore
