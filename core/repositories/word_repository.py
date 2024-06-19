"""
This module provides the WordRepository class for managing Word entities
in a PostgreSQL database using SQLAlchemy. The repository includes methods
to retrieve, create, and learn new words.
"""

import logging
from typing import List, Optional

from sqlalchemy import select, insert
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from core.entities.word_entity import Word

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class WordRepository:
    """
    Repository class for managing Word entities in the database.
    Provides methods to retrieve, create, and learn new words.
    """

    def _create(self, session: Session, word: str) -> Optional[int]:
        """
        Create a new Word with the given word.

        Args:
            session (Session): SQLAlchemy session.
            word (str): The word to create.

        Returns:
            Optional[int]: The ID of the created Word, or None if creation failed.
        """
        logger.debug("Creating Word with word: %s", word)
        stmt = insert(Word).values(word=word)

        assert session.bind

        if session.bind.dialect.name == 'sqlite':
            try:
                session.execute(stmt)
                session.commit()
                result = session.execute(
                    select(Word.id).where(Word.word == word)
                ).scalar()
                logger.debug("Created Word with ID: %d", result)
                return result
            except IntegrityError as e:
                logger.error("IntegrityError: %s", e)
                session.rollback()
                return None
        else:
            stmt = stmt.returning(Word.id)
            try:
                result = session.execute(stmt).scalar()
                session.commit()
                logger.debug("Created Word with ID: %d", result)
                return result
            except IntegrityError as e:
                logger.error("IntegrityError: %s", e)
                session.rollback()
                return None

    def get_by_words(self, session: Session, words: List[str]) -> List[Word]:
        """
        Retrieve WordEntities by a list of words.

        Args:
            session (Session): SQLAlchemy session.
            words (List[str]): List of words to retrieve.

        Returns:
            List[Word]: List of found WordEntities.
        """
        logger.debug("Getting WordEntities by words: %s", words)
        result = session.execute(
            select(Word).where(Word.word.in_(words))
        ).scalars().all()
        logger.debug("Found WordEntities: %s", result)
        return list(result)

    def get_word_by_id(self, session: Session, word_id: int) -> Optional[Word]:
        """
        Retrieve a Word by its ID.

        Args:
            session (Session): SQLAlchemy session.
            word_id (int): ID of the word to retrieve.

        Returns:
            Optional[Word]: The found Word, or None if not found.
        """
        logger.debug("Getting Word by ID: %d", word_id)
        result = session.execute(
            select(Word).where(Word.id == word_id).limit(1)
        ).scalar()
        logger.debug("Found Word: %s", result)
        return result

    def learn_words(self, session: Session, words: List[str]) -> None:
        """
        Learn a list of new words by creating WordEntities for them if they do not already exist.

        Args:
            session (Session): SQLAlchemy session.
            words (List[str]): List of words to learn.
        """
        logger.debug("Learning words: %s", words)
        existing_words = {
            word.word for word in self.get_by_words(session, words)}
        for word in words:
            if word in existing_words:
                logger.debug("Word already exists: %s", word)
                continue
            logger.debug("Creating new word: %s", word)
            self._create(session, word)
        logger.debug("Completed learning words")
