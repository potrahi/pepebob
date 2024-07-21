import pytest
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError
from bot.clean_pairs import CleanPairs


def test_initialization_with_repository(clean_pairs, pair_repo):
    assert clean_pairs.pair_repository == pair_repo
    assert clean_pairs.retry_delay == 0


def test_initialization_without_repository():
    with patch('bot.clean_pairs.PairRepository') as MockPairRepository:
        cp = CleanPairs()
        assert cp.pair_repository == MockPairRepository.return_value
        assert cp.retry_delay == 5


def test_run_clean_up_called(clean_pairs, mock_session, mock_config):
    with patch.object(clean_pairs, 'clean_up', side_effect=[None, Exception("break loop")]) as mock_clean_up:
        with patch('time.sleep', return_value=None):
            with pytest.raises(Exception, match="break loop"):
                clean_pairs.run(mock_session, mock_config)
            assert mock_clean_up.call_count == 2
            mock_clean_up.assert_any_call(mock_session, mock_config)


def test_clean_up_successful_removal(clean_pairs, mock_session, mock_config, pair_repo):
    with patch.object(pair_repo, 'remove_old', return_value=[1, 2, 3]):
        with patch('logging.Logger.info') as mock_logger_info:
            clean_pairs.clean_up(mock_session, mock_config)
            mock_logger_info.assert_called_with(
                "Removed %d pairs: %s", 3, '1, 2, 3'
            )


def test_clean_up_no_pairs_to_remove(clean_pairs, mock_session, mock_config, pair_repo):
    with patch.object(pair_repo, 'remove_old', return_value=[]):
        with patch('logging.Logger.info') as mock_logger_info:
            clean_pairs.clean_up(mock_session, mock_config)
            mock_logger_info.assert_called_with("No pairs to remove.")


def test_clean_up_exception_handling(clean_pairs, mock_session, mock_config, pair_repo):
    with patch.object(pair_repo, 'remove_old', side_effect=SQLAlchemyError("DB error")):
        with patch.object(clean_pairs, '_handle_exception') as mock_handle_exception:
            with pytest.raises(SQLAlchemyError):
                clean_pairs.clean_up(mock_session, mock_config)
            mock_handle_exception.assert_called_once()


def test_handle_exception_logging(clean_pairs):
    exceptions = [
        (SQLAlchemyError("DB error"), "Database error occurred during cleanup: %s"),
        (ValueError("Value error"), "Configuration error occurred during cleanup: %s"),
        (RuntimeError("Runtime error"), "Runtime error occurred during cleanup: %s"),
        (OSError("OS error"), "OS error occurred during cleanup: %s")
    ]

    for exc, expected_msg in exceptions:
        with patch('logging.Logger.error') as mock_logger_error:
            clean_pairs._handle_exception(exc)
            mock_logger_error.assert_called_with(
                expected_msg, exc, exc_info=True)


def test_handle_unexpected_exception_logging(clean_pairs):
    unexpected_exception = Exception("Unexpected error")
    with patch('logging.Logger.error') as mock_logger_error:
        clean_pairs._handle_exception(unexpected_exception)
        mock_logger_error.assert_called_with(
            "Unexpected error occurred during cleanup: %s", unexpected_exception, exc_info=True)
