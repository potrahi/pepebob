import time
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pymongo.errors import PyMongoError
from core.repositories.learn_queue_repository import LearnQueueRepository, LearnItem
from core.services.learn_service import LearnService
from config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class Learn:
    """Class responsible for processing learning items from the queue sequentially."""

    def __init__(self, config: Config, session: Session, max_no_item_count: int = 5):
        self.config = config
        self.max_no_item_count = max_no_item_count
        self.session = session
        self.learn_queue_repository = LearnQueueRepository()

    def run(self) -> None:
        """
        Main method to start processing learn items.
        It initializes the necessary configurations and processes items one by one.
        """
        no_item_count = 0

        while no_item_count < self.max_no_item_count:
            logger.debug(
                "Starting processing cycle with no_item_count: %d", no_item_count)
            try:
                item_processed = self.process_item()
                logger.debug("Item processed: %s", item_processed)
                if not item_processed:
                    no_item_count += 1
                    logger.debug("No item count incremented: %d/%d",
                                 no_item_count, self.max_no_item_count)
                else:
                    no_item_count = 0
                    logger.debug(
                        "Item processed successfully, no_item_count reset")
            except KeyboardInterrupt:
                logger.info("Interrupted by user, shutting down.")
                break
            except RuntimeError as e:
                logger.error("Runtime error: %s", str(e), exc_info=True)
                time.sleep(5)
                no_item_count += 1  # Increment to avoid infinite loop

        logger.debug("No new learn items for a while, finishing execution.")

    def process_item(self) -> bool:
        """
        Retrieves and processes a single learn item.

        Returns:
            bool: True if an item was processed, False otherwise.
        """
        with self.session as session:
            try:
                return self.learn(session)
            except (SQLAlchemyError, PyMongoError) as e:
                logger.error("Database error: %s", str(e), exc_info=True)
                time.sleep(5)
                return False

    def learn(self, session: Session) -> bool:
        """
        The core method that performs the learning operation on an item.

        Args:
            session (Session): SQLAlchemy session.

        Returns:
            bool: True if an item was processed, False otherwise.
        """
        learn_item: Optional[LearnItem] = self.learn_queue_repository.pop()
        if not learn_item:
            logger.debug("No learn item found, sleeping for a short period.")
            time.sleep(0.1)
            return False

        logger.debug("Processing learn item: %s", learn_item)
        learn_service = LearnService(
            words=learn_item.message, end_sentence=self.config.end_sentence,
            chat_id=learn_item.chat_id, session=session
        )
        learn_service.learn_pair()
        return True
