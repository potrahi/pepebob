"""
This module contains the CleanQueue class which handles the process
of cleaning the learn queue in the repository. It includes methods
for running the cleanup process and handling potential database errors.
"""

import time
import logging
from pymongo.errors import PyMongoError
from core.repositories.learn_queue_repository import LearnQueueRepository

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class CleanQueue:
    """Class to handle cleaning the learn queue in the repository."""

    def __init__(self, learn_queue_repository=None, retry_delay=5):
        """
        Initialize the CleanQueue with a LearnQueueRepository instance.

        :param learn_queue_repository: Instance of LearnQueueRepository.
        :param retry_delay: Time to wait between retries in seconds.
        """
        self.learn_queue = learn_queue_repository or LearnQueueRepository()
        self.retry_delay = retry_delay

    def run(self):
        """
        Continuously tries to clean the learn queue until successful.
        Logs the success or any database errors encountered.
        """
        while True:
            try:
                self._clean_up()
                logger.info("Learn queue has been cleared successfully.")
                break
            except PyMongoError as e:
                logger.error(
                    "Database error occurred during cleanup: %s", e, exc_info=True)
                time.sleep(self.retry_delay)

    def _clean_up(self):
        """Clears the learn queue by calling the clear method of the repository."""
        self.learn_queue.clear()
        logger.debug("Called clear method on learn queue repository.")
