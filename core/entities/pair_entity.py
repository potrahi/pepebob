"""
This module defines the Pair entity class for the database model.
The Pair class represents a pair of words associated with a chat,
and is mapped to the 'pairs' table in the database.
"""
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.entities.base_entity import Base


class Pair(Base):
    """
    Represents a pair entity with attributes like id, chat_id, first_id, etc.
    This class is mapped to the 'pairs' table in the database.

    Attributes:
        id (int): Primary key of the pair.
        chat_id (int): Foreign key to the chat.
        first_id (int): Foreign key to the first word.
        second_id (int): Foreign key to the second word.
        created_at (str): Timestamp when the pair was created.
        updated_at (str): Timestamp when the pair was last updated.
        chat (Chat): Relationship to the Chat entity.
        first_word (Word): Relationship to the first Word entity.
        second_word (Word): Relationship to the second Word entity.
        replies (List[Reply]): Relationship to the Reply entity.
    """

    __tablename__ = 'pairs'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('chats.id', ondelete='CASCADE'), nullable=False)
    first_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('words.id', ondelete='CASCADE'))
    second_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('words.id', ondelete='CASCADE'))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now())  # pylint: disable=not-callable
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())  # pylint: disable=not-callable

    chat = relationship('Chat', back_populates='pairs')
    first_word = relationship('Word', foreign_keys=[first_id])
    second_word = relationship('Word', foreign_keys=[second_id])
    replies = relationship('Reply', order_by='Reply.id', back_populates='pair')

    def __repr__(self) -> str:
        return (f"Pair(id={self.id!r}, chat_id={self.chat_id!r}, first_id={self.first_id!r}, "
                f"second_id={self.second_id!r}, created_at={self.created_at!r}, "
                f"updated_at={self.updated_at!r}, replies={self.replies!r})")
