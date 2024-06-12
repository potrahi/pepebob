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

    @staticmethod
    def run(session: Session, config: Config):
        """
        Continuously run the cleanup process in an infinite loop.

        Args:
            session (Session): SQLAlchemy session object.
            config (Config): Configuration object containing settings.
        """
        while True:
            try:
                CleanPairs.clean_up(session, config)
            except (SQLAlchemyError, ValueError, RuntimeError, OSError) as e:
                CleanPairs._handle_exception(e)
                time.sleep(5)

    @staticmethod
    def clean_up(session: Session, config: Config):
        """
        Perform the cleanup operation by removing old pairs from the database.

        Args:
            session (Session): SQLAlchemy session object.
            config (Config): Configuration object containing settings.
        """
        try:
            with session.begin():
                pair_repo = PairRepository()
                removed_ids: List[int] = pair_repo.remove_old(
                    session, config.bot.cleanup_limit)

                if not removed_ids:
                    logger.info("Nothing to remove")
                else:
                    logger.info(
                        "Removed %d pairs: %s", len(removed_ids), ', '.join(map(str, removed_ids)))
        except (SQLAlchemyError, ValueError, RuntimeError, OSError) as e:
            CleanPairs._handle_exception(e)
            raise

    @staticmethod
    def _handle_exception(e: Exception):
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
