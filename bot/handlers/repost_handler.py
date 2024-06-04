from typing import Optional

from sqlalchemy.orm import Session
from telegram import Update, Bot

from bot.handlers.generic_handler import GenericHandler


class RepostHandler(GenericHandler):
    def __init__(self, update: Update, session: Session, bot: Bot):
        super().__init__(update, session)
        self.bot = bot

    async def call(self) -> Optional[str]:
        self.before()

        if self.can_repost():
            if self.message and self.message.reply_to_message and self.message.chat:
                await self.bot.forward_message(
                    chat_id=self.chat.repost_chat_username,
                    from_chat_id=self.message.chat.id,
                    message_id=self.message.reply_to_message.message_id
                )
                return f"Message forwarded to {self.chat.repost_chat_username}"
        return None

    def can_repost(self) -> bool:
        if not self.message or not self.message.reply_to_message:
            return False

        reply_message = self.message.reply_to_message
        if not reply_message.from_user:
            return False

        from_user = reply_message.from_user
        if not from_user.username:
            return False

        return from_user.username.lower() == self.bot_config.name.lower()

    @staticmethod
    def apply(update: Update, session, bot: Bot):
        return RepostHandler(update, session, bot)
