import pytest
from sqlalchemy.orm.session import Session
from core.entities.chat_entity import Chat
from core.enums.chat_types import ChatType
from core.repositories.chat_repository import ChatRepository


def test_get_or_create_by_existing_chat(
    chat_repo: ChatRepository, chat: Chat, dbsession: Session):
    
    result = chat_repo.get_or_create_by(
        dbsession, telegram_id=123, name="Test Chat", chat_type="group")

    assert result == chat


def test_get_or_create_by_new_chat(chat_repo: ChatRepository, dbsession: Session):
    result = chat_repo.get_or_create_by(
        dbsession, telegram_id=123, name="Test Chat", chat_type="group")

    assert result.telegram_id == 123
    assert result.name == "Test Chat"
    assert result.chat_type == ChatType.from_str('chat')


def test_update_random_chance(
    chat_repo: ChatRepository, chat: Chat, dbsession: Session):
    chat_repo.update_random_chance(dbsession, chat_id=chat.id, random_chance=50)

    updated_chat = dbsession.query(Chat).filter_by(id=chat.id).first()

    assert updated_chat is not None
    assert updated_chat.random_chance == 50


def test_update_chat(
    chat_repo: ChatRepository, chat: Chat, dbsession: Session):
    chat_repo.update_chat(dbsession, chat_id=chat.id,
                          name="Updated Chat", telegram_id=456)

    updated_chat = dbsession.query(Chat).filter_by(id=chat.id).first()

    assert updated_chat is not None
    assert updated_chat.name == "Updated Chat"
    assert updated_chat.telegram_id == 456


def test_create_chat(chat_repo: ChatRepository, dbsession: Session):
    result = chat_repo._create(
        dbsession, telegram_id=123, name="Test Chat", chat_type="group")

    assert result.telegram_id == 123
    assert result.name == "Test Chat"
    assert result.chat_type == ChatType.from_str('chat')


def test_create_chat_failure(
    chat_repo: ChatRepository, chat: Chat, dbsession: Session):
    with pytest.raises(
        ValueError, match=f"Chat with telegram_id {chat.telegram_id} already exists"):
        chat_repo._create(dbsession, telegram_id=123,
                          name="Test Chat", chat_type="group")


def test_get_by_telegram_id(
    chat_repo: ChatRepository, chat: Chat, dbsession: Session):
    result = chat_repo._get_by_telegram_id(dbsession, telegram_id=123)

    assert result == chat
