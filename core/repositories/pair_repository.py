import logging
from typing import List, Optional
from datetime import datetime, timedelta

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import Session

from core.entities.pair_entity import Pair as PairEntity
from core.entities.reply_entity import Reply as ReplyEntity

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class PairRepository:
    def has_with_word_id(self, session: Session, word_id: int) -> bool:
        logger.debug(f"Checking if PairEntity exists with word_id: {word_id}")
        result = session.execute(
            select(PairEntity.id).where((PairEntity.first_id == word_id) | (PairEntity.second_id == word_id)).limit(1)
        ).scalar()
        logger.debug(f"PairEntity existence check result: {result}")
        return result is not None

    def get_pair_with_replies(self, session: Session, chat_id: int, first_ids: Optional[int], second_ids: List[Optional[int]]) -> List[PairEntity]:
        logger.debug(f"Getting pairs with replies for chat_id: {chat_id}, first_ids: {first_ids}, second_ids: {second_ids}")
        time_offset = datetime.now() - timedelta(minutes=10)
        result = session.execute(
            select(PairEntity)
            .where(
                (PairEntity.chat_id == chat_id) &
                (PairEntity.first_id == first_ids) &
                (PairEntity.second_id.in_(second_ids)) &
                (PairEntity.created_at < time_offset) &
                session.query(ReplyEntity).filter(ReplyEntity.pair_id == PairEntity.id).exists()
            )
            .limit(3)
        ).scalars().all()
        logger.debug(f"Found pairs: {result}")
        return list(result)

    def get_pair_by(self, session: Session, chat_id: int, first_id: Optional[int], second_id: Optional[int]) -> Optional[PairEntity]:
        logger.debug(f"Getting pair by chat_id: {chat_id}, first_id: {first_id}, second_id: {second_id}")
        result = session.execute(
            select(PairEntity).where(
                (PairEntity.chat_id == chat_id) &
                (PairEntity.first_id == first_id) &
                (PairEntity.second_id == second_id)
            ).limit(1)
        ).scalar()
        logger.debug(f"Found pair: {result}")
        return result

    def create_pair_by(self, session: Session, chat_id: int, first_id: Optional[int], second_id: Optional[int], updated_at: datetime = datetime.now()) -> PairEntity:
        logger.debug(f"Creating pair for chat_id: {chat_id}, first_id: {first_id}, second_id: {second_id}")
        session.execute(
            insert(PairEntity).values(
                chat_id=chat_id,
                first_id=first_id,
                second_id=second_id,
                created_at=datetime.now(),
                updated_at=updated_at
            ).on_conflict_do_nothing()
        )
        session.commit()

        pair = self.get_pair_by(session, chat_id, first_id, second_id)
        if pair:
            logger.debug(f"Created pair: {pair}")
            return pair
        else:
            logger.error(f"Failed to create pair for chat_id: {chat_id}, first_id: {first_id}, second_id: {second_id}")
            raise ValueError("No such pair")

    def touch(self, session: Session, pair_ids: List[int]) -> None:
        logger.debug(f"Touching pairs with ids: {pair_ids}")
        session.execute(
            update(PairEntity).where(PairEntity.id.in_(pair_ids)).values(updated_at=datetime.now())
        )
        session.commit()

    def get_pairs_count(self, session: Session, chat_id: int) -> int:
        logger.debug(f"Getting pairs count for chat_id: {chat_id}")
        result = session.execute(
            select(func.count(func.distinct(PairEntity.id))).where(PairEntity.chat_id == chat_id)
        ).scalar()
        logger.debug(f"Pairs count: {result}")
        return result if result is not None else 0

    def remove_old(self, session: Session, cleanup_limit: int) -> List[int]:
        logger.debug(f"Removing old pairs with cleanup_limit: {cleanup_limit}")
        remove_lt = datetime.now() - timedelta(days=90)
        to_removal_ids = session.execute(
            select(PairEntity.id).where(PairEntity.updated_at < remove_lt).limit(cleanup_limit)
        ).scalars().all()

        session.execute(
            delete(PairEntity).where(PairEntity.id.in_(to_removal_ids))
        )
        session.commit()

        logger.debug(f"Removed pairs with ids: {to_removal_ids}")
        return list(to_removal_ids)

    def get_pair_or_create_by(self, session: Session, chat_id: int, first_id: Optional[int], second_id: Optional[int]) -> PairEntity:
        logger.debug(f"Getting or creating pair for chat_id: {chat_id}, first_id: {first_id}, second_id: {second_id}")
        pair = self.get_pair_by(session, chat_id, first_id, second_id)
        if pair:
            logger.debug(f"Found existing pair: {pair}")
            return pair
        else:
            logger.debug(f"No existing pair found, creating new one.")
            return self.create_pair_by(session, chat_id, first_id, second_id)
