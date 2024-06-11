from typing import Optional

from telegram import Update
from sqlalchemy.orm import Session

from core.repositories.pair_repository import PairRepository
from bot.handlers.generic_handler import GenericHandler
from config import Config

class GetStatsHandler(GenericHandler):
    def __init__(self, update: Update, session: Session, config: Config):
        super().__init__(update, session, config)

    def call(self) -> Optional[str]:
        self.before()
        count = PairRepository().get_pairs_count(self.session, self.chat.id)
        return f"Known pairs in this chat: {count}."
