import datetime
from sqlalchemy import BigInteger, Integer, SmallInteger, TIMESTAMP, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.entities.base_entity import Base


class Chat(Base):
    __tablename__ = 'chats'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chat_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    random_chance: Mapped[int] = mapped_column(SmallInteger, default=5, nullable=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    updated_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    name: Mapped[str] = mapped_column(String)
    repost_chat_username: Mapped[str] = mapped_column(String)
    
    pairs = relationship('Pair', order_by='Pair.id', back_populates='chat')
 
    def __repr__(self) -> str:
        return f"""Chat(id={self.id!r}, name={self.name!r}, telegram_id={self.telegram_id!r}, 
                repost_chat_username={self.repost_chat_username!r}), 
                chat_type={self.chat_type!r}, random_chance={self.random_chance!r}, 
                created_at={self.created_at!r}, updated_at={self.updated_at!r})"""