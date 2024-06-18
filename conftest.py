import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.entities.base_entity import Base


@pytest.fixture(scope='module')
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope='module')
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(scope='function')
def dbsession(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    session_obj = sessionmaker(bind=connection)
    session = session_obj()
    yield session
    session.close()
    transaction.rollback()
    connection.close()
