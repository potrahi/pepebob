from typing import Optional

import requests
from sqlalchemy.orm import Session
from telegram import Update

from core.repositories.chat_repository import ChatRepository
from bot.handlers.generic_handler import GenericHandler


class SetRepostChatHandler(GenericHandler):
    ADMIN_STATUSES = ["creator", "administrator"]

    def __init__(self, update: Update, chat_member_request_url: Optional[str], session: Session):
        super().__init__(update, session)
        self.chat_member_request_url = chat_member_request_url

    def call(self, chat_username: str) -> Optional[str]:
        self.before()

        if self.can_set_repost_chat():
            ChatRepository().update_repost_chat(self.session, self.chat.id, chat_username)
            return f"Ya wohl, Lord Helmet! Setting repost channel to {chat_username}"
        else:
            return None

    def can_set_repost_chat(self) -> bool:
        if not self.chat_member_request_url:
            return False

        try:
            response = requests.get(self.chat_member_request_url, timeout=60)
            response.raise_for_status()
            chat_member = response.json()
            return chat_member.get('status') in self.ADMIN_STATUSES
        except requests.Timeout:
            return False
        except requests.RequestException:
            return False
