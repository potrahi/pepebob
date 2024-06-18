"""
Config module for handling application configurations.

This module defines configuration classes for the database, cache, and bot settings,
and loads environment variables to initialize these configurations.
"""

import os
import ast
import logging
from typing import List
from dotenv import load_dotenv, find_dotenv

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class DatabaseConfig:
    """Configuration class for the database."""

    def __init__(self, engine: str, host: str, name: str, port: int,
                 user: str, password: str):
        self.engine = engine
        self.host = host
        self.name = name
        self.port = port
        self.user = user
        self.password = password
        logger.debug("DatabaseConfig initialized: %s", self.url)

    @property
    def url(self):
        """Construct the database URL from the given components."""
        return f"{self.engine}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class CacheConfig:
    """Configuration class for the cache."""

    def __init__(self, host: str = 'mongo', port: int = 27017,
                 name: str = 'cache'):
        self.host = host
        self.port = port
        self.name = name
        logger.debug(
            "CacheConfig initialized: host=%s, port=%d, name=%s", self.host, self.port, self.name)


class BotConfig:
    """Configuration class for the bot."""

    def __init__(self, token: str, name: str, anchors: List[str],
                 async_learn: bool = False, cleanup_limit: int = 1000):
        self.token = token
        self.name = name
        self.anchors = anchors
        self.async_learn = async_learn
        self.cleanup_limit = cleanup_limit
        logger.debug(
            "BotConfig initialized: name=%s, async_learn=%s, cleanup_limit=%d",
            self.name, self.async_learn, self.cleanup_limit)

class Config:
    """Singleton configuration class that loads environment variables."""

    _instance = None
    __initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.debug("Creating new instance of Config")
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        logger.debug("Initializing Config")
        self.load_env()
        self.db = DatabaseConfig(
            engine=self.get_str('DATABASE_ENGINE'),
            host=self.get_str('DATABASE_HOST'),
            name=self.get_str('DATABASE_NAME'),
            port=self.get_int('DATABASE_PORT'),
            user=self.get_str('DATABASE_USER'),
            password=self.get_str('DATABASE_PASSWORD')
        )
        self.cache = CacheConfig(
            host=self.get_str('CACHE_HOST'),
            port=self.get_int('CACHE_PORT'),
            name=self.get_str('CACHE_NAME')
        )
        self.bot = BotConfig(
            token=self.get_str('TELEGRAM_BOT_TOKEN'),
            name=self.get_str('TELEGRAM_BOT_NAME'),
            anchors=self.get_str_list('TELEGRAM_BOT_ANCHORS'),
            async_learn=self.get_boolean('TELEGRAM_BOT_ASYNC_LEARN'),
            cleanup_limit=self.get_int('TELEGRAM_BOT_CLEANUP_LIMIT')
        )
        self.end_sentence = self.get_str_list('PUNCTUATION_END_SENTENCE')
        logger.debug("Config initialization complete")

    def load_env(self) -> None:
        """Load environment variables from the .env file."""
        dotenv_path = find_dotenv()
        if not dotenv_path:
            logger.error("Could not find .env file")
            raise FileNotFoundError("Could not find .env file")
        load_dotenv(dotenv_path)
        logger.debug(".env file loaded")

    def is_empty(self, key: str, value: str) -> bool:
        """Check if a given key or value is empty."""
        if key == '' or value == '':
            logger.warning("Key: '%s' or value: '%s' is empty", key, value)
            return True
        return False

    def get_boolean(self, key: str) -> bool:
        """Get a boolean value from environment variables."""
        value = os.getenv(key, '')
        if not self.is_empty(key, value):
            try:
                result = bool(ast.literal_eval(value.capitalize()))
                logger.debug("Boolean value for %s: %s", key, result)
                return result
            except (SyntaxError, ValueError):
                logger.error("Error parsing boolean value for key: '%s'", key)
                return False
        return False

    def get_int(self, key: str) -> int:
        """Get an integer value from environment variables."""
        value = os.getenv(key, '')
        if not self.is_empty(key, value):
            try:
                result = int(value)
                logger.debug("Integer value for %s: %d", key, result)
                return result
            except ValueError:
                logger.error(
                    "Error: '%s' in '%s' is not a valid integer and will be ignored", value, key)
                return 0
        return 0

    def get_str(self, key: str) -> str:
        """Get a string value from environment variables."""
        value = os.getenv(key, '')
        if not self.is_empty(key, value):
            logger.debug("String value for %s: %s", key, value)
            return value
        return ''

    def get_int_list(self, key: str) -> List[int]:
        """Get a list of integers from environment variables."""
        value = os.getenv(key, '')
        if not self.is_empty(key, value):
            try:
                result = [int(item) for item in value.split(',')]
                logger.debug("Integer list for %s: %s", key, result)
                return result
            except ValueError:
                logger.error(
                    "Error parsing list of integers for key: '%s'", key)
                return []
        return []

    def get_str_list(self, key: str) -> List[str]:
        """Get a list of strings from environment variables."""
        value = os.getenv(key, '')
        if not self.is_empty(key, value):
            result = value.split(',')
            logger.debug("String list for %s: %s", key, result)
            return result
        return []
