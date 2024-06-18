import time
import logging
from core.repositories.learn_queue_repository import LearnQueueRepository

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CleanQueue:
    learn_queue = LearnQueueRepository()
    
    @staticmethod
    def run():
        while True:
            try:
                CleanQueue.clean_up()
                logger.info("Learn queue has been cleared.")
                break
            except Exception as e:
                logger.error(f"Exception occurred during cleanup: {e}", exc_info=True)
                time.sleep(5)

    @staticmethod
    def clean_up():
        CleanQueue.learn_queue.clear()