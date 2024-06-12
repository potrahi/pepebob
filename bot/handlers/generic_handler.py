"""
This module defines the GenericHandler abstract base class,
which serves as a base for handling Telegram bot updates.
"""

import string
import random
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from telegram import Update

from core.entities.chat_entity import Chat as ChatEntity
from core.repositories.chat_repository import ChatRepository
from core.repositories.context_repository import ContextRepository
from config import Config


class GenericHandler(ABC):
    """
    Abstract base class for handling Telegram bot updates.
    """

    def __init__(self, update: Update, session: Session, config: Config):
        """
        Initializes the GenericHandler with the given update, session, and config.

        Attributes:
            update (Update): The Telegram update object.
            session (Session): The SQLAlchemy session object.
            config (Config): The configuration object.
        """
        self.message = update.message
        self.session = session
        self.config = config
        self.context_repository = ContextRepository(
            host=self.config.cache.host,
            port=self.config.cache.port,
            database_name=self.config.cache.name
        )

    @abstractmethod
    async def call(self, *args, **kwargs) -> Optional[str]:
        """
        Abstract method to handle the Telegram update.

        This method should be implemented by subclasses to define the specific behavior
        for handling a Telegram update. The method can accept a variable number of
        arguments and keyword arguments to provide flexibility in handling different
        types of updates.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Optional[str]: A string result of the update handling, or None if no response
                           is needed. The returned string can be used to send a message
                           back to the user or perform other actions based on the update.
        """


    def before(self):
        """
        Executes actions before handling the update.
        """
        if self.is_chat_changed:
            ChatRepository().update_chat(self.session, self.chat.id,
                                         self.chat_name, self.migration_id)

    @property
    def is_chat_changed(self) -> bool:
        """
        Checks if the chat has changed.

        Returns:
            bool: True if the chat has changed, False otherwise.
        """
        return self.chat_name != self.chat.name or self.migration_id != self.telegram_id

    @property
    def is_private(self) -> bool:
        """
        Checks if the chat is private.

        Returns:
            bool: True if the chat is private, False otherwise.
        """
        return self.chat_type == "chat"

    @property
    def is_random_answer(self) -> bool:
        """
        Checks if a random answer should be provided based on the chat's random chance.

        Returns:
            bool: True if a random answer should be provided, False otherwise.
        """
        return random.randint(0, 99) < self.chat.random_chance

    @property
    def is_reply_to_bot(self) -> bool:
        """
        Checks if the message is a reply to the bot.

        Returns:
            bool: True if the message is a reply to the bot, False otherwise.
        """
        if self.message and self.message.reply_to_message:
            reply_user = self.message.reply_to_message.from_user
            return bool(reply_user and reply_user.username == self.config.bot.name)
        return False

    @property
    def has_anchors(self) -> bool:
        """
        Checks if the message contains any anchor words or the bot's name.

        Returns:
            bool: True if the message contains anchor words or the bot's name, False otherwise.
        """
        if not self.text:
            return False
        anchors = self.config.bot.anchors
        name = self.config.bot.name
        text_no_punctuation = self.text.translate(
            str.maketrans('', '', string.punctuation))
        word_in_anchors = any(
            word in anchors for word in text_no_punctuation.split())
        anchor_in_text = name in self.text
        return word_in_anchors or anchor_in_text

    @property
    def has_entities(self) -> bool:
        """
        Checks if the message has any entities.

        Returns:
            bool: True if the message has entities, False otherwise.
        """
        return bool(self.message and self.message.entities)

    @property
    def is_edition(self) -> bool:
        """
        Checks if the message has been edited.

        Returns:
            bool: True if the message has been edited, False otherwise.
        """
        return bool(self.message and self.message.edit_date)

    @property
    def has_text(self) -> bool:
        """
        Checks if the message contains text.

        Returns:
            bool: True if the message contains text, False otherwise.
        """
        return bool(self.text)

    @property
    def is_mentioned(self) -> bool:
        """
        Checks if the bot is mentioned in the message.

        Returns:
            bool: True if the bot is mentioned in the message, False otherwise.
        """
        return bool(self.text) and f"@{self.config.bot.name.lower()}" in self.text

    @property
    def is_command(self) -> bool:
        """
        Checks if the message is a command.

        Returns:
            bool: True if the message is a command, False otherwise.
        """
        return bool(self.text) and self.text.startswith("/")

    def get_words(self, sentence: str = "") -> List[str]:
        """
        Extracts and returns a list of words from the given sentence or the message text.

        Args:
            sentence (str, optional): The sentence to extract words from. Defaults to "".

        Returns:
            List[str]: A list of words extracted from the sentence or message text.
        """
        text = sentence or self.text
        if not text:
            return []
        if self.message and self.message.entities:
            for entity in self.message.entities:
                start, end = entity.offset, entity.offset + entity.length
                text = text[:start] + " " * (end - start) + text[end:]
        return [word.lower() for word in text.split() if word and len(word) <= 2000]

    @property
    def chat(self) -> ChatEntity:
        """
        Gets or creates the chat entity for the current chat.

        Returns:
            ChatEntity: The chat entity for the current chat.
        """
        return ChatRepository().get_or_create_by(
            self.session, self.telegram_id, self.chat_name, self.chat_type)

    @property
    def telegram_id(self) -> int:
        """
        Gets the Telegram ID of the current chat.

        Returns:
            int: The Telegram ID of the current chat.
        """
        return self.message.chat.id if self.message else 0

    @property
    def migration_id(self) -> int:
        """
        Gets the migration ID of the current chat.

        Returns:
            int: The migration ID of the current chat.
        """
        return (
            self.message.migrate_to_chat_id
            if self.message and self.message.migrate_to_chat_id
            else self.telegram_id
        )

    @property
    def chat_type(self) -> str:
        """
        Gets the type of the current chat.

        Returns:
            str: The type of the current chat.
        """
        chat_type_mapping = {
            "private": "chat",
            "supergroup": "supergroup",
            "group": "faction",
            "channel": "channel"
        }
        return chat_type_mapping.get(self.message.chat.type, "chat") if self.message else "chat"

    @property
    def chat_name(self) -> str:
        """
        Gets the name of the current chat.

        Returns:
            str: The name of the current chat.
        """
        return (
            self.message.chat.title
            if self.message and self.message.chat.title
            else self.from_username
        )

    @property
    def from_username(self) -> str:
        """
        Gets the username of the user who sent the message.

        Returns:
            str: The username of the user who sent the message.
        """
        return (
            self.message.from_user.username
            if self.message and self.message.from_user and self.message.from_user.username
            else "Unknown"
        )

    def get_context(self, limit: int) -> List[str]:
        """
        Gets a random sample of context strings for the current chat.

        Args:
            limit (int): The maximum number of context strings to retrieve.

        Returns:
            List[str]: A random sample of context strings for the current chat.
        """
        context = self.context_repository.get_context(self.chat_context, limit)
        return random.sample(context, min(len(context), limit))

    @property
    def context(self) -> List[str]:
        """
        Gets a sample of 10 context strings for the current chat.

        Returns:
            List[str]: A sample of 10 context strings for the current chat.
        """
        return self.get_context(10)

    @property
    def full_context(self) -> List[str]:
        """
        Gets a sample of 50 context strings for the current chat.

        Returns:
            List[str]: A sample of 50 context strings for the current chat.
        """
        return self.get_context(50)

    @property
    def words(self) -> List[str]:
        """
        Gets the list of words in the message text.

        Returns:
            List[str]: A list of words in the message text.
        """
        return self.get_words()

    @property
    def text(self) -> Optional[str]:
        """
        Gets the text of the message.

        Returns:
            Optional[str]: The text of the message, or None if there is no message.
        """
        return self.message.text if self.message else None

    @property
    def chat_context(self) -> str:
        """
        Gets the context string for the current chat.

        Returns:
            str: The context string for the current chat.
        """
        return f"chat_context/{self.chat.id}" if self.chat else ""
