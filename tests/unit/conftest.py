import os
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.entities.base_entity import Base

# Set up the test database URL from the environment variable
load_dotenv()

# PostgreSQL connection string
DATABASE_ENGINE = os.getenv('DATABASE_ENGINE')
DATABASE_HOST = os.getenv('DATABASE_HOST_TEST')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')

DATABASE_URL = (
    f"{DATABASE_ENGINE}://{DATABASE_USER}:{DATABASE_PASSWORD}"
    f"@{DATABASE_HOST}/{DATABASE_NAME}"
)


@pytest.fixture(scope='module')
def engine():
    return create_engine(DATABASE_URL)


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
