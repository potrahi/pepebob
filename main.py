import os
import sys
import pytz
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from bot.clear_queue import CleanQueue
from bot.router import Router
from bot.learn import Learn
from bot.clear_up import CleanUp
from config import Config


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress debug logs from specific noisy libraries
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('pymongo').setLevel(logging.WARNING)

# Set default timezone to UTC
def set_default_timezone():
    utc = pytz.utc
    now = datetime.now(utc)
    logger.info(f"Current time in UTC: {now}")

if sys.argv[1] != 'learn':
    config = Config()

    # Database setup
    DATABASE_URL = config.db.url
    logger.debug(f"Database URI: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)

def check_db_connection(engine):
    logger.debug("Checking database connection.")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("Successfully connected to the database.")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")

def main():
    if len(sys.argv) < 2:
        logger.error("Missing application argument")
        sys.exit(1)

    set_default_timezone()
    if sys.argv[1] != 'learn':
        check_db_connection(engine)
        session = Session()

    arg = sys.argv[1]
    logger.debug(f"Application argument: {arg}")

    try:
        if arg == "learn":
            logger.info("Running learn task")
            Learn.run()
        elif arg == "cleanup":
            logger.info("Running cleanup task")
            CleanUp.run(session)
        elif arg == "clearqueue":
            logger.info("Running clean learn queue task")
            CleanQueue.run()
        elif arg == "bot":
            logger.info("Running bot")
            router = Router(config, session)
            router.run()
        else:
            logger.error(f"Unknown application argument: {arg}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred while running the '{arg}' task: {e}")
    finally:
        if sys.argv[1] != 'learn':
            session.close()
            logger.debug("Database session closed.")

if __name__ == "__main__":
    logger.debug("Starting the application.")
    main()
    logger.debug("Application finished.")
