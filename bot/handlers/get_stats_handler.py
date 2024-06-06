from typing import Optional

from telegram import Update
from sqlalchemy.orm import Session

from core.repositories.pair_repository import PairRepository
from bot.handlers.generic_handler import GenericHandler


class GetStatsHandler(GenericHandler):
    def __init__(self, update: Update, session: Session):
        super().__init__(update, session)

    def call(self) -> Optional[str]:
        self.before()
        count = PairRepository().get_pairs_count(self.session, self.chat.id)
        return f"Known pairs in this chat: {count}."
