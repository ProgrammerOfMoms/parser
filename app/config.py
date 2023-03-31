"""Файлы конфигураций"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Класс для экпорта и хранения переменных окружения"""

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    DEBUG: bool

    class Config:
        env_file = "../.env"


settings = Settings()
