from typing import Optional

from telegram import Update

from core.services.story_service import StoryService
from bot.handlers.generic_handler import GenericHandler


class CoolStoryHandler(GenericHandler):
    def __init__(self, update: Update, session):
        super().__init__(update, session)
        self.story_service = None

    def initialize_story_service(self):
        self.story_service = StoryService([], self.full_context, self.chat.id, 50)

    def call(self) -> Optional[str]:
        self.before()
        self.initialize_story_service()
        if self.story_service:
            return self.story_service.generate()
        return None

    @staticmethod
    def apply(update: Update, session):
        return CoolStoryHandler(update, session)
