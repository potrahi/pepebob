from datetime import datetime
from unittest.mock import MagicMock
import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from telegram import (
    Update, Message,
    Chat as TelegramChat, User
)
from bot.handlers.generic_handler import GenericHandler
from config import Config
from core.entities.base_entity import Base
from core.entities.chat_entity import Chat
from core.entities.pair_entity import Pair
from core.entities.reply_entity import Reply
from core.entities.word_entity import Word
from core.enums.chat_types import ChatType
from core.repositories.chat_repository import ChatRepository
from core.repositories.pair_repository import PairRepository
from core.repositories.reply_repository import ReplyRepository
from core.repositories.word_repository import WordRepository
from core.services.learn_service import LearnService
from core.services.story_service import StoryService


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
def chat_repo() -> ChatRepository:
    """
    Fixture to provide a ChatRepository instance.
    """
    return ChatRepository()


@pytest.fixture
def pair_repo() -> PairRepository:
    """
    Fixture to provide a PairRepository instance.
    """
    return PairRepository()


@pytest.fixture
def reply_repo() -> ReplyRepository:
    """
    Fixture to provide a ReplyRepository instance.
    """
    return ReplyRepository()


@pytest.fixture
def word_repo() -> WordRepository:
    """
    Fixture to provide a WordRepository instance.
    """
    return WordRepository()


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
    chat_entity = Chat(
        telegram_id=123,
        chat_type=ChatType.from_str("chat"),
        random_chance=5,
        created_at=created_date,
        updated_at=updated_date,
        name="Test chat"
    )
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


@pytest.fixture
def learn_service(dbsession: Session, word1: Word, word2: Word, chat: Chat) -> LearnService:
    """
    Fixture to provide a LearnService instance.
    """
    words = [word1.word, word2.word]
    end_sentence = [".", "!", "?"]
    return LearnService(
        words=words, chat_id=chat.id,
        session=dbsession, end_sentence=end_sentence)


@pytest.fixture
def story_service(word1: Word, word2: Word, chat: Chat, dbsession: Session) -> StoryService:
    """
    Fixture to provide a StoryService instance.
    """
    words = [word1.word, word2.word]
    context = ["contextword"]
    end_sentence = [".", "!", "?"]
    return StoryService(
        words=words, context=context, chat_id=chat.id,
        session=dbsession, end_sentence=end_sentence
    )


@pytest.fixture
def mock_update():
    user = User(id=123, first_name='Test', is_bot=False, username='testuser')
    telegram_chat = TelegramChat(id=456, type='private', title='Test Chat')
    message = Message(message_id=1, date=datetime.now(),
                      chat=telegram_chat, text="Test message", from_user=user)
    update = Update(update_id=1, message=message)
    return update


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_config():
    config = Config()
    config.bot.name = "TestBot"
    config.bot.anchors = ["hello", "test"]
    config.cache.host = "localhost"
    config.cache.port = 27017
    config.cache.name = "test_cache"
    config.end_sentence = [".", "!", "?"]
    return config
