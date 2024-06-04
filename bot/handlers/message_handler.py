import logging
from typing import Optional
from sqlalchemy.orm import Session
from telegram import Update

from core.repositories.learn_queue_repository import LearnQueueRepository
from core.services.learn_service import LearnService
from core.services.story_service import StoryService
from bot.handlers.generic_handler import GenericHandler

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MessageHandler(GenericHandler):
    def __init__(self, update: Update, session: Session):
        super().__init__(update, session)
        self.learn_service = LearnService(
            self.words, self.chat.id, self.session)
        self.learn_queue_repository = LearnQueueRepository()
        self.story_service = None
        logger.debug("MessageHandler initialized")

    def initialize_services(self):
        self.story_service = StoryService(
            words=self.words, context=self.context, chat_id=self.chat.id, session=self.session)
        logger.debug("StoryService initialized")

    def call(self) -> Optional[str]:
        self.before()

        if not self.has_text or self.is_edition:
            logger.debug("No text or message is an edition, exiting")
            return None

        logger.info(f"Message received: {self.text or ''} from {self.chat_name} ({self.migration_id})")

        self.learn()
        self.context_repository.update_context(self.chat_context, self.words)
        logger.debug("Context updated")

        self.initialize_services()

        if self.story_service is None:
            logger.debug("StoryService is None, exiting")
            return None

        if self.is_reply_to_bot:
            logger.debug("Message is a reply to bot, generating story")
            return self.story_service.generate()
        if self.is_mentioned:
            logger.debug("Message mentions bot, generating story")
            return self.story_service.generate()
        if self.is_private:
            logger.debug("Message is private, generating story")
            return self.story_service.generate()
        if self.has_anchors:
            logger.debug("Message has anchors, generating story")
            return self.story_service.generate()
        if self.is_random_answer:
            logger.debug("Message is a random answer, generating story")
            return self.story_service.generate()

        logger.debug("No conditions met for generating story")
        return None

    def learn(self) -> None:
        if self.bot_config.async_learn:
            logger.debug("Async learn enabled, pushing to learn queue")
            self.learn_queue_repository.push(self.words, self.chat.id)
        else:
            logger.debug("Async learn disabled, learning pair immediately")
            self.learn_service.learn_pair()

    @staticmethod
    def apply(update: Update, session):
        logger.debug("Applying MessageHandler")
        return MessageHandler(update, session)
