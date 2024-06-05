import datetime

from sqlalchemy import Integer, ForeignKey, TIMESTAMP, func, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.entities.base_entity import Base


class Pair(Base):
    __tablename__ = 'pairs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey('chats.id', ondelete='CASCADE'), nullable=False)
    first_id: Mapped[int] = mapped_column(Integer, ForeignKey('words.id', ondelete='CASCADE'))
    second_id: Mapped[int] = mapped_column(Integer, ForeignKey('words.id', ondelete='CASCADE'))
    created_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    updated_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    chat = relationship('Chat', back_populates='pairs')
    first_word = relationship('Word', foreign_keys=[first_id])
    second_word = relationship('Word', foreign_keys=[second_id])
    replies = relationship('Reply', order_by='Reply.id', back_populates='pair')
   
    def __repr__(self) -> str:
        return f"""Pair(id={self.id!r}, chat_id={self.chat_id!r}, first_id={self.first_id!r},
                second_id={self.second_id!r}, created_at={self.created_at!r}, 
                updated_at={self.updated_at!r}, replies={self.replies!r})"""