from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

DATABASE_URL = ("postgresql://"
                f"{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
                f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, bind=engine)

Base = declarative_base()


def get_session_pool(db_url: str | None = None) -> None:
    """Получить сессию БД"""
    if db_url is None:
        db_url = DATABASE_URL
    inner_engine = create_engine(db_url)
    session_pool = sessionmaker(autoflush=False, bind=inner_engine)
    return session_pool
