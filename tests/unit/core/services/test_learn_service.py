"""
This module contains unit tests for the LearnService class.
"""

from sqlalchemy.orm import Session
from core.entities.chat_entity import Chat
from core.entities.word_entity import Word
from core.entities.pair_entity import Pair
from core.entities.reply_entity import Reply
from core.services.learn_service import LearnService


def test_learn_pair(learn_service: LearnService, dbsession: Session):
    """
    Test the learn_pair method to ensure it processes learning pairs and managing replies correctly.
    """
    learn_service.learn_pair()

    # Verify words were learned
    result_words = dbsession.query(Word).all()
    assert len(result_words) == 2
    assert {word.word for word in result_words} == set(learn_service.words)

    # Verify pairs and replies were created
    pairs = dbsession.query(Pair).all()
    replies = dbsession.query(Reply).all()

    assert len(pairs) >= 2
    assert len(replies) >= 2


def test_learn_pair_with_sentences(chat: Chat, dbsession: Session):
    """
    Test the learn_pair method with words ending in sentence delimiters.
    """
    words = ["hello", "world.", "goodbye", "world"]
    learn_service = LearnService(words=words, chat_id=chat.id, session=dbsession)
    learn_service.learn_pair()

    # Verify words were learned
    result_words = dbsession.query(Word).all()
    assert len(result_words) == 4
    assert {word.word for word in result_words} == set(learn_service.words)

    # Verify pairs and replies were created
    pairs = dbsession.query(Pair).all()
    replies = dbsession.query(Reply).all()

    assert len(pairs) >= 5
    assert len(replies) >= 5
