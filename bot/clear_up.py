import time
import logging
from typing import List
from sqlalchemy.orm import Session

from core.repositories.pair_repository import PairRepository
from config import Config

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CleanUp:
    
    @staticmethod
    def run(session: Session):
        while True:
            try:
                CleanUp.clean_up(session)
            except Exception as e:
                logger.error(f"Exception occurred during cleanup: {e}", exc_info=True)
                time.sleep(5)

    @staticmethod
    def clean_up(session: Session):
        with session:
            removed_ids: List[int] = PairRepository().remove_old(session, Config().bot.cleanup_limit)

            if not removed_ids:
                logger.info("Nothing to remove")
                time.sleep(5)
            else:
                logger.info(f"Removed pairs {len(removed_ids)} ({', '.join(map(str, removed_ids))})")