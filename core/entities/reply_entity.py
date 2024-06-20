"""
This module defines the Reply entity class for the database model.
The Reply class represents a reply associated with a pair of words and a chat,
and is mapped to the 'replies' table in the database.
"""

from sqlalchemy import BigInteger, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.entities.base_entity import Base


class Reply(Base):
    """
    Represents a reply entity with attributes like id, pair_id, word_id, etc.
    This class is mapped to the 'replies' table in the database.

    Attributes:
        id (int): Primary key of the reply.
        pair_id (int): Foreign key to the pair.
        word_id (int): Foreign key to the word.
        count (int): Count of replies.
        pair (Pair): Relationship to the Pair entity.
        word (Word): Relationship to the Word entity.
    """

    __tablename__ = 'replies'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False)
    pair_id: Mapped[int] = mapped_column(Integer, ForeignKey(
        'pairs.id', ondelete='CASCADE'), nullable=False)
    word_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('words.id', ondelete='CASCADE'), nullable=True)
    count: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)

    pair = relationship('Pair', back_populates='replies')
    word = relationship('Word')

    def __repr__(self) -> str:
        return (f"Reply(id={self.id!r}, pair_id={self.pair_id!r}, "
                f"word_id={self.word_id!r}, count={self.count!r})")
