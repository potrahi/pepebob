from sqlalchemy import Integer, String, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.entities.base_entity import Base


class Word(Base):
    __tablename__ = 'words'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    word: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    
    __table_args__ = (
        Index('index_words_on_word', 'word'),
        UniqueConstraint('word', name='unique_word_word')
    )
        
    def __repr__(self) -> str:
        return f"Word(id={self.id!r}, word={self.word!r})"