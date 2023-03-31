"""Модуль с хелпперами для тестов"""

import os
import shutil
import time
from functools import wraps
from pathlib import Path

from celery.result import GroupResult


BASE_DIR = Path(__file__).parent


def generate_folders(func):
    """
    Декоратор для создания директорий для
    хранения файлов.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        root_folder = Path(BASE_DIR) / "files"
        os.makedirs(root_folder)
        files_folders = (
            root_folder / "In",
            root_folder / "Out",
            root_folder / "Err",
            root_folder / "Ok"
        )
        for folder in files_folders:
            os.makedirs(folder)

        try:
            return func(*args, **kwargs)
        finally:
            shutil.rmtree(root_folder)
    return wrapper


def wait_subtasks(group_uuid: str | None) -> None:
    """
    Ожидает выполнения всех подзадач
    :param group_uuid: Идентификатор группы задач Celery
    """
    if group_uuid is not None:
        group_result = GroupResult.restore(group_uuid)
        while not group_result.ready():
            time.sleep(0.5)
