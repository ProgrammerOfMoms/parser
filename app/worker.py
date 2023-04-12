import logging
import os
from pathlib import Path

from celery import Celery  # type: ignore
from celery.signals import after_setup_logger  # type: ignore

from app.config import settings
from app.logging import BASE_DIR

MODULES = ("app.flights", )

celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND


@after_setup_logger.connect
def on_after_setup_logger(logger: logging.Logger, *args, **kwargs) -> None:
    """Конфигурирем логгер Celery"""
    fmt = logging.Formatter("%(levelname)s %(asctime)s %(name)s %(message)s")
    fh = logging.FileHandler(os.path.join(BASE_DIR, 'logs/celery.log'))
    fh.setLevel(settings.LOG_LEVEL)
    fh.setFormatter(fmt)
    logger.addHandler(fh)


celery.autodiscover_tasks(lambda: MODULES)

celery.conf.beat_schedule = {
    "process-incoming-files": {
        "task": "app.flights.tasks.process_incoming_flight_files",
        "schedule": settings.TASK_PROCESS_INCOMING_FILES_SEC,
        "args": (str(Path(BASE_DIR) / "app/files/In"), )
    }
}

if settings.DEBUG:
    celery.conf.beat_schedule.update({
        "generate-file": {
            "task": "app.flights.tasks.generate_file",
            "schedule": settings.TASK_GENERATE_FILE_SEC,
            "args": (str(Path(BASE_DIR) / "app/files/"), )
        }
    })

celery.conf.timezone = 'UTC'
