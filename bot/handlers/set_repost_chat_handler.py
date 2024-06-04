from typing import Optional

import asyncio
from telegram import Update

from core.repositories.chat_repository import ChatRepository
from bot.handlers.generic_handler import GenericHandler


class SetRepostChatHandler(GenericHandler):
    ADMIN_STATUSES = ["creator", "administrator"]

    def __init__(self, update: Update, chat_member_request: Optional[asyncio.Future], session):
        super().__init__(update, session)
        self.chat_member_request = chat_member_request

    async def call(self, chat_username: str) -> Optional[str]:
        self.before()

        if await self.can_set_repost_chat():
            ChatRepository().update_repost_chat(self.session, self.chat.id, chat_username)
            return f"Ya wohl, Lord Helmet! Setting repost channel to {chat_username}"
        else:
            return None

    async def can_set_repost_chat(self) -> bool:
        if not self.chat_member_request:
            return False

        try:
            chat_member = await asyncio.wait_for(self.chat_member_request, timeout=60)
            return chat_member.status in self.ADMIN_STATUSES
        except asyncio.TimeoutError:
            return False

    @staticmethod
    def apply(update: Update, chat_member_request: Optional[asyncio.Future], session):
        return SetRepostChatHandler(update, chat_member_request, session)
