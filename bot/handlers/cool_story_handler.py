from typing import Optional

from sqlalchemy.orm import Session
from telegram import Update

from core.services.story_service import StoryService
from bot.handlers.generic_handler import GenericHandler
from config import Config

class CoolStoryHandler(GenericHandler):
    def __init__(self, update: Update, session: Session, config: Config):
        super().__init__(update, session, config)
        self.story_service = StoryService(
            words=self.words, 
            context=self.full_context, 
            chat_id=self.chat.id, 
            session=self.session,
            end_sentence=self.config.end_sentence, 
            sentences=50)

    def call(self) -> Optional[str]:
        self.before()
        if self.story_service:
            return self.story_service.generate()
        return None
