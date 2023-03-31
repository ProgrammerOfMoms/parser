from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database, drop_database

from app.main import app as fastapi_app
from app.db import Base
from app.dependencies import get_db
from app.flights.models import *


@pytest.fixture(scope="session")
def postgres_url() -> Generator[str, None, None]:
    db_url = ("postgresql+psycopg2://postgres:postgres"
              "@db:5432/test_db")
    yield db_url


@pytest.fixture(scope="session")
def db_engine(postgres_url: str) -> Generator[Engine, None, None]:
    engine = create_engine(postgres_url)
    if not database_exists(engine.url):
        create_database(engine.url)

    Base.metadata.create_all(bind=engine)
    yield engine
    drop_database(engine.url)


@pytest.fixture(scope="function")
def session(db_engine: Engine) -> Generator[Session, None, None]:
    try:
        connection = db_engine.connect()
        transaction = connection.begin()
        db = Session(bind=connection)
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(session: Session) -> Generator[TestClient, None, None]:
    fastapi_app.dependency_overrides[get_db] = lambda: session

    with TestClient(fastapi_app) as test_client:
        yield test_client
