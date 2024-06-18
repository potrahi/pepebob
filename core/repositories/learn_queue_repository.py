import json
from typing import List, Optional
from pymongo import MongoClient
from config import Config

class LearnItem:
    def __init__(self, message: List[str], chat_id: int):
        self.message = message
        self.chat_id = chat_id

    def to_json(self) -> str:
        return json.dumps({"message": self.message, "chat_id": self.chat_id})

    @staticmethod
    def from_json(data: str) -> 'LearnItem':
        json_data = json.loads(data)
        return LearnItem(json_data['message'], json_data['chat_id'])

class LearnQueueRepository:
    _client = None
    
    def __init__(self):
        if not LearnQueueRepository._client:
            config = Config()
            LearnQueueRepository._client = MongoClient(host=config.cache.host, port=config.cache.port)
        self.client = LearnQueueRepository._client
        config = Config()
        self.db = self.client[config.cache.name] # pylint: disable=unsubscriptable-object
        self.collection = self.db["learn_queue"]

    def push(self, message: List[str], chat_id: int) -> None:
        item = LearnItem(message, chat_id)
        self.collection.insert_one({"message": item.message, "chat_id": item.chat_id})

    def pop(self) -> Optional[LearnItem]:
        doc = self.collection.find_one_and_delete({})
        if doc:
            try:
                return LearnItem(message=doc['message'], chat_id=doc['chat_id'])
            except (json.JSONDecodeError, KeyError) as e:
                return None
        return None

    def clear(self):
        """Clear all records in the learn_queue collection."""
        self.collection.delete_many({})