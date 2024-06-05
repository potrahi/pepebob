import time
import logging
from typing import Optional
from sqlalchemy.orm import Session
from core.repositories.learn_queue_repository import LearnQueueRepository, LearnItem
from core.services.learn_service import LearnService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Learn:
    learn_queue_repository = LearnQueueRepository()

    @staticmethod
    def run(session: Session):
        while True:
            try:
                Learn.learn(session)
            except Exception as e:
                logger.error(f"Error: {str(e)}", exc_info=True)
                time.sleep(5)

    @staticmethod
    def learn(session: Session):
        learn_item: Optional[LearnItem] = Learn.learn_queue_repository.pop()
        if learn_item:
            logger.debug(f"Processing learn item: {learn_item}")
            learn_service = LearnService(learn_item.message, learn_item.chat_id, session)
            learn_service.learn_pair()
        else:
            logger.debug("No learn item found, sleeping for a short period.")
            time.sleep(0.1)
