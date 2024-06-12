"""
This module is the main entry point for the bot application.
It handles different tasks such as learning, pairs and learnqueue clearing, and bot operations.
The module sets up logging, configures the database connection, and dispatches tasks 
    based on the command-line argument.
"""

import logging
import sys
from datetime import datetime
import pytz
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, ProgrammingError, DatabaseError
from bot.clear_queue import CleanQueue
from bot.clear_pairs import CleanPairs
from bot.learn import Learn
from bot.router import Router
from config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress debug logs from specific noisy libraries
suppress_logging_for_libraries = ['httpcore', 'httpx', 'telegram', 'asyncio', 'pymongo']
for lib in suppress_logging_for_libraries:
    logging.getLogger(lib).setLevel(logging.WARNING)

def set_default_timezone():
    """Set the default timezone to UTC and log the current time."""
    utc = pytz.utc
    now = datetime.now(utc)
    logger.info("Current time in UTC: %s", now)

def get_config():
    """Retrieve and return the configuration."""
    return Config()

def setup_database(config):
    """Set up the database connection and return the engine and session."""
    logger.debug("Database URI: %s", config.db.url)
    engine = create_engine(config.db.url)
    session = sessionmaker(bind=engine)
    return engine, session

def check_db_connection(engine):
    """Check the database connection and log the result."""
    logger.debug("Checking database connection.")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("Successfully connected to the database.")
    except OperationalError as e:
        logger.error("Operational error while connecting to the database: %s", e)
    except ProgrammingError as e:
        logger.error("Programming error while connecting to the database: %s", e)
    except DatabaseError as e:
        logger.error("General database error: %s", e)

def run_task(arg, config=None, session=None):
    """Run the specified task based on the argument."""
    try:
        if arg == "learn":
            logger.info("Running learn task")
            Learn.run()
        elif arg == "clearpairs":
            if session and config:
                logger.info("Running clear pairs task")
                CleanPairs.run(session, config)
        elif arg == "clearqueue":
            logger.info("Running clear learn queue task")
            CleanQueue.run()
        elif arg == "bot":
            if config and session:
                logger.info("Running bot")
                router = Router(config, session)
                router.run()
        else:
            logger.error("Unknown application argument: %s", arg)
            sys.exit(1)
    except (ConnectionError, RuntimeError) as e:
        logger.error("An error occurred while running the '%s' task: %s", arg, e)

def main():
    """Main function to start the application."""
    if len(sys.argv) < 2:
        logger.error("Missing application argument")
        sys.exit(1)

    set_default_timezone()

    arg = sys.argv[1]
    logger.debug("Application argument: %s", arg)

    if arg != 'learn':
        config = get_config()
        engine, session = setup_database(config)
        check_db_connection(engine)
        session = session()

    run_task(arg, config if arg != 'learn' else None, session if arg != 'learn' else None)

    if arg != 'learn' and 'session' in locals():
        session.close()
        logger.debug("Database session closed.")

if __name__ == "__main__":
    logger.debug("Starting the application.")
    main()
    logger.debug("Application finished.")
