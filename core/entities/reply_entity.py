from sqlalchemy import BigInteger, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.entities.base_entity import Base


class Reply(Base):
    __tablename__ = 'replies'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    pair_id: Mapped[int] = mapped_column(Integer, ForeignKey('pairs.id', ondelete='CASCADE'), nullable=False)
    word_id: Mapped[int] = mapped_column(Integer, ForeignKey('words.id', ondelete='CASCADE'))
    count: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)
    
    pair = relationship('Pair', back_populates='replies')
    word = relationship('Word')
    
    def __repr__(self) -> str:
        return f"""Reply(id={self.id!r}, pair_id={self.pair_id!r},
                word_id={self.word_id!r}, count={self.count!r})"""