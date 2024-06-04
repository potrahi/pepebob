import logging
from typing import List
from pymongo import MongoClient

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ContextRepository:
    def __init__(self, host: str = 'localhost', port: int = 27017, database_name: str = 'cache'):
        logger.debug(f"Initializing MongoClient with host={host}, port={port}, database_name={database_name}")
        self.client = MongoClient(host, port)
        self.db = self.client[database_name]
        self.collection = self.db['contexts']

    def update_context(self, path: str, words: List[str]) -> None:
        logger.debug(f"Updating context for path={path} with words={words}")
        ctx = self.get_context(path, 50)
        logger.debug(f"Current context for path={path}: {ctx}")
        
        filtered_words = list(set(word.lower() for word in words if word.lower() not in ctx))
        logger.debug(f"Filtered words: {filtered_words}")
        
        aggregated_words = (filtered_words + ctx)[:50]
        logger.debug(f"Aggregated words for update: {aggregated_words}")

        result = self.collection.update_one(
            {'_id': path},
            {'$set': {'words': aggregated_words}},
            upsert=True
        )
        logger.debug(f"Update result: {result.raw_result}")

    def get_context(self, path: str, limit: int = 50) -> List[str]:
        logger.debug(f"Fetching context for path={path} with limit={limit}")
        doc = self.collection.find_one({'_id': path})
        if doc and 'words' in doc:
            logger.debug(f"Found context: {doc['words'][:limit]}")
            return doc['words'][:limit]
        logger.debug("No context found")
        return []
