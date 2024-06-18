from typing import Optional

from sqlalchemy.orm import Session
from telegram import Update

from bot.handlers.generic_handler import GenericHandler
from config import Config

class PingHandler(GenericHandler):
    def __init__(self, update: Update, session: Session,  config: Config):
        super().__init__(update, session, config)

    async def call(self) -> Optional[str]:
        self.before()
        return "Pong."
