import logging
from typing import Optional
import json
from pymongo import MongoClient
from core.core_config import CoreConfig

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class WordForDeletion:
    def __init__(self, word_id: int, name: str):
        self.word_id = word_id
        self.name = name

    def to_json(self) -> str:
        return json.dumps({"word_id": self.word_id, "name": self.name})

    @staticmethod
    def from_json(data: str) -> 'WordForDeletion':
        json_data = json.loads(data)
        return WordForDeletion(json_data['word_id'], json_data['name'])

class WordDeletionQueueRepository:
    def __init__(self):
        logger.debug("Initializing WordDeletionQueueRepository")
        config = CoreConfig()
        mongo_config = config.mongo
        logger.debug(f"MongoDB Config: host={mongo_config['host']}, port={mongo_config['port']}, database_name={mongo_config['database_name']}")
        self.client = MongoClient(host=mongo_config['host'], port=mongo_config['port'])
        self.db = self.client[mongo_config['database_name']]
        self.collection = self.db["words_for_deletion"]

    def push(self, word_id: int, name: str) -> None:
        logger.debug(f"Pushing word for deletion: word_id={word_id}, name={name}")
        item = WordForDeletion(word_id, name)
        self.collection.insert_one({"word_id": item.word_id, "name": item.name})
        logger.info(f"Word pushed for deletion: word_id={word_id}, name={name}")

    def pop(self) -> Optional[WordForDeletion]:
        logger.debug("Popping word for deletion from queue")
        doc = self.collection.find_one_and_delete({})
        if doc:
            try:
                logger.debug(f"Document found: {doc}")
                return WordForDeletion(word_id=doc['word_id'], name=doc['name'])
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error decoding document: {e}")
                return None
        logger.debug("No document found")
        return None
