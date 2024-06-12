"""
This module provides the LearnQueueRepository class for managing a learning
queue stored in a MongoDB collection. It also includes the LearnItem class
to represent items in the learning queue.
"""

import logging
from typing import List, Optional
from pymongo import MongoClient
from config import Config


class LearnItem:
    """
    A class to represent an item in the learning queue.
    """

    def __init__(self, message: List[str], chat_id: int):
        """
        Initialize a LearnItem.

        Args:
            message (List[str]): The message content.
            chat_id (int): The chat ID associated with the message.
        """
        self.message = message
        self.chat_id = chat_id


class LearnQueueRepository:
    """
    Repository class for managing a learning queue stored in a MongoDB collection.
    """

    _client = None

    def __init__(self):
        """
        Initialize the LearnQueueRepository with the given MongoDB connection details.
        """
        if not LearnQueueRepository._client:
            config = Config()
            LearnQueueRepository._client = MongoClient(
                host=config.cache.host, port=config.cache.port)
        self.client = LearnQueueRepository._client
        config = Config()
        self.db = self.client[config.cache.name]  # pylint: disable=unsubscriptable-object
        self.collection = self.db["learn_queue"]

    def push(self, message: List[str], chat_id: int) -> None:
        """
        Push a new item onto the learning queue.

        Args:
            message (List[str]): The message content.
            chat_id (int): The chat ID associated with the message.
        """
        item = LearnItem(message, chat_id)
        self.collection.insert_one(
            {"message": item.message, "chat_id": item.chat_id})

    def pop(self) -> Optional[LearnItem]:
        """
        Pop an item from the learning queue.

        Returns:
            Optional[LearnItem]: The popped LearnItem, or None if the queue is empty.
        """
        doc = self.collection.find_one_and_delete({})
        if doc:
            try:
                return LearnItem(message=doc['message'], chat_id=doc['chat_id'])
            except KeyError as e:
                logging.error(
                    "Failed to pop item from queue: missing key %s", e)
                return None
        return None

    def clear(self) -> None:
        """
        Clear all records in the learn_queue collection.
        """
        self.collection.delete_many({})
