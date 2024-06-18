"""
This module defines the CoolStoryHandler class, which handles the creation and
generation of stories based on Telegram updates.
"""

from typing import Optional
from sqlalchemy.orm import Session
from telegram import Update

from core.services.story_service import StoryService
from bot.handlers.generic_handler import GenericHandler
from config import Config


class CoolStoryHandler(GenericHandler):
    """
    Handler class responsible for generating stories using the StoryService.

    Attributes:
        update (Update): The Telegram update object.
        session (Session): The SQLAlchemy session for database operations.
        config (Config): Configuration object.
    """

    def __init__(self, update: Update, session: Session, config: Config):
        """
        Initializes the CoolStoryHandler with the provided update, session, and config.

        Args:
            update (Update): The Telegram update object.
            session (Session): The SQLAlchemy session for database operations.
            config (Config): Configuration object.
        """
        super().__init__(update, session, config)
        self.story_service = self._initialize_story_service()

    def _initialize_story_service(self) -> StoryService:
        """
        Initializes the StoryService with the necessary parameters.

        Returns:
            StoryService: An instance of StoryService configured with the necessary parameters.
        """
        return StoryService(
            words=self.words,
            context=self.full_context,
            chat_id=self.chat.id,
            session=self.session,
            end_sentence=self.config.end_sentence,
            sentences=50
        )

    async def call(self, *args, **kwargs) -> Optional[str]:
        """
        Executes the handler's main functionality to generate a story based on the Telegram update.

        This method performs the following steps:
        1. Calls the `before` method to execute any preliminary actions before handling the update.
        2. Utilizes the `StoryService` to generate a story using the words from the message, 
            the full context of the chat, the chat ID, and the configured end sentence. 
            The story generation is limited to 50 sentences.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Optional[str]: The generated story as a string, or None if the story service is not 
                available or fails to generate a story.
        """

        self.before()
        return self.story_service.generate() if self.story_service else None
