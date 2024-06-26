"""
This module provides the PairRepository class for managing Pair entities
in a PostgreSQL database using SQLAlchemy. The repository includes methods
to check, retrieve, create, update, and delete pairs and their associated replies.
"""

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
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PairRepository:
    """
    Repository class for managing Pair entities in the database.
    Provides methods to retrieve, create, update, and delete pairs.
    """

    def _get_pair_by(self, session: Session, chat_id: int,
                     first_id: Optional[int], second_id: Optional[int]) -> Optional[PairEntity]:
        """
        Get a pair by chat_id, first_id, and second_id.

        Args:
            session (Session): SQLAlchemy session.
            chat_id (int): Chat ID to filter pairs.
            first_id (Optional[int]): First ID to filter pairs.
            second_id (Optional[int]): Second ID to filter pairs.

        Returns:
            Optional[PairEntity]: The found pair, or None if not found.
        """
        logger.debug("Getting pair by chat_id: %d, first_id: %s, second_id: %s",
                     chat_id, first_id, second_id)
        result = session.execute(
            select(PairEntity).where(
                (PairEntity.chat_id == chat_id) &
                (PairEntity.first_id == first_id) &
                (PairEntity.second_id == second_id)
            ).limit(1)
        ).scalar()
        logger.debug("Found pair: %s", result)
        return result

    def _create_pair_by(self, session: Session, chat_id: int,
                        first_id: Optional[int], second_id: Optional[int],
                        updated_at: datetime = datetime.now()) -> PairEntity:
        """
        Create a pair by chat_id, first_id, and second_id.

        Args:
            session (Session): SQLAlchemy session.
            chat_id (int): Chat ID for the new pair.
            first_id (Optional[int]): First ID for the new pair.
            second_id (Optional[int]): Second ID for the new pair.
            updated_at (datetime, optional): Timestamp for when the pair was updated. 
                Defaults to current time.

        Returns:
            PairEntity: The created pair.

        Raises:
            ValueError: If the pair could not be created.
        """
        logger.debug("Creating pair for chat_id: %d, first_id: %s, second_id: %s",
                     chat_id, first_id, second_id)
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

        pair = self._get_pair_by(session, chat_id, first_id, second_id)
        if not pair:
            logger.error(
                "Failed to create pair for chat_id: %d, first_id: %s, second_id: %s",
                chat_id, first_id, second_id
            )
            raise ValueError("No such pair")

        logger.debug("Created pair: %s", pair)
        return pair

    def has_with_word_id(self, session: Session, word_id: int) -> bool:
        """
        Check if any PairEntity exists with the given word_id.

        Args:
            session (Session): SQLAlchemy session.
            word_id (int): Word ID to check.

        Returns:
            bool: True if a pair with the word_id exists, False otherwise.
        """
        logger.debug("Checking if PairEntity exists with word_id: %d", word_id)
        result = session.execute(
            select(PairEntity.id).where(
                (PairEntity.first_id == word_id) | (
                    PairEntity.second_id == word_id)
            ).limit(1)
        ).scalar()
        logger.debug("PairEntity existence check result: %s", result)
        return result is not None

    def get_pair_with_replies(self, session: Session, chat_id: int, first_ids: Optional[int],
                              second_ids: List[Optional[int]]) -> List[PairEntity]:
        """
        Get pairs with replies for the given chat_id, first_ids, and second_ids.

        Args:
            session (Session): SQLAlchemy session.
            chat_id (int): Chat ID to filter pairs.
            first_ids (Optional[int]): First ID to filter pairs.
            second_ids (List[Optional[int]]): List of second IDs to filter pairs.

        Returns:
            List[PairEntity]: List of pairs with replies.
        """
        logger.debug("Getting pairs with replies for chat_id: %d, first_ids: %s, second_ids: %s",
                     chat_id, first_ids, second_ids)
        time_offset = datetime.now() - timedelta(minutes=10)
        result = session.execute(
            select(PairEntity)
            .where(
                (PairEntity.chat_id == chat_id) &
                (PairEntity.first_id == first_ids) &
                (PairEntity.second_id.in_(second_ids)) &
                (PairEntity.created_at < time_offset) &
                session.query(ReplyEntity).filter(
                    ReplyEntity.pair_id == PairEntity.id).exists()
            )
            .limit(3)
        ).scalars().all()
        logger.debug("Found pairs: %s", result)
        return list(result)

    def touch(self, session: Session, pair_ids: List[int]) -> None:
        """
        Update the updated_at timestamp for the given pairs.

        Args:
            session (Session): SQLAlchemy session.
            pair_ids (List[int]): List of pair IDs to update.
        """
        logger.debug("Touching pairs with ids: %s", pair_ids)
        session.execute(
            update(PairEntity).where(PairEntity.id.in_(
                pair_ids)).values(updated_at=datetime.now())
        )
        session.commit()

    def get_pairs_count(self, session: Session, chat_id: int) -> int:
        """
        Get the count of pairs for a given chat_id.

        Args:
            session (Session): SQLAlchemy session.
            chat_id (int): Chat ID to filter pairs.

        Returns:
            int: The count of pairs.
        """
        logger.debug("Getting pairs count for chat_id: %d", chat_id)
        result = session.execute(
            select(func.count(func.distinct(PairEntity.id))).where(  # pylint: disable=not-callable
                PairEntity.chat_id == chat_id)
        ).scalar()
        logger.debug("Pairs count: %d", result)
        return result if result is not None else 0

    def remove_old(self, session: Session, cleanup_limit: int) -> List[int]:
        """
        Remove old pairs that have not been updated for more than 90 days.

        Args:
            session (Session): SQLAlchemy session.
            cleanup_limit (int): The maximum number of pairs to remove.

        Returns:
            List[int]: List of removed pair IDs.
        """
        logger.debug(
            "Removing old pairs with cleanup_limit: %d", cleanup_limit)
        remove_lt = datetime.now() - timedelta(days=90)
        to_removal_ids = session.execute(
            select(PairEntity.id).where(
                PairEntity.updated_at < remove_lt).limit(cleanup_limit)
        ).scalars().all()

        session.execute(
            delete(PairEntity).where(PairEntity.id.in_(to_removal_ids))
        )
        session.commit()

        logger.debug("Removed pairs with ids: %s", to_removal_ids)
        return list(to_removal_ids)

    def get_pair_or_create_by(self, session: Session, chat_id: int,
                              first_id: Optional[int], second_id: Optional[int]) -> PairEntity:
        """
        Get a pair by chat_id, first_id, and second_id, or create it if it does not exist.

        Args:
            session (Session): SQLAlchemy session.
            chat_id (int): Chat ID for the pair.
            first_id (Optional[int]): First ID for the pair.
            second_id (Optional[int]): Second ID for the pair.

        Returns:
            PairEntity: The found or created pair.
        """
        logger.debug("Getting or creating pair for chat_id: %d, first_id: %s, second_id: %s",
                     chat_id, first_id, second_id)
        pair = self._get_pair_by(session, chat_id, first_id, second_id)
        if not pair:
            logger.debug("No existing pair found, creating new one.")
            return self._create_pair_by(session, chat_id, first_id, second_id)

        logger.debug("Found existing pair: %s", pair)
        return pair
