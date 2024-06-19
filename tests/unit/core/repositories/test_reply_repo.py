"""
This module contains unit tests for the ReplyRepository class.
"""

from sqlalchemy.orm import Session
from core.entities.pair_entity import Pair
from core.entities.reply_entity import Reply
from core.entities.word_entity import Word
from core.repositories.reply_repository import ReplyRepository


def test_has_with_word_id(reply_repo: ReplyRepository, word1: Word, pair: Pair, dbsession: Session):
    """
    Test the has_with_word_id method to check if a reply exists with the given word ID.
    """
    create_reply(dbsession, pair.id, word1.id)
    result = reply_repo.has_with_word_id(dbsession, word1.id)
    assert result is True


def test_replies_for_pair(
        reply_repo: ReplyRepository, pair: Pair,
        word1: Word, word2: Word, dbsession: Session):
    """
    Test the replies_for_pair method to retrieve top replies for a given pair ID.
    """
    create_reply(dbsession, pair.id, word1.id, count=5)
    create_reply(dbsession, pair.id, word2.id, count=3)
    result = reply_repo.replies_for_pair(dbsession, pair.id)
    assert len(result) == 2
    assert result[0].count == 5
    assert result[1].count == 3


def test_increment_reply(reply_repo: ReplyRepository, pair: Pair, word1: Word, dbsession: Session):
    """
    Test the increment_reply method to increment the reply count.
    """
    reply = create_reply(dbsession, pair.id, word1.id, count=1)
    reply_repo.increment_reply(dbsession, reply.id, reply.count)
    updated_reply = dbsession.query(Reply).filter_by(id=reply.id).first()
    assert updated_reply is not None
    assert updated_reply.count == 2


def test_get_reply_by(reply_repo: ReplyRepository, pair: Pair, word1: Word, dbsession: Session):
    """
    Test the get_reply_by method to retrieve a reply by pair ID and word ID.
    """
    reply = create_reply(dbsession, pair.id, word1.id)
    result = reply_repo.get_reply_by(dbsession, pair.id, word1.id)
    assert result is not None
    assert result.pair_id == pair.id
    assert result.word_id == word1.id


def test_create_reply_by(reply_repo: ReplyRepository, pair: Pair, word1: Word, dbsession: Session):
    """
    Test the create_reply_by method to create a new reply.
    """
    result = reply_repo.create_reply_by(dbsession, pair.id, word1.id)
    assert result is not None
    assert result.pair_id == pair.id
    assert result.word_id == word1.id


# Helper function to create a reply
def create_reply(dbsession: Session, pair_id: int, word_id: int, count: int = 1) -> Reply:
    reply = Reply(pair_id=pair_id, word_id=word_id, count=count)
    dbsession.add(reply)
    dbsession.commit()
    return reply
