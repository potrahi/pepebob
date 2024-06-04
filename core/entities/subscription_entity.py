from sqlalchemy import String, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from core.entities.base_entity import Base


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    since_id: Mapped[int] = mapped_column(BigInteger)
    
    def __repr__(self) -> str:
        return f"""Subscription(id={self.id!r}, name={self.name!r},
                chat_id={self.chat_id!r}, since_id={self.since_id!r})"""