import pytest
from unittest.mock import patch
from pymongo.errors import PyMongoError
from bot.clean_queue import CleanQueue


@pytest.fixture
def clean_queue(mock_learn_queue_repository):
    return CleanQueue(learn_queue_repository=mock_learn_queue_repository, retry_delay=0)


def test_clean_queue_init(mock_learn_queue_repository):
    clean_queue = CleanQueue(
        learn_queue_repository=mock_learn_queue_repository, retry_delay=10)
    assert clean_queue.learn_queue == mock_learn_queue_repository
    assert clean_queue.retry_delay == 10


def test_clean_queue_run_successful(clean_queue: CleanQueue, mock_learn_queue_repository):
    mock_learn_queue_repository.clear.return_value = None

    with patch('logging.Logger.info') as mock_logger_info:
        clean_queue.run()
        mock_learn_queue_repository.clear.assert_called_once()
        mock_logger_info.assert_called_once_with(
            "Learn queue has been cleared successfully.")


def test_clean_queue_run_retry_on_failure(clean_queue: CleanQueue, mock_learn_queue_repository):
    mock_learn_queue_repository.clear.side_effect = [
        PyMongoError("Database error"), None]

    with patch('time.sleep', return_value=None) as _, patch('logging.Logger.error') as mock_logger_error, patch('logging.Logger.info') as mock_logger_info:
        clean_queue.run()
        assert mock_learn_queue_repository.clear.call_count == 2
        mock_logger_error.assert_called_once()
        mock_logger_info.assert_called_once_with(
            "Learn queue has been cleared successfully.")


def test_clean_queue_clean_up(clean_queue: CleanQueue, mock_learn_queue_repository):
    clean_queue._clean_up()
    mock_learn_queue_repository.clear.assert_called_once()


def test_clean_queue_run_log_error(clean_queue: CleanQueue, mock_learn_queue_repository):
    error_message = "Database error occurred during cleanup"
    mock_learn_queue_repository.clear.side_effect = PyMongoError(error_message)

    # Set max_retries to a finite number to prevent infinite loop
    clean_queue.max_retries = 3

    with patch('time.sleep', return_value=None) as _, patch('logging.Logger.error') as mock_logger_error:
        clean_queue.run()
        # Verify the logger was called with the correct formatted error message
        mock_logger_error.assert_any_call(
            "Database error occurred during cleanup: %s", mock_learn_queue_repository.clear.side_effect, exc_info=True
        )
        assert mock_learn_queue_repository.clear.call_count == 3
