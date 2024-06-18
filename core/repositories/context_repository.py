"""
This module provides the ContextRepository class for managing context data
stored in a MongoDB collection. The repository includes methods for updating
and retrieving context records, ensuring efficient management of context data.
"""

from typing import List
from pymongo import MongoClient


class ContextRepository:
    """
    Repository class for managing context data stored in a MongoDB collection.
    Provides methods to retrieve and update context records.
    """

    def __init__(self, host: str = 'localhost', port: int = 27017, database_name: str = 'cache'):
        """
        Initialize the ContextRepository with the given MongoDB connection details.

        Args:
            host (str, optional): MongoDB host. Defaults to 'localhost'.
            port (int, optional): MongoDB port. Defaults to 27017.
            database_name (str, optional): Name of the database. Defaults to 'cache'.
        """
        self.client = MongoClient(host, port)
        self.db = self.client[database_name]
        self.collection = self.db['contexts']

    def _get_context_words(self, path: str) -> List[str]:
        """
        Helper method to retrieve the context words for a given path.

        Args:
            path (str): The unique identifier for the context.

        Returns:
            List[str]: List of words in the context.
        """
        doc = self.collection.find_one({'_id': path}, {'words': 1})
        if doc and 'words' in doc:
            return doc['words']
        return []

    def update_context(self, path: str, words: List[str]) -> None:
        """
        Update the context for a given path by adding new words to the existing context,
        ensuring the context does not exceed the specified limit.

        Args:
            path (str): The unique identifier for the context.
            words (List[str]): List of new words to add to the context.
        """
        existing_context = self._get_context_words(path)
        new_words = {word.lower()
                     for word in words if word.lower() not in existing_context}
        updated_context = list(new_words.union(existing_context))[:50]

        self.collection.update_one(
            {'_id': path},
            {'$set': {'words': updated_context}},
            upsert=True
        )

    def get_context(self, path: str, limit: int = 50) -> List[str]:
        """
        Retrieve the context words for a given path, limited to a specified number of words.

        Args:
            path (str): The unique identifier for the context.
            limit (int, optional): Maximum number of words to retrieve. Defaults to 50.

        Returns:
            List[str]: List of words in the context.
        """
        context = self._get_context_words(path)
        return context[:limit]
