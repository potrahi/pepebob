from unittest.mock import patch
import pytest
import mongomock
from core.repositories.context_repository import ContextRepository

@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    db = client['cache']
    yield db

@pytest.fixture
def context_repo(mock_db: mongomock.Database):
    with patch(
        'core.repositories.context_repository.MongoClient', 
        return_value=mock_db.client
    ):
        yield ContextRepository()

def test_update_context_new_path(context_repo: ContextRepository):
    path = 'test_path'
    words = ['hello', 'world', 'example']

    context_repo.update_context(path, words)

    result = context_repo.collection.find_one({'_id': path})
    assert result is not None
    assert set(result['words']) == set(words)

def test_update_context_existing_path(context_repo: ContextRepository):
    path = 'test_path'
    initial_words = ['hello', 'world']
    new_words = ['example', 'world', 'new']

    context_repo.collection.insert_one({'_id': path, 'words': initial_words})
    context_repo.update_context(path, new_words)

    result = context_repo.collection.find_one({'_id': path})
    assert result is not None
    expected_words = set(initial_words + ['example', 'new'])
    assert set(result['words']) == expected_words

def test_update_context_limit(context_repo: ContextRepository):
    path = 'test_path'
    initial_words = ['word' + str(i) for i in range(45)]
    new_words = ['new' + str(i) for i in range(10)]

    context_repo.collection.insert_one({'_id': path, 'words': initial_words})
    context_repo.update_context(path, new_words)

    result = context_repo.collection.find_one({'_id': path})
    assert result is not None
    assert len(result['words']) == 50

def test_get_context(context_repo: ContextRepository):
    path = 'test_path'
    words = ['hello', 'world', 'example']

    context_repo.collection.insert_one({'_id': path, 'words': words})
    result = context_repo.get_context(path)

    assert result == words[:50]

def test_get_context_with_limit(context_repo: ContextRepository):
    path = 'test_path'
    words = ['word' + str(i) for i in range(100)]

    context_repo.collection.insert_one({'_id': path, 'words': words})
    result = context_repo.get_context(path, limit=10)

    assert result == words[:10]

def test_get_context_non_existing_path(context_repo: ContextRepository):
    path = 'non_existing_path'

    result = context_repo.get_context(path)

    assert result == []

def test_get_context_words_existing_path(context_repo: ContextRepository):
    path = 'test_path'
    words = ['hello', 'world', 'example']

    context_repo.collection.insert_one({'_id': path, 'words': words})
    result = context_repo._get_context_words(path)

    assert result == words

def test_get_context_words_non_existing_path(context_repo: ContextRepository):
    path = 'non_existing_path'

    result = context_repo._get_context_words(path)

    assert result == []

