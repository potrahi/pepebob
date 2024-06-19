from datetime import datetime
import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from core.entities.base_entity import Base
from core.entities.chat_entity import Chat
from core.entities.pair_entity import Pair
from core.entities.reply_entity import Reply
from core.entities.word_entity import Word
from core.enums.chat_types import ChatType
from core.repositories.chat_repository import ChatRepository
from core.repositories.pair_repository import PairRepository


@pytest.fixture(scope='module')
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope='module')
def tables(engine: Engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(scope='function')
def dbsession(engine: Engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    session_obj = sessionmaker(bind=connection)
    session = session_obj()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def pair_repo():
    """
    Fixture to provide a PairRepository instance.
    """
    return PairRepository()


@pytest.fixture
def chat_repo():
    return ChatRepository()


@pytest.fixture
def word1(dbsession: Session) -> Word:
    """
    Fixture to create and provide a Word entity.
    """
    word = Word(word="word1")
    dbsession.add(word)
    dbsession.commit()
    return word


@pytest.fixture
def word2(dbsession: Session) -> Word:
    """
    Fixture to create and provide a Word entity.
    """
    word = Word(word="word2")
    dbsession.add(word)
    dbsession.commit()
    return word


@pytest.fixture
def chat(dbsession: Session) -> Chat:
    """
    Fixture to create and provide a Chat entity.
    """
    created_date = datetime(2023, 1, 2, 0, 0, 0)
    updated_date = datetime(2023, 1, 2, 0, 0, 0)
    chat_entity = Chat(telegram_id=123, chat_type=ChatType.from_str("chat"), random_chance=5,
                       created_at=created_date, updated_at=updated_date, name="Test chat")
    dbsession.add(chat_entity)
    dbsession.commit()
    return chat_entity


@pytest.fixture
def pair(dbsession: Session, chat: Chat, word1: Word, word2: Word) -> Pair:
    created_date = datetime(2023, 1, 2, 0, 0, 0)
    pair_entity = Pair(chat_id=chat.id, first_id=word1.id,
                       second_id=word2.id, created_at=created_date)
    dbsession.add(pair_entity)
    dbsession.commit()
    return pair_entity


@pytest.fixture
def reply(dbsession: Session, pair: Pair, word1: Word) -> Reply:
    reply_entity = Reply(pair_id=pair.id, word_id=word1.id, count=1)
    dbsession.add(reply_entity)
    dbsession.commit()
    return reply_entity
