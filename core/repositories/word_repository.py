import logging
from typing import List, Optional

from sqlalchemy import select, insert, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from core.entities.word_entity import Word as WordEntity

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class WordRepository:
    def get_first_id(self, session: Session) -> Optional[int]:
        logger.debug("Getting first WordEntity ID")
        result = session.execute(select(WordEntity.id).order_by(WordEntity.id.asc()).limit(1)).scalar()
        logger.debug(f"First WordEntity ID: {result}")
        return result

    def get_next_id(self, session: Session, id: int) -> Optional[int]:
        logger.debug(f"Getting next WordEntity ID after ID: {id}")
        result = session.execute(select(WordEntity.id).where(WordEntity.id > id).order_by(WordEntity.id.asc()).limit(1)).scalar()
        logger.debug(f"Next WordEntity ID: {result}")
        return result

    def delete_by_id(self, session: Session, id: int) -> None:
        logger.debug(f"Deleting WordEntity with ID: {id}")
        session.execute(delete(WordEntity).where(WordEntity.id == id))
        session.commit()
        logger.debug(f"Deleted WordEntity with ID: {id}")

    def get_by_words(self, session: Session, words: List[str]) -> List[WordEntity]:
        logger.debug(f"Getting WordEntities by words: {words}")
        result = session.execute(select(WordEntity).where(WordEntity.word.in_(words))).scalars().all()
        logger.debug(f"Found WordEntities: {result}")
        return list(result)

    def get_word_by_id(self, session: Session, id: int) -> Optional[WordEntity]:
        logger.debug(f"Getting WordEntity by ID: {id}")
        result = session.execute(select(WordEntity).where(WordEntity.id == id).limit(1)).scalar()
        logger.debug(f"Found WordEntity: {result}")
        return result

    def get_by_word(self, session: Session, word: str) -> Optional[WordEntity]:
        logger.debug(f"Getting WordEntity by word: {word}")
        result = session.execute(select(WordEntity).where(WordEntity.word == word).limit(1)).scalar()
        logger.debug(f"Found WordEntity: {result}")
        return result

    def create(self, session: Session, word: str) -> Optional[int]:
        logger.debug(f"Creating WordEntity with word: {word}")
        stmt = insert(WordEntity).values(word=word).returning(WordEntity.id)
        try:
            result = session.execute(stmt).scalar()
            session.commit()
            logger.debug(f"Created WordEntity with ID: {result}")
            return result
        except IntegrityError as e:
            logger.error(f"IntegrityError: {e}")
            session.rollback()
            return None

    def learn_words(self, session: Session, words: List[str]) -> None:
        logger.debug(f"Learning words: {words}")
        existed_words = [word.word for word in self.get_by_words(session, words)]
        for word in words:
            if word in existed_words:
                logger.debug(f"Word already exists: {word}")
                continue
            logger.debug(f"Creating new word: {word}")
            self.create(session, word)
        logger.debug("Completed learning words")
