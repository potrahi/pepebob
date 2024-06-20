"""
This module contains unit tests for the LearnQueueRepository class.
"""

from unittest.mock import patch
import pytest
import mongomock
from core.repositories.learn_queue_repository import LearnQueueRepository

@pytest.fixture
def mock_db():
    """
    Fixture to set up an in-memory MongoDB using mongomock.
    """
    client = mongomock.MongoClient()
    db = client['cache']
    yield db

@pytest.fixture
def learn_queue_repo(mock_db: mongomock.Database):
    """
    Fixture to set up the LearnQueueRepository with a patched MongoDB client.
    """
    with patch('core.repositories.learn_queue_repository.MongoClient', return_value=mock_db.client):
        repo = LearnQueueRepository()
        repo.collection.delete_many({})
        yield repo

def test_push(learn_queue_repo: LearnQueueRepository):
    """
    Test the push method to ensure an item is correctly added to the queue.
    """
    message = ['test message']
    chat_id = 12345

    learn_queue_repo.push(message, chat_id)

    result = learn_queue_repo.collection.find_one({'chat_id': chat_id})
    assert result is not None
    assert result['message'] == message
    assert result['chat_id'] == chat_id

def test_pop_empty_queue(learn_queue_repo: LearnQueueRepository):
    """
    Test the pop method when the queue is empty, ensuring it returns None.
    """
    result = learn_queue_repo.pop()
    assert result is None

def test_pop_non_empty_queue(learn_queue_repo: LearnQueueRepository):
    """
    Test the pop method when the queue has an item, ensuring it retrieves and removes the item.
    """
    message = ['test message']
    chat_id = 12345

    learn_queue_repo.push(message, chat_id)
    result = learn_queue_repo.pop()

    assert result is not None
    assert result.message == message
    assert result.chat_id == chat_id

def test_clear(learn_queue_repo: LearnQueueRepository):
    """
    Test the clear method to ensure all items are removed from the queue.
    """
    message1 = ['message 1']
    chat_id1 = 12345
    message2 = ['message 2']
    chat_id2 = 67890

    learn_queue_repo.push(message1, chat_id1)
    learn_queue_repo.push(message2, chat_id2)
    learn_queue_repo.clear()

    result = learn_queue_repo.collection.find_one({})
    assert result is None
