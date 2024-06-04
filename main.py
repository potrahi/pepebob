import os
import sys
import pytz
import logging
from datetime import datetime
from alembic.config import Config as AlembicConfig
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from core.entities.base_entity import Base
from router import Router
from learn import Learn
from clear_up import CleanUp
from init_config import config


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress debug logs from specific noisy libraries
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

# Set default timezone to UTC
def set_default_timezone():
    utc = pytz.utc
    now = datetime.now(utc)
    logger.info(f"Current time in UTC: {now}")


# Database setup
DATABASE_URI = config.core_config.get_string("database", "url")
logger.debug(f"Database URI: {DATABASE_URI}")
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

logger.debug("Creating database tables if not exist.")
Base.metadata.create_all(engine)

def check_db_connection(engine):
    logger.debug("Checking database connection.")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("Successfully connected to the database.")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")

# Alembic configuration
alembic_path = os.path.join(os.path.dirname(__file__), 'alembic.ini')
logger.debug(f"Alembic configuration path: {alembic_path}")
alembic_cfg = AlembicConfig(alembic_path)

def run_alembic_migrations():
    logger.debug("Running Alembic migrations.")
    try:
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic migrations ran successfully.")
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")

def main():
    if len(sys.argv) < 2:
        logger.error("Missing application argument")
        sys.exit(1)

    set_default_timezone()
    # run_alembic_migrations()
    check_db_connection(engine)

    arg = sys.argv[1]
    logger.debug(f"Application argument: {arg}")
    session = Session()

    try:
        if arg == "learn":
            logger.info("Running learn task")
            Learn.run(session)
        elif arg == "cleanup":
            logger.info("Running cleanup task")
            CleanUp.run(session)
        elif arg == "bot":
            logger.info("Running bot")
            router = Router(config.bot.telegram_token, session)
            router.run()
        else:
            logger.error(f"Unknown application argument: {arg}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred while running the '{arg}' task: {e}")
    finally:
        session.close()
        logger.debug("Database session closed.")

if __name__ == "__main__":
    logger.debug("Starting the application.")
    main()
    logger.debug("Application finished.")
