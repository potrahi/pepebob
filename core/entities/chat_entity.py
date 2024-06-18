"""
This module defines the Chat entity class for the database model.
The Chat class represents a chat with various attributes and relationships,
and is mapped to the 'chats' table in the database.
"""
from datetime import datetime
from sqlalchemy import BigInteger, Integer, SmallInteger, TIMESTAMP, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.entities.base_entity import Base

class Chat(Base):
    """
    Represents a chat entity with attributes like id, telegram_id, chat_type, etc.
    This class is mapped to the 'chats' table in the database.

    Attributes:
        id (int): Primary key of the chat.
        telegram_id (int): Telegram ID of the chat.
        chat_type (int): Type of the chat.
        random_chance (int): Random chance associated with the chat.
        created_at (str): Timestamp when the chat was created.
        updated_at (str): Timestamp when the chat was last updated.
        name (str): Name of the chat.
        repost_chat_username (str): Username of the repost chat.
        pairs (List[Pair]): Relationship to the Pair entity.
    """

    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chat_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    random_chance: Mapped[int] = mapped_column(
        SmallInteger, default=5, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    name: Mapped[str] = mapped_column(String)
    repost_chat_username: Mapped[str] = mapped_column(String)

    pairs = relationship('Pair', order_by='Pair.id', back_populates='chat')

    def __repr__(self) -> str:
        return (f"Chat(id={self.id!r}, name={self.name!r}, telegram_id={self.telegram_id!r}, "
                f"repost_chat_username={self.repost_chat_username!r}, "
                f"chat_type={self.chat_type!r}, random_chance={self.random_chance!r}, "
                f"created_at={self.created_at.strftime('%Y-%m-%d %H:%M:%S')!r}, "
                f"updated_at={self.updated_at.strftime('%Y-%m-%d %H:%M:%S')!r})")
