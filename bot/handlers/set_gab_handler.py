from typing import Optional

from sqlalchemy.orm import Session
from telegram import Update

from core.repositories.chat_repository import ChatRepository
from bot.handlers.generic_handler import GenericHandler
from config import Config

class SetGabHandler(GenericHandler):
    def __init__(self, update: Update, session: Session, config: Config):
        super().__init__(update, session, config)

    async def call(self, level: int) -> Optional[str]:
        self.before()

        if level > 50 or level < 0:
            return "0-50 allowed, Dude!"

        ChatRepository().update_random_chance(self.session, self.chat.id, level)
        return f"Ya wohl, Lord Helmet! Setting gab to {level}"