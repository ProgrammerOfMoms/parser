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
    LOG_LEVEL: str

    TASK_GENERATE_FILE_SEC: int
    TASK_PROCESS_INCOMING_FILES_SEC: int

    class Config:
        env_file = "../.env"


settings = Settings()
