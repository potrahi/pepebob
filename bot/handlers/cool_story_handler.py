from typing import Optional

from sqlalchemy.orm import Session
from telegram import Update

from core.services.story_service import StoryService
from bot.handlers.generic_handler import GenericHandler


class CoolStoryHandler(GenericHandler):
    def __init__(self, update: Update, session: Session):
        super().__init__(update, session)
        self.story_service = StoryService(self.words, self.full_context, self.chat.id, self.session, 50)

    def call(self) -> Optional[str]:
        self.before()
        if self.story_service:
            return self.story_service.generate()
        return None
