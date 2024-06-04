from typing import Optional

from telegram import Update

from bot.handlers.generic_handler import GenericHandler


class GetRepostChatHandler(GenericHandler):
    def __init__(self, update: Update, session):
        super().__init__(update, session)

    def call(self) -> Optional[str]:
        self.before()

        repost_chat_username = self.chat.repost_chat_username
        if repost_chat_username:
            return f"Pidorskie quote is on {repost_chat_username}"
        return None

    @staticmethod
    def apply(update: Update, session):
        return GetRepostChatHandler(update, session)
