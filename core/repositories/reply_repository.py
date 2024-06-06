from typing import List, Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from core.entities.reply_entity import Reply as ReplyEntity


class ReplyRepository:
    def has_with_word_id(self, session: Session, word_id: int) -> bool:
        result = session.execute(
            select(ReplyEntity.id).where(ReplyEntity.word_id == word_id).limit(1)
        ).scalar()
        exists = result is not None
        return exists

    def replies_for_pair(self, session: Session, pair_id: int) -> List[ReplyEntity]:
        result = session.execute(
            select(ReplyEntity)
            .where(ReplyEntity.pair_id == pair_id)
            .order_by(ReplyEntity.count.desc())
            .limit(3)
        ).scalars().all()
        replies = list(result)
        return replies

    def get_reply_or_create_by(self, session: Session, pair_id: int, word_id: Optional[int]) -> ReplyEntity:
        reply = self.get_reply_by(session, pair_id, word_id)
        if reply:
            return reply
        else:
            return self.create_reply_by(session, pair_id, word_id)

    def increment_reply(self, session: Session, id: int, counter: int) -> None:
        session.execute(
            update(ReplyEntity)
            .where(ReplyEntity.id == id)
            .values(count=counter + 1)
        )
        session.commit()

    def get_reply_by(self, session: Session, pair_id: int, word_id: Optional[int]) -> Optional[ReplyEntity]:
        result = session.execute(
            select(ReplyEntity)
            .where((ReplyEntity.word_id == word_id) & (ReplyEntity.pair_id == pair_id))
            .limit(1)
        ).scalar()
        return result

    def create_reply_by(self, session: Session, pair_id: int, word_id: Optional[int]) -> ReplyEntity:
        session.execute(
            insert(ReplyEntity).values(
                pair_id=pair_id,
                word_id=word_id
            ).on_conflict_do_nothing()
        )
        session.commit()

        reply = self.get_reply_by(session, pair_id, word_id)
        if reply:
            return reply
        else:
            raise ValueError("No such reply")
