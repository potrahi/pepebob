from datetime import datetime
import pytest
from sqlalchemy.orm.session import Session
from core.entities.chat_entity import Chat
from core.entities.word_entity import Word
from core.entities.pair_entity import Pair
from core.entities.reply_entity import Reply
from core.enums.chat_types import ChatType
from core.repositories.chat_repository import ChatRepository


@pytest.fixture
def chat_repo():
    return ChatRepository()


def test_get_or_create_by_existing_chat(chat_repo: ChatRepository, dbsession: Session):
    created_date = datetime(2023, 3, 1, 0, 0, 0)
    updated_date = datetime(2023, 3, 1, 0, 0, 0)
    chat = Chat(
        id=1, telegram_id=123, name="Test Chat",
        chat_type=ChatType.from_str('chat'), created_at=created_date,
        updated_at=updated_date
    )

    dbsession.add(chat)
    dbsession.commit()

    result = chat_repo.get_or_create_by(
        dbsession, telegram_id=123, name="Test Chat", chat_type="group")

    assert result == chat


def test_get_or_create_by_new_chat(chat_repo: ChatRepository, dbsession: Session):
    result = chat_repo.get_or_create_by(
        dbsession, telegram_id=123, name="Test Chat", chat_type="group")

    assert result.telegram_id == 123
    assert result.name == "Test Chat"
    assert result.chat_type == ChatType.from_str('chat')


def test_update_random_chance(chat_repo: ChatRepository, dbsession: Session):
    created_date = datetime(2023, 3, 1, 0, 0, 0)
    updated_date = datetime(2023, 3, 1, 0, 0, 0)

    chat = Chat(id=1, telegram_id=123, name="Test Chat",
                chat_type=ChatType.from_str('chat'), random_chance=10,
                created_at=created_date, updated_at=updated_date)
    dbsession.add(chat)
    dbsession.commit()

    chat_repo.update_random_chance(dbsession, chat_id=1, random_chance=50)

    updated_chat = dbsession.query(Chat).filter_by(id=1).first()

    assert updated_chat
    assert updated_chat.random_chance == 50


def test_update_chat(chat_repo: ChatRepository, dbsession: Session):
    created_date = datetime(2023, 3, 1, 0, 0, 0)
    updated_date = datetime(2023, 3, 1, 0, 0, 0)

    chat = Chat(id=1, telegram_id=123, name="Test Chat",
                chat_type=ChatType.from_str('chat'),
                created_at=created_date, updated_at=updated_date)
    dbsession.add(chat)
    dbsession.commit()

    chat_repo.update_chat(dbsession, chat_id=1,
                          name="Updated Chat", telegram_id=456)

    updated_chat = dbsession.query(Chat).filter_by(id=1).first()

    assert updated_chat
    assert updated_chat.name == "Updated Chat"
    assert updated_chat.telegram_id == 456


def test_create_chat(chat_repo: ChatRepository, dbsession: Session):
    result = chat_repo._create(
        dbsession, telegram_id=123, name="Test Chat", chat_type="group")

    assert result.telegram_id == 123
    assert result.name == "Test Chat"
    assert result.chat_type == ChatType.from_str('chat')


def test_create_chat_failure(chat_repo: ChatRepository, dbsession: Session):
    existing_chat = Chat(
        telegram_id=321,
        name="Existing Chat",
        chat_type=ChatType.from_str('group'),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    dbsession.add(existing_chat)
    dbsession.commit()

    with pytest.raises(
        ValueError, match=f"Chat with telegram_id {existing_chat.telegram_id} already exists"):
        chat_repo._create(dbsession, telegram_id=321,
                          name="Test Chat", chat_type="group")


def test_get_by_telegram_id(chat_repo: ChatRepository, dbsession: Session):
    created_date = datetime(2023, 3, 1, 0, 0, 0)
    updated_date = datetime(2023, 3, 1, 0, 0, 0)

    chat = Chat(id=1, telegram_id=123, name="Test Chat",
                chat_type=ChatType.from_str('chat'),
                created_at=created_date, updated_at=updated_date)
    dbsession.add(chat)
    dbsession.commit()

    result = chat_repo._get_by_telegram_id(dbsession, telegram_id=123)

    assert result == chat
