"""
This module contains unit tests for the PairRepository class.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from core.entities.chat_entity import Chat
from core.entities.pair_entity import Pair
from core.entities.reply_entity import Reply
from core.entities.word_entity import Word
from core.repositories.pair_repository import PairRepository


def test_get_pair_or_create_by(
        pair_repo: PairRepository, chat: Chat, word1: Word, word2: Word, dbsession: Session):
    """
    Test the retrieval and creation of a pair using get_pair_or_create_by.
    """
    result = pair_repo.get_pair_or_create_by(
        dbsession, chat.id, word1.id, word2.id)
    assert result is not None
    assert result.chat_id == chat.id
    assert result.first_id == word1.id
    assert result.second_id == word2.id

    result_existing = pair_repo.get_pair_or_create_by(
        dbsession, chat.id, word1.id, word2.id)
    assert result_existing is not None
    assert result_existing.id == result.id


def test_has_with_word_id(pair_repo: PairRepository, pair: Pair, dbsession: Session):
    """
    Test the has_with_word_id method to check if a pair exists with the given word ID.
    """
    result = pair_repo.has_with_word_id(dbsession, pair.first_id)
    assert result is True


def test_get_pair_with_replies(
        pair_repo: PairRepository, pair: Pair, reply: Reply,
        chat: Chat, word1: Word, word2: Word, dbsession: Session):
    """
    Test the get_pair_with_replies method to retrieve pairs with replies.
    """
    result = pair_repo.get_pair_with_replies(
        dbsession, pair.chat_id, pair.first_id, [pair.second_id]
    )
    assert len(result) == 1
    assert result[0].chat_id == chat.id
    assert result[0].first_id == word1.id
    assert result[0].second_id == word2.id


def test_touch(pair_repo: PairRepository, dbsession: Session):
    """
    Test the touch method to update the updated_at timestamp of pairs.
    """
    pair = Pair(chat_id=1, first_id=1, second_id=2,
                updated_at=datetime.now() - timedelta(days=1))
    dbsession.add(pair)
    dbsession.commit()

    pair_repo.touch(dbsession, [pair.id])
    updated_pair = dbsession.query(Pair).filter_by(id=pair.id).first()

    assert updated_pair is not None
    assert updated_pair.updated_at > datetime.now() - timedelta(hours=1)


def test_get_pairs_count(pair_repo: PairRepository, dbsession: Session):
    """
    Test the get_pairs_count method to count the number of pairs for a given chat ID.
    """
    pair1 = Pair(chat_id=1, first_id=1, second_id=2)
    pair2 = Pair(chat_id=1, first_id=2, second_id=3)
    dbsession.add(pair1)
    dbsession.add(pair2)
    dbsession.commit()

    count = pair_repo.get_pairs_count(dbsession, 1)
    assert count == 2


def test_remove_old(
        pair_repo: PairRepository, chat: Chat, word1: Word,
        word2: Word, dbsession: Session):
    """
    Test the remove_old method to remove pairs that haven't been updated recently.
    """
    old_pair = Pair(chat_id=chat.id, first_id=word1.id, second_id=word2.id,
                    updated_at=datetime.now() - timedelta(days=100))
    recent_pair = Pair(chat_id=chat.id, first_id=word2.id,
                       second_id=word1.id, updated_at=datetime.now())
    dbsession.add(old_pair)
    dbsession.add(recent_pair)
    dbsession.commit()

    old_pair_id = old_pair.id
    recent_pair_id = recent_pair.id

    removed_ids = pair_repo.remove_old(dbsession, 10)
    assert old_pair_id in removed_ids
    assert recent_pair_id not in removed_ids
