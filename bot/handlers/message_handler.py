"""
This module defines the MessageHandler class responsible for handling 
incoming messages, learning new words, and generating stories based 
on specific conditions using Telegram bot updates.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from telegram import Update

from core.repositories.learn_queue_repository import LearnQueueRepository
from core.services.learn_service import LearnService
from core.services.story_service import StoryService
from bot.handlers.generic_handler import GenericHandler
from config import Config

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class MessageHandler(GenericHandler):
    """Handler for processing messages and generating stories based on specific conditions."""

    def __init__(self, update: Update, session: Session, config: Config):
        """Initialize the MessageHandler with update, session, and config."""
        super().__init__(update, session, config)
        self.learn_service = LearnService(
            words=self.words, chat_id=self.chat.id, session=self.session
        )
        self.story_service = StoryService(
            words=self.words,
            context=self.context,
            chat_id=self.chat.id,
            session=self.session,
            end_sentence=self.config.end_sentence
        )
        logger.debug("MessageHandler initialized")

    async def call(self, *args, **kwargs) -> Optional[str]:
        """
        Main method to process the message and possibly generate a story.

        This method performs the following steps:
        1. Calls the `before` method to execute any preliminary actions before handling the update.
        2. Checks if the message has text and is not an edition (i.e., not edited). If not, 
            logs the condition and exits.
        3. Logs the receipt of the message, including the text, chat name, and migration ID.
        4. Calls the `_learn` method to learn the words from the message based on the bot's 
            asynchronous configuration.
        5. Updates the chat context with the words from the message using the context repository.
        6. Checks if the `StoryService` is available. If not, logs the condition and exits.
        7. Calls the `_should_generate_story` method to determine if a story should be generated 
            based on various conditions.
        8. If conditions are met for generating a story, logs the condition and generates the 
            story using the `StoryService`.
        9. If no conditions are met for generating a story, logs the condition and exits.

        Args:
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Optional[str]: The generated story if conditions are met, or None if no story is 
                generated or conditions are not met.
        """
        self.before()

        if not self.has_text or self.is_edition:
            logger.debug("No text or message is an edition, exiting")
            return None

        logger.info(
            "Message received: %s from %s (%s)",
            self.text or '',
            self.chat_name,
            self.migration_id
        )

        self._learn()
        self.context_repository.update_context(self.chat_context, self.words)
        logger.debug("Context updated")

        if self.story_service is None:
            logger.debug("StoryService is None, exiting")
            return None

        if self._should_generate_story():
            logger.debug("Conditions met for generating story")
            return self.story_service.generate()

        logger.debug("No conditions met for generating story")
        return None

    def _learn(self) -> None:
        """Learn the words based on the async configuration."""
        if self.config.bot.async_learn:
            logger.debug("Async learn enabled, pushing to learn queue")
            LearnQueueRepository().push(self.words, self.chat.id)
        else:
            logger.debug("Async learn disabled, learning pair immediately")
            self.learn_service.learn_pair()

    def _should_generate_story(self) -> bool:
        """Determine if a story should be generated based on various conditions."""
        return (
            self.is_reply_to_bot or
            self.is_mentioned or
            self.is_private or
            self.has_anchors or
            self.is_random_answer
        )
