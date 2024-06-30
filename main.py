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
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress debug logs from specific noisy libraries
for lib in ['httpcore', 'httpx', 'telegram', 'asyncio', 'pymongo']:
    logging.getLogger(lib).setLevel(logging.WARNING)


def set_default_timezone():
    """Set the default timezone to UTC and log the current time."""
    now = datetime.now(pytz.utc)
    logger.info("Current time in UTC: %s", now)


def get_config():
    """Retrieve and return the configuration."""
    return Config()


def setup_database(config):
    """Set up the database connection and return the engine and session."""
    logger.debug("Database URI: %s", config.db.url)
    engine = create_engine(config.db.url)
    SessionFactory = sessionmaker(bind=engine)
    return engine, SessionFactory


def check_db_connection(engine):
    """Check the database connection and log the result."""
    logger.debug("Checking database connection.")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("Successfully connected to the database.")
    except (OperationalError, ProgrammingError, DatabaseError) as e:
        logger.error("Database connection error: %s", e)


def run_task(arg, config, session_factory):
    """Run the specified task based on the argument."""
    tasks = {
        "learn": lambda: Learn(config=config, session_factory=session_factory).run(),
        "clearpairs": lambda: run_with_session(CleanPairs().run, session_factory, config),
        "clearqueue": lambda: CleanQueue().run(),
        "bot": lambda: Router(config=config, session_factory=session_factory).run(),
    }

    task = tasks.get(arg)
    if task:
        try:
            logger.info("Running %s task", arg)
            task()
        except (ConnectionError, RuntimeError) as e:
            logger.error(
                "An error occurred while running the '%s' task: %s", arg, e)
    else:
        logger.error("Unknown application argument: %s", arg)
        sys.exit(1)


def run_with_session(task_func, session_factory, *args):
    """Run a task function with a session and ensure the session is closed afterwards."""
    session = session_factory()
    try:
        task_func(session, *args)
    finally:
        session.close()


def main():
    """Main function to start the application."""
    if len(sys.argv) < 2:
        logger.error("Missing application argument")
        sys.exit(1)

    set_default_timezone()

    arg = sys.argv[1]
    logger.debug("Application argument: %s", arg)

    config = get_config()
    engine, session_factory = setup_database(config)
    check_db_connection(engine)

    run_task(arg, config, session_factory)

    logger.debug("Database session closed.")


if __name__ == "__main__":
    logger.debug("Starting the application.")
    main()
    logger.debug("Application finished.")
