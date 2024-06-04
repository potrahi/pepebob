import logging
import configparser
import os

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CoreConfig:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.debug("Creating new instance of CoreConfig")
            cls._instance = super(CoreConfig, cls).__new__(cls, *args, **kwargs)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        logger.debug("Initializing CoreConfig")
        self.config = self.load_config()
        self.__initialized = True

    def load_config(self) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '../config.ini')
        logger.debug(f"Loading configuration from {config_path}")
        config.read(config_path)
        return config

    def get_config(self, section: str) -> configparser.SectionProxy:
        if section in self.config:
            logger.debug(f"Fetching config section: {section}")
            return self.config[section]
        else:
            logger.error(f"Section '{section}' not found in configuration")
            raise KeyError(f"Section '{section}' not found in configuration")

    def get_string(self, section: str, key: str) -> str:
        value = self.config.get(section, key)
        logger.debug(f"Fetching string config: section={section}, key={key}, value={value}")
        return value
    
    @property
    def mongo(self) -> dict:
        value = {
            'host': self.config.get('mongo', 'host'),
            'port': self.config.getint('mongo', 'port'),
            'database_name': self.config.get('mongo', 'database_name')
        }
        logger.debug(f"Fetching mongo config: {value}")
        return value
    
    @property
    def punctuation(self) -> dict:
        value = {
            'end_sentence': self.config.get('punctuation', 'end_sentence').strip('[]').split(', '),
        }
        logger.debug(f"Fetching punctuation config: {value}")
        return value
