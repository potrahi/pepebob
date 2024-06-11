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
    def __init__(self, update: Update, session: Session, config: Config):
        self.message = update.message if update.message else None
        self.session = session
        self.config = config
        self.context_repository = ContextRepository(
            host=self.config.cache.host,
            port=self.config.cache.port,
            database_name=self.config.cache.name
        )
    
    @abstractmethod
    def call(self) -> Optional[str]:
        pass

    def before(self):
        if self.is_chat_changed:
            ChatRepository().update_chat(self.session, self.chat.id, self.chat_name, self.migration_id)

    @property
    def is_chat_changed(self) -> bool:
        return self.chat_name != self.chat.name or self.migration_id != self.telegram_id

    @property
    def is_private(self) -> bool:
        return self.chat_type == "chat"

    @property
    def is_random_answer(self) -> bool:
        return random.randint(0, 99) < self.chat.random_chance

    @property
    def is_reply_to_bot(self) -> bool:
        if self.message and self.message.reply_to_message:
            reply_user = self.message.reply_to_message.from_user
            if reply_user:
                return reply_user.username == self.config.bot.name
        return False

    @property
    def has_anchors(self) -> bool:
        anchors = self.config.bot.anchors
        name = self.config.bot.name
        word_in_anchors = any(
            word.translate(str.maketrans('', '', string.punctuation)) in anchors for word in self.words)
        anchor_in_text = self.text is not None and name in self.text
        return self.has_text and (word_in_anchors or anchor_in_text)

    @property
    def has_entities(self) -> bool:
        return bool(self.message and self.message.entities)

    @property
    def is_edition(self) -> bool:
        return bool(self.message and self.message.edit_date)

    @property
    def has_text(self) -> bool:
        return bool(self.text)

    @property
    def is_mentioned(self) -> bool:
        return self.text is not None and f"@{self.config.bot.name.lower()}" in self.text

    @property
    def is_command(self) -> bool:
        return self.text is not None and self.text.startswith("/")

    def get_words(self) -> List[str]:
        if not self.text:
            return []

        text_copy = self.text
        if self.message and self.message.entities:
            for entity in self.message.entities:
                start = entity.offset
                end = entity.offset + entity.length
                text_copy = text_copy[:start] + " " * (end - start) + text_copy[end:]

        return [
            word.lower()
            for word in text_copy.split()
            if word and len(word) <= 2000
        ]

    @property
    def chat(self) -> ChatEntity:
        return ChatRepository().get_or_create_by(self.session, self.telegram_id, self.chat_name, self.chat_type)

    @property
    def telegram_id(self) -> int:
        return self.message.chat.id if self.message else 0

    @property
    def migration_id(self) -> int:
        return self.message.migrate_to_chat_id if self.message and self.message.migrate_to_chat_id else self.telegram_id

    @property
    def chat_type(self) -> str:
        chat_type_mapping = {
            "private": "chat",
            "supergroup": "supergroup",
            "group": "faction",
            "channel": "channel"
        }
        return chat_type_mapping.get(self.message.chat.type, "chat") if self.message else "chat"

    @property
    def chat_name(self) -> str:
        return self.message.chat.title if self.message and self.message.chat.title else self.from_username

    @property
    def from_username(self) -> str:
        return self.message.from_user.username if self.message and self.message.from_user and self.message.from_user.username else "Unknown"

    def get_context(self, limit: int) -> List[str]:
        context = self.context_repository.get_context(self.chat_context, limit)
        return random.sample(context, min(len(context), limit))

    @property
    def context(self) -> List[str]:
        return self.get_context(10)

    @property
    def full_context(self) -> List[str]:
        return self.get_context(50)

    @property
    def words(self) -> List[str]:
        return self.get_words()

    @property
    def text(self) -> Optional[str]:
        return self.message.text if self.message else None

    @property
    def chat_context(self) -> str:
        return f"chat_context/{self.chat.id}" if self.chat else ""
