from typing import Optional

from sqlalchemy.orm import Session
from telegram import Update

from bot.handlers.generic_handler import GenericHandler
from config import Config

class GetRepostChatHandler(GenericHandler):
    def __init__(self, update: Update, session: Session, config: Config):
        super().__init__(update, session, config)

    async def call(self) -> Optional[str]:
        self.before()

        repost_chat_username = self.chat.repost_chat_username
        if repost_chat_username:
            return f"Pidorskie quote is on {repost_chat_username}"
        return None