"""
This module contains unit tests for the LearnService class.
"""

from sqlalchemy.orm import Session
from core.entities.chat_entity import Chat
from core.entities.word_entity import Word
from core.entities.pair_entity import Pair
from core.entities.reply_entity import Reply
from core.services.learn_service import LearnService


def test_learn_words(learn_service: LearnService, dbsession: Session):
    """
    Test the _learn_words method to ensure words are stored in the database correctly.
    """
    learn_service._learn_words()

    # Verify words were learned
    result_words = dbsession.query(Word).all()
    assert len(result_words) == 2
    assert {word.word for word in result_words} == set(learn_service.words)


def test_prepare_new_words(learn_service: LearnService):
    """
    Test the _prepare_new_words method to ensure it processes words correctly with sentence delimiters.
    """
    new_words = learn_service._prepare_new_words()
    expected_words = [None, "word1", "word2", None]

    assert new_words == expected_words


def test_preload_words(learn_service: LearnService, dbsession: Session):
    """
    Test the _preload_words method to ensure it preloads words from the database.
    """
    preloaded_words = learn_service._preload_words()

    assert len(preloaded_words) == 2
    assert "word1" in preloaded_words
    assert "word2" in preloaded_words


def test_map_trigram(learn_service: LearnService, dbsession: Session, word1: Word, word2: Word):
    """
    Test the _map_trigram method to ensure it maps words to their IDs correctly.
    """
    preloaded_words = learn_service._preload_words()
    new_words = ["word1", "word2", None]

    trigram_map, trigram = learn_service._map_trigram(
        new_words, preloaded_words)

    assert trigram_map == {0: word1.id, 1: word2.id}
    assert trigram == ["word1", "word2", None]


def test_manage_reply(learn_service: LearnService, dbsession: Session, pair: Pair, word1: Word):
    """
    Test the _manage_reply method to ensure replies are managed correctly.
    """
    # Ensure the reply does not exist initially
    initial_reply = dbsession.query(Reply).filter_by(
        pair_id=pair.id, word_id=word1.id).one_or_none()
    assert initial_reply is None

    # Call the _manage_reply method
    learn_service._manage_reply(pair.id, word1.id)

    # Fetch the reply again to check if it has been created and the count is set correctly
    created_reply = dbsession.query(Reply).filter_by(
        pair_id=pair.id, word_id=word1.id).one()
    assert created_reply.count == 1

    # Call the _manage_reply method again to increment the count
    learn_service._manage_reply(pair.id, word1.id)

    # Fetch the reply again to check if the count has been incremented
    # Refresh the state of the reply instance from the database
    dbsession.refresh(created_reply)
    assert created_reply.count == 2  # The count should be incremented


# Additional test to cover creation of new reply if not exists
def test_manage_reply_create_new(learn_service: LearnService, dbsession: Session, pair: Pair):
    """
    Test the _manage_reply method to ensure a new reply is created if it does not exist.
    """
    word3 = Word(word="word3")
    dbsession.add(word3)
    dbsession.commit()

    learn_service._manage_reply(pair.id, word3.id)

    reply = dbsession.query(Reply).filter_by(
        pair_id=pair.id, word_id=word3.id).one_or_none()

    assert reply is not None
    assert reply.count == 1


def test_update_pairs_timestamp(learn_service: LearnService, dbsession: Session, pair: Pair):
    """
    Test the _update_pairs_timestamp method to ensure it updates the timestamp of the given pairs.
    """
    initial_timestamp = pair.created_at
    learn_service._update_pairs_timestamp([pair.id])

    updated_pair = dbsession.query(Pair).filter_by(id=pair.id).one()

    assert updated_pair.updated_at != initial_timestamp  # Assuming timestamp is updated


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
    end_sentence = [".", "!", "?"]
    learn_service = LearnService(
        words=words, chat_id=chat.id, session=dbsession,
        end_sentence=end_sentence)
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
