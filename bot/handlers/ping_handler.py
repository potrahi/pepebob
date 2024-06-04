from typing import Optional

from telegram import Update

from bot.handlers.generic_handler import GenericHandler


class PingHandler(GenericHandler):
    def __init__(self, update: Update, session):
        super().__init__(update, session)

    def call(self) -> Optional[str]:
        self.before()
        return "Pong."

    @staticmethod
    def apply(update: Update, session):
        return PingHandler(update, session)
