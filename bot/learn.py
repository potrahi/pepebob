import time
import logging
from typing import Optional
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from pymongo.errors import PyMongoError
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.repositories.learn_queue_repository import LearnQueueRepository, LearnItem
from core.services.learn_service import LearnService
from config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Learn:
    max_workers = 5  # Adjust the number of threads as needed

    @staticmethod
    def run():
        no_item_count = 0
        max_no_item_count = 50  # Adjust this threshold as needed

        config = Config()
        engine = create_engine(config.db.url)
        session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        learn_queue_repository = LearnQueueRepository()

        with ThreadPoolExecutor(max_workers=Learn.max_workers) as executor:
            futures = []
            while True:
                try:
                    if len(futures) < Learn.max_workers:
                        futures.append(executor.submit(Learn.process_item, session_local, learn_queue_repository))
                    else:
                        for future in as_completed(futures):
                            item_processed = future.result()
                            futures.remove(future)
                            if not item_processed:
                                no_item_count += 1
                                if no_item_count >= max_no_item_count:
                                    logger.debug("No new learn items for a while, finishing execution.")
                                    return
                            else:
                                no_item_count = 0  # Reset count if an item was processed
                except Exception as e:
                    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                    time.sleep(5)
                    no_item_count = 0  # Reset count if an error occurred

    @staticmethod
    def process_item(sesstion_local, learn_queue_repository) -> bool:
        session = sesstion_local()
        try:
            return Learn.learn(session, learn_queue_repository)
        finally:
            session.close()

    @staticmethod
    def learn(session: Session, learn_queue_repository: LearnQueueRepository) -> bool:
        try:
            learn_item: Optional[LearnItem] = learn_queue_repository.pop()
            if learn_item:
                logger.debug(f"Processing learn item: {learn_item}")
                learn_service = LearnService(learn_item.message, learn_item.chat_id, session)
                learn_service.learn_pair()
                return True
            else:
                logger.debug("No learn item found, sleeping for a short period.")
                time.sleep(0.1)
                return False
        except SQLAlchemyError as e:
            logger.error(f"PostgreSQL error: {str(e)}", exc_info=True)
            time.sleep(5)  # Delay before retrying
            return False
        except PyMongoError as e:
            logger.error(f"MongoDB error: {str(e)}", exc_info=True)
            time.sleep(5)  # Delay before retrying
            return False
        except Exception as e:
            logger.error(f"Unexpected error in learn method: {str(e)}", exc_info=True)
            time.sleep(5)  # Delay before retrying
            return False
