from typing import List
from pymongo import MongoClient

class ContextRepository:
    def __init__(self, host: str = 'localhost', port: int = 27017, database_name: str = 'cache'):
        self.client = MongoClient(host, port)
        self.db = self.client[database_name]
        self.collection = self.db['contexts']

    def update_context(self, path: str, words: List[str]) -> None:
        ctx = self.get_context(path, 50)
        filtered_words = list(set(word.lower() for word in words if word.lower() not in ctx))
        aggregated_words = (filtered_words + ctx)[:50]

        self.collection.update_one(
            {'_id': path},
            {'$set': {'words': aggregated_words}},
            upsert=True
        )

    def get_context(self, path: str, limit: int = 50) -> List[str]:
        doc = self.collection.find_one({'_id': path})
        if doc and 'words' in doc:
            return doc['words'][:limit]
        return []
