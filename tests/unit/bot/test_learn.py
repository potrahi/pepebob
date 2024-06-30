import logging
from unittest.mock import patch
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pymongo.errors import PyMongoError
from core.repositories.learn_queue_repository import LearnQueueRepository, LearnItem
from core.services.learn_service import LearnService
from config import Config
from bot.learn import Learn


def test_init(learn_instance: Learn, mock_config: Config, mock_session: Session):
    assert learn_instance.config == mock_config
    assert learn_instance.max_no_item_count == 5
    assert learn_instance.session == mock_session
    assert isinstance(learn_instance.learn_queue_repository,
                      LearnQueueRepository)


@patch.object(Learn, 'process_item', return_value=False)
def test_run_no_items(mock_process_item, learn_instance: Learn):
    learn_instance.max_no_item_count = 3
    learn_instance.run()
    assert mock_process_item.call_count == 3


@patch('time.sleep', return_value=None)
@patch('bot.learn.Learn.process_item', side_effect=[True, False, False, True, False, False, False])
def test_run_some_items(mock_process_item, mock_sleep, learn_instance: Learn, caplog: pytest.LogCaptureFixture):
    learn_instance.max_no_item_count = 3

    with caplog.at_level(logging.DEBUG):
        learn_instance.run()

    expected_call_count = 7  # Adjusted to cover all calls
    assert mock_process_item.call_count == expected_call_count
    assert "No new learn items for a while, finishing execution." in caplog.text
    assert "No item count incremented: 3/3" in caplog.text


@patch('time.sleep', return_value=None)
@patch('bot.learn.Learn.process_item', side_effect=RuntimeError('Test error'))
def test_run_runtime_error(mock_process_item, mock_sleep, learn_instance: Learn):
    learn_instance.max_no_item_count = 2
    learn_instance.run()

    assert mock_process_item.call_count == 2
    assert mock_sleep.call_count == 2


@patch('bot.learn.Learn.learn', return_value=False)
def test_process_item_no_item(mock_learn, learn_instance: Learn):
    result = learn_instance.process_item()

    assert result is False
    mock_learn.assert_called_once_with(learn_instance.session.__enter__())


@patch('bot.learn.Learn.learn', side_effect=SQLAlchemyError('DB error'))
@patch('time.sleep', return_value=None)
def test_process_item_sqlalchemy_error(mock_sleep, mock_learn, learn_instance: Learn):
    result = learn_instance.process_item()

    assert result is False
    mock_learn.assert_called_once_with(learn_instance.session.__enter__())
    mock_sleep.assert_called_once()


@patch('bot.learn.Learn.learn', side_effect=PyMongoError('Mongo error'))
@patch('time.sleep', return_value=None)
def test_process_item_pymongo_error(mock_sleep, mock_learn, learn_instance: Learn):
    result = learn_instance.process_item()

    assert result is False
    mock_learn.assert_called_once_with(learn_instance.session.__enter__())
    mock_sleep.assert_called_once()


def test_learn_no_item(learn_instance: Learn):
    with patch.object(learn_instance.learn_queue_repository, 'pop', return_value=None):
        result = learn_instance.learn(learn_instance.session.__enter__())
    assert result is False


@patch('time.sleep', return_value=None)
def test_learn_with_item(mock_sleep, learn_instance: Learn):
    learn_item = LearnItem(message=["test message"], chat_id=1)
    with patch.object(learn_instance.learn_queue_repository, 'pop', return_value=learn_item):
        with patch.object(LearnService, 'learn_pair', return_value=None) as mock_learn_pair:
            result = learn_instance.learn(learn_instance.session.__enter__())
    assert result is True
    mock_learn_pair.assert_called_once()
    mock_sleep.assert_not_called()
