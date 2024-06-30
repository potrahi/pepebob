import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from typing import Optional, List
from sqlalchemy.orm import sessionmaker
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

    def __init__(
            self, config: Config, session_factory: sessionmaker,
            max_no_item_count: int = 5, num_workers: int = 10):
        self.config = config
        self.max_no_item_count = max_no_item_count
        self.session_factory = session_factory
        self.learn_queue_repository = LearnQueueRepository()
        self.num_workers = num_workers

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
                items_processed = self.process_items_parallel()
                logger.debug("Items processed: %d", items_processed)
                if items_processed == 0:
                    no_item_count += 1
                    logger.debug("No item count incremented: %d/%d",
                                 no_item_count, self.max_no_item_count)
                else:
                    no_item_count = 0
                    logger.debug(
                        "Items processed successfully, no_item_count reset")
            except KeyboardInterrupt:
                logger.info("Interrupted by user, shutting down.")
                break
            except RuntimeError as e:
                logger.error("Runtime error: %s", str(e), exc_info=True)
                time.sleep(5)
                no_item_count += 1  # Increment to avoid infinite loop

        logger.debug("No new learn items for a while, finishing execution.")

    def process_items_parallel(self) -> int:
        """
        Retrieves and processes multiple learn items in parallel.

        Returns:
            int: The number of items processed.
        """
        items: List[Optional[LearnItem]] = []
        with self.session_factory():
            try:
                for _ in range(self.num_workers):
                    item = self.learn_queue_repository.pop()
                    if item:
                        items.append(item)
                    else:
                        break
            except (SQLAlchemyError, PyMongoError) as e:
                logger.error("Database error: %s", str(e), exc_info=True)
                time.sleep(5)
                return 0

        valid_items = [item for item in items if item is not None]

        if not items:
            time.sleep(0.1)
            return 0

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = [executor.submit(self.learn, item)
                       for item in valid_items]
            results = [future.result() for future in as_completed(futures)]

        return sum(results)

    def learn(self, item: Optional[LearnItem]) -> bool:
        """
        The core method that performs the learning operation on an item.

        Args:
            item (LearnItem): Learn item to be processed.

        Returns:
            bool: True if an item was processed, False otherwise.
        """
        if not item:
            logger.debug("No learn item found, sleeping for a short period.")
            return False

        logger.debug("Processing learn item: %s", item)
        with self.session_factory() as session:
            try:
                learn_service = LearnService(
                    words=item.message, end_sentence=self.config.end_sentence,
                    chat_id=item.chat_id, session=session
                )
                learn_service.learn_pair()
                return True
            except (SQLAlchemyError, PyMongoError) as e:
                logger.error("Database error: %s", str(e), exc_info=True)
                return False
