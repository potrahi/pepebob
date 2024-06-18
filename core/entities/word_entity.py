"""
This module defines the Word entity class for the database model.
The Word class represents a word with a unique identifier,
and is mapped to the 'words' table in the database.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.entities.base_entity import Base


class Word(Base):
    """
    Represents a word entity with attributes like id and word.
    This class is mapped to the 'words' table in the database.

    Attributes:
        id (int): Primary key of the word.
        word (str): The word string, which is unique and cannot be null.
    """

    __tablename__ = 'words'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False)
    word: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"Word(id={self.id!r}, word={self.word!r})"
