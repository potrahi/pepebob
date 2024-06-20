"""
This module contains unit tests for the WordRepository class.
"""

from sqlalchemy.orm import Session
from core.entities.word_entity import Word
from core.repositories.word_repository import WordRepository


def test_get_by_words(word_repo: WordRepository, word1: Word, word2: Word, dbsession: Session):
    """
    Test the get_by_words method to retrieve WordEntities by a list of words.
    """
    words = [word1.word, word2.word]
    result = word_repo.get_by_words(dbsession, words)
    assert len(result) == 2
    assert set(word.word for word in result) == set(words)


def test_get_word_by_id(word_repo: WordRepository, word1: Word, dbsession: Session):
    """
    Test the get_word_by_id method to retrieve a WordEntity by its ID.
    """
    result = word_repo.get_word_by_id(dbsession, word1.id)
    assert result is not None
    assert result.id == word1.id
    assert result.word == word1.word


def test_get_word_by_nonexistent_id(word_repo: WordRepository, dbsession: Session):
    """
    Test the get_word_by_id method to handle a nonexistent ID.
    """
    result = word_repo.get_word_by_id(dbsession, 9999)
    assert result is None


def test_learn_words(word_repo: WordRepository, word1: Word, dbsession: Session):
    """
    Test the learn_words method to learn new words and handle existing ones.
    """
    words = [word1.word, "newword1", "newword2"]
    word_repo.learn_words(dbsession, words)

    result = word_repo.get_by_words(dbsession, words)
    assert len(result) == 3
    assert set(word.word for word in result) == set(words)


def test_learn_existing_words(word_repo: WordRepository, word1: Word, dbsession: Session):
    """
    Test the learn_words method with words that already exist.
    """
    words = [word1.word]
    word_repo.learn_words(dbsession, words)
    result = word_repo.get_by_words(dbsession, words)
    assert len(result) == 1
    assert result[0].word == word1.word
