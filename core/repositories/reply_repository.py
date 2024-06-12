"""
This module provides the ReplyRepository class for managing Reply entities
in a PostgreSQL database using SQLAlchemy. The repository includes methods
to check, retrieve, create, and update replies associated with pairs.
"""

import logging
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from core.entities.reply_entity import Reply as ReplyEntity

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class ReplyRepository:
    """
    Repository class for managing Reply entities in the database.
    Provides methods to check, retrieve, create, and update replies.
    """

    def has_with_word_id(self, session: Session, word_id: int) -> bool:
        """
        Check if any ReplyEntity exists with the given word_id.

        Args:
            session (Session): SQLAlchemy session.
            word_id (int): Word ID to check.

        Returns:
            bool: True if a reply with the word_id exists, False otherwise.
        """
        logger.debug(
            "Checking if ReplyEntity exists with word_id: %d", word_id)
        result = session.execute(
            select(ReplyEntity.id).where(
                ReplyEntity.word_id == word_id).limit(1)
        ).scalar()
        exists = result is not None
        logger.debug("ReplyEntity existence check result: %s", exists)
        return exists

    def replies_for_pair(self, session: Session, pair_id: int) -> List[ReplyEntity]:
        """
        Get the top 3 replies for a given pair_id, ordered by count in descending order.

        Args:
            session (Session): SQLAlchemy session.
            pair_id (int): Pair ID to filter replies.

        Returns:
            List[ReplyEntity]: List of replies for the given pair_id.
        """
        logger.debug("Getting top 3 replies for pair_id: %d", pair_id)
        result = session.execute(
            select(ReplyEntity)
            .where(ReplyEntity.pair_id == pair_id)
            .order_by(ReplyEntity.count.desc())
            .limit(3)
        ).scalars().all()
        replies = list(result)
        logger.debug("Found replies: %s", replies)
        return replies

    def increment_reply(self, session: Session, reply_id: int, counter: int) -> None:
        """
        Increment the count of a reply by 1.

        Args:
            session (Session): SQLAlchemy session.
            reply_id (int): ID of the reply to increment.
            counter (int): Current count of the reply.
        """
        logger.debug(
            "Incrementing reply count for id: %d, current count: %d", reply_id, counter)
        session.execute(
            update(ReplyEntity)
            .where(ReplyEntity.id == reply_id)
            .values(count=counter + 1)
        )
        session.commit()
        logger.debug("Reply count incremented for id: %d", reply_id)

    def get_reply_by(self, session: Session, pair_id: int,
                     word_id: Optional[int]) -> Optional[ReplyEntity]:
        """
        Get a reply by pair_id and word_id.

        Args:
            session (Session): SQLAlchemy session.
            pair_id (int): Pair ID to filter replies.
            word_id (Optional[int]): Word ID to filter replies.

        Returns:
            Optional[ReplyEntity]: The found reply, or None if not found.
        """
        logger.debug("Getting reply by pair_id: %d, word_id: %s",
                     pair_id, word_id)
        result = session.execute(
            select(ReplyEntity)
            .where((ReplyEntity.word_id == word_id) & (ReplyEntity.pair_id == pair_id))
            .limit(1)
        ).scalar()
        logger.debug("Found reply: %s", result)
        return result

    def create_reply_by(self, session: Session, pair_id: int,
                        word_id: Optional[int]) -> ReplyEntity:
        """
        Create a reply by pair_id and word_id.

        Args:
            session (Session): SQLAlchemy session.
            pair_id (int): Pair ID for the new reply.
            word_id (Optional[int]): Word ID for the new reply.

        Returns:
            ReplyEntity: The created reply.

        Raises:
            ValueError: If the reply could not be created.
        """
        logger.debug("Creating reply for pair_id: %d, word_id: %s",
                     pair_id, word_id)
        session.execute(
            insert(ReplyEntity).values(
                pair_id=pair_id,
                word_id=word_id
            ).on_conflict_do_nothing()
        )
        session.commit()

        reply = self.get_reply_by(session, pair_id, word_id)
        if not reply:
            logger.error(
                "Failed to create reply for pair_id: %d, word_id: %s", pair_id, word_id)
            raise ValueError("No such reply")
        logger.debug("Created reply: %s", reply)
        return reply
