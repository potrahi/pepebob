"""
This module provides the ChatRepository class for managing chat entities
in a PostgreSQL database using SQLAlchemy.
"""

import logging
from typing import Optional
from datetime import datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from core.entities.chat_entity import Chat
from core.enums.chat_types import ChatType

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class ChatRepository:
    """
    Repository class for managing Chat entities.
    Provides methods to retrieve, create, and update Chat records.
    """

    def get_or_create_by(self, session: Session, telegram_id: int,
                         name: str, chat_type: str) -> Chat:
        """
        Retrieve a Chat entity by its Telegram ID, or create it if it does not exist.

        Args:
            session (Session): SQLAlchemy session.
            telegram_id (int): Telegram ID of the chat.
            name (str): Name of the chat.
            chat_type (str): Type of the chat.

        Returns:
            Chat: The existing or newly created Chat entity.
        """
        logger.debug(
            "Fetching or creating chat with telegram_id=%d, name=%s, chat_type=%s",
            telegram_id, name, chat_type
        )
        chat = self._get_by_telegram_id(session, telegram_id)
        if chat:
            logger.debug("Chat found with telegram_id=%d", telegram_id)
            return chat
        logger.debug(
            "Chat not found, creating new chat with telegram_id=%d", telegram_id)
        return self._create(session, telegram_id, name, chat_type)

    def update_random_chance(self, session: Session, chat_id: int, random_chance: int) -> None:
        """
        Update the random chance value of a Chat entity.

        Args:
            session (Session): SQLAlchemy session.
            chat_id (int): ID of the chat to update.
            random_chance (int): New random chance value.

        Returns:
            None
        """
        logger.debug(
            "Updating random_chance for chat id=%d to random_chance=%d",
            chat_id, random_chance
        )
        session.execute(
            update(Chat)
            .where(Chat.id == chat_id)
            .values(random_chance=random_chance, updated_at=datetime.now())
        )
        session.commit()

    def update_chat(self, session: Session, chat_id: int,
                    name: Optional[str], telegram_id: int) -> None:
        """
        Update the name and Telegram ID of a Chat entity.

        Args:
            session (Session): SQLAlchemy session.
            chat_id (int): ID of the chat to update.
            name (Optional[str]): New name of the chat.
            telegram_id (int): New Telegram ID of the chat.

        Returns:
            None
        """
        logger.debug(
            "Updating chat id=%d with name=%s and telegram_id=%d",
            chat_id, name, telegram_id
        )
        session.execute(
            update(Chat)
            .where(Chat.id == chat_id)
            .values(name=name, telegram_id=telegram_id, updated_at=datetime.now())
        )
        session.commit()

    def _create(
            self, session: Session, telegram_id: int, name: str,
            chat_type: str) -> Chat:
        """
        Create a new Chat entity.

        Args:
            session (Session): SQLAlchemy session.
            telegram_id (int): Telegram ID of the new chat.
            name (str): Name of the new chat.
            chat_type (str): Type of the new chat.

        Returns:
            Chat: The newly created Chat entity.

        Raises:
            ValueError: If the chat could not be created.
        """
        logger.debug(
            "Creating chat with telegram_id=%d, name=%s, chat_type=%s",
            telegram_id, name, chat_type
        )

        existing_chat = self._get_by_telegram_id(session, telegram_id)
        if existing_chat:
            raise ValueError(
                f"Chat with telegram_id {telegram_id} already exists")

        session.execute(
            insert(Chat)
            .values(
                telegram_id=telegram_id,
                name=name,
                chat_type=ChatType.from_str(chat_type.lower()),
                updated_at=datetime.now(),
                created_at=datetime.now()
            )
            .on_conflict_do_nothing()
        )
        session.commit()

        chat = self._get_by_telegram_id(session, telegram_id)
        if chat:
            logger.debug(
                "Chat created successfully with telegram_id=%d", telegram_id)
            return chat
        logger.error("Failed to create chat with telegram_id=%d", telegram_id)
        raise ValueError("No such chat")

    def _get_by_telegram_id(self, session: Session, telegram_id: int) -> Optional[Chat]:
        """
        Retrieve a Chat entity by its Telegram ID.

        Args:
            session (Session): SQLAlchemy session.
            telegram_id (int): Telegram ID of the chat to retrieve.

        Returns:
            Optional[Chat]: The Chat entity, or None if not found.
        """
        logger.debug("Fetching chat with telegram_id=%d", telegram_id)
        result = session.execute(
            select(Chat).where(Chat.telegram_id == telegram_id).limit(1)).scalar()
        return result
