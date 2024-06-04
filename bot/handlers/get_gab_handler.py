from typing import Optional

from telegram import Update

from bot.handlers.generic_handler import GenericHandler


class GetGabHandler(GenericHandler):
    def __init__(self, update: Update, session):
        super().__init__(update, session)

    def call(self) -> Optional[str]:
        self.before()
        return f"Pizdlivost level is on {self.chat.random_chance}"

    @staticmethod
    def apply(update: Update, session):
        return GetGabHandler(update, session)
