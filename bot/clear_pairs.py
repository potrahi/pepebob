"""
This module contains the CleanPairs class, which is responsible for periodically 
cleaning up old pairs from the database based on the configuration settings.
"""

import time
import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from core.repositories.pair_repository import PairRepository
from config import Config

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class CleanPairs:
    """Class for cleaning up old pairs from the database."""

    def __init__(self, pair_repository=None, retry_delay: int = 5):
        """
        Initialize the CleanPairs with a PairRepository instance and retry delay.

        Args:
            pair_repository (PairRepository): Instance of PairRepository.
            retry_delay (int): Time to wait between retries in seconds.
        """
        self.pair_repository = pair_repository or PairRepository()
        self.retry_delay = retry_delay

    def run(self, session: Session, config: Config):
        """
        Continuously run the cleanup process in an infinite loop.

        Args:
            session (Session): SQLAlchemy session object.
            config (Config): Configuration object containing settings.
        """
        while True:
            try:
                self.clean_up(session, config)
            except (SQLAlchemyError, ValueError, RuntimeError, OSError) as e:
                self._handle_exception(e)
                time.sleep(self.retry_delay)

    def clean_up(self, session: Session, config: Config):
        """
        Perform the cleanup operation by removing old pairs from the database.

        Args:
            session (Session): SQLAlchemy session object.
            config (Config): Configuration object containing settings.
        """
        try:
            with session.begin():
                removed_ids: List[int] = self.pair_repository.remove_old(
                    session, config.bot.cleanup_limit)

                if not removed_ids:
                    logger.info("No pairs to remove.")
                else:
                    logger.info(
                        "Removed %d pairs: %s", len(removed_ids), ', '.join(map(str, removed_ids)))
        except (SQLAlchemyError, ValueError, RuntimeError, OSError) as e:
            self._handle_exception(e)
            raise

    def _handle_exception(self, e: Exception):
        """
        Handle exceptions by logging appropriate error messages.

        Args:
            e (Exception): The exception that occurred.
        """
        if isinstance(e, SQLAlchemyError):
            logger.error(
                "Database error occurred during cleanup: %s", e, exc_info=True)
        elif isinstance(e, ValueError):
            logger.error(
                "Configuration error occurred during cleanup: %s", e, exc_info=True)
        elif isinstance(e, RuntimeError):
            logger.error(
                "Runtime error occurred during cleanup: %s", e, exc_info=True)
        elif isinstance(e, OSError):
            logger.error(
                "OS error occurred during cleanup: %s", e, exc_info=True)
        else:
            logger.error(
                "Unexpected error occurred during cleanup: %s", e, exc_info=True)
