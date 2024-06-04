import logging
from typing import List, Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from core.entities.reply_entity import Reply as ReplyEntity

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ReplyRepository:
    def has_with_word_id(self, session: Session, word_id: int) -> bool:
        logger.debug(f"Checking existence of reply with word_id={word_id}")
        result = session.execute(
            select(ReplyEntity.id).where(ReplyEntity.word_id == word_id).limit(1)
        ).scalar()
        exists = result is not None
        logger.debug(f"Reply with word_id={word_id} exists: {exists}")
        return exists

    def replies_for_pair(self, session: Session, pair_id: int) -> List[ReplyEntity]:
        logger.debug(f"Fetching replies for pair_id={pair_id}")
        result = session.execute(
            select(ReplyEntity)
            .where(ReplyEntity.pair_id == pair_id)
            .order_by(ReplyEntity.count.desc())
            .limit(3)
        ).scalars().all()
        replies = list(result)
        logger.debug(f"Replies for pair_id={pair_id}: {replies}")
        return replies

    def get_reply_or_create_by(self, session: Session, pair_id: int, word_id: Optional[int]) -> ReplyEntity:
        logger.debug(f"Getting or creating reply for pair_id={pair_id}, word_id={word_id}")
        reply = self.get_reply_by(session, pair_id, word_id)
        if reply:
            logger.debug(f"Found existing reply for pair_id={pair_id}, word_id={word_id}")
            return reply
        else:
            logger.debug(f"No existing reply found, creating new reply for pair_id={pair_id}, word_id={word_id}")
            return self.create_reply_by(session, pair_id, word_id)

    def increment_reply(self, session: Session, id: int, counter: int) -> None:
        logger.debug(f"Incrementing reply count for id={id}, current counter={counter}")
        session.execute(
            update(ReplyEntity)
            .where(ReplyEntity.id == id)
            .values(count=counter + 1)
        )
        session.commit()
        logger.debug(f"Reply count incremented for id={id}")

    def get_reply_by(self, session: Session, pair_id: int, word_id: Optional[int]) -> Optional[ReplyEntity]:
        logger.debug(f"Fetching reply for pair_id={pair_id}, word_id={word_id}")
        result = session.execute(
            select(ReplyEntity)
            .where((ReplyEntity.word_id == word_id) & (ReplyEntity.pair_id == pair_id))
            .limit(1)
        ).scalar()
        logger.debug(f"Fetched reply: {result}")
        return result

    def create_reply_by(self, session: Session, pair_id: int, word_id: Optional[int]) -> ReplyEntity:
        logger.debug(f"Creating reply for pair_id={pair_id}, word_id={word_id}")
        session.execute(
            insert(ReplyEntity).values(
                pair_id=pair_id,
                word_id=word_id
            ).on_conflict_do_nothing()
        )
        session.commit()
        logger.debug(f"Reply created for pair_id={pair_id}, word_id={word_id}")

        reply = self.get_reply_by(session, pair_id, word_id)
        if reply:
            logger.debug(f"Successfully created reply: {reply}")
            return reply
        else:
            logger.error(f"Failed to create reply for pair_id={pair_id}, word_id={word_id}")
            raise ValueError("No such reply")
