"""
Module for processing learning items from a queue using multiple threads.

This module defines the Learn class which is responsible for fetching learning items 
from a queue and processing them using a pool of worker threads. It handles 
database interactions with SQLAlchemy and MongoDB, and provides robust error handling 
for different types of exceptions that might occur during processing.
"""

import time
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from pymongo.errors import PyMongoError
from core.repositories.learn_queue_repository import LearnQueueRepository, LearnItem
from core.services.learn_service import LearnService
from config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class Learn:
    """Class responsible for processing learning items from the queue using multiple threads."""

    max_workers = 5
    max_no_item_count = 50

    @staticmethod
    def run():
        """
        Main method to start processing learn items.
        It initializes the necessary configurations and manages the worker threads.
        """
        no_item_count = 0

        config = Config()
        engine = create_engine(config.db.url)
        session_local = sessionmaker(
            autocommit=False, autoflush=False, bind=engine)
        learn_queue_repository = LearnQueueRepository()

        with ThreadPoolExecutor(max_workers=Learn.max_workers) as executor:
            futures = []
            while no_item_count < Learn.max_no_item_count:
                try:
                    if len(futures) < Learn.max_workers:
                        futures.append(
                            executor.submit(
                                Learn.process_item, session_local, learn_queue_repository
                            )
                        )
                    else:
                        for future in as_completed(futures):
                            item_processed = future.result()
                            futures.remove(future)
                            if not item_processed:
                                no_item_count += 1
                                logger.debug(
                                    "No item count: %d/%d", no_item_count, Learn.max_no_item_count)
                            else:
                                no_item_count = 0
                except KeyboardInterrupt:
                    logger.info("Interrupted by user, shutting down.")
                    break
                except RuntimeError as e:
                    logger.error("Runtime error: %s", str(e), exc_info=True)
                    time.sleep(5)
                    no_item_count = 0

            logger.debug("No new learn items for a while, finishing execution.")

    @staticmethod
    def process_item(session_local, learn_queue_repository) -> bool:
        """
        Retrieves and processes a single learn item.

        Args:
            session_local: SQLAlchemy session factory.
            learn_queue_repository: Repository to manage the learn queue.

        Returns:
            bool: True if an item was processed, False otherwise.
        """
        session = session_local()
        try:
            return Learn.learn(session, learn_queue_repository)
        finally:
            session.close()

    @staticmethod
    def learn(session: Session, learn_queue_repository: LearnQueueRepository) -> bool:
        """
        The core method that performs the learning operation on an item.

        Args:
            session (Session): SQLAlchemy session.
            learn_queue_repository (LearnQueueRepository): Repository to manage the learn queue.

        Returns:
            bool: True if an item was processed, False otherwise.
        """
        try:
            learn_item: Optional[LearnItem] = learn_queue_repository.pop()
            if learn_item:
                logger.debug("Processing learn item: %s", learn_item)
                learn_service = LearnService(
                    learn_item.message, learn_item.chat_id, session)
                learn_service.learn_pair()
                return True
            else:
                logger.debug("No learn item found, sleeping for a short period.")
                time.sleep(0.1)
                return False
        except (SQLAlchemyError, PyMongoError) as e:
            logger.error("Database error: %s", str(e), exc_info=True)
            time.sleep(5)
            return False
