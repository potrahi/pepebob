from typing import Optional

from sqlalchemy.orm import Session
from telegram import Update

from bot.handlers.generic_handler import GenericHandler


class PingHandler(GenericHandler):
    def __init__(self, update: Update, session: Session):
        super().__init__(update, session)

    def call(self) -> Optional[str]:
        self.before()
        return "Pong."
