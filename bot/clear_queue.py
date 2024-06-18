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

    learn_queue = LearnQueueRepository()

    @staticmethod
    def run():
        """
        Continuously tries to clean the learn queue until successful.
        Logs the success or any database errors encountered.
        """
        while True:
            try:
                CleanQueue._clean_up()
                logger.info("Learn queue has been cleared.")
                break
            except PyMongoError as e:
                logger.error(
                    "Database error occurred during cleanup: %s", e, exc_info=True)
                time.sleep(5)

    @staticmethod
    def _clean_up():
        """Clears the learn queue by calling the clear method of the repository."""
        CleanQueue.learn_queue.clear()
