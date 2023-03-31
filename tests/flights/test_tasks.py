"""Модуль с тестами задач Celery модуля flights"""

import os
import re
import shutil
from pathlib import Path

from celery.result import GroupResult

from app.flights.schemas import FILE_NAME_PATTERN
from app.flights.tasks import generate_file, process_incoming_flight_files
from tests.helpers import BASE_DIR, generate_folders, wait_subtasks


@generate_folders
def test_generate_file() -> None:
    """Тестирование создания случайного входящего файла"""
    root_folder = Path(BASE_DIR) / "files"
    generate_file(str(root_folder))
    incoming_files = os.listdir(path=root_folder / "In")
    assert len(incoming_files) == 1

    incoming_file = incoming_files[0]
    assert bool(re.match(FILE_NAME_PATTERN, incoming_file)) is True


@generate_folders
def test_process_incoming_flight_files_ok() -> None:
    """Тестирование обработки валидного входящего файла"""
    in_folder = Path(BASE_DIR) / "files" / "In"
    test_folder = Path(BASE_DIR) / "incoming_files"
    file_name = "20221020_1234_OK.csv"
    test_file = test_folder / file_name
    shutil.copyfile(test_file, in_folder / file_name)

    count_of_files, group_uuid = process_incoming_flight_files(str(in_folder))
    wait_subtasks(group_uuid)

    assert count_of_files == 1

    root_folder = in_folder.parent.absolute()
    ok_files = os.listdir(path=root_folder / "Ok")
    assert len(ok_files) == 1
    ok_file = ok_files[0]
    assert ok_file == file_name

    err_files = os.listdir(path=root_folder / "Err")
    assert len(err_files) == 0

    out_files = os.listdir(path=root_folder / "Out")
    assert len(out_files) == 1
    out_file = out_files[0]
    assert out_file == "20221020_1234_OK.json"

    in_files = os.listdir(path=root_folder / "In")
    assert len(in_files) == 0


@generate_folders
def test_process_incoming_flight_files_err() -> None:
    """Тестирование обработки невалидного входящего файла"""

    in_folder = Path(BASE_DIR) / "files" / "In"
    test_folder = Path(BASE_DIR) / "incoming_files"
    file_name = "20251020_1234_ERR.csv"
    test_file = test_folder / file_name
    shutil.copyfile(test_file, in_folder / file_name)

    count_of_files, group_uuid = process_incoming_flight_files(str(in_folder))
    wait_subtasks(group_uuid)
    assert count_of_files == 0

    root_folder = in_folder.parent.absolute()
    err_files = os.listdir(path=root_folder / "Err")
    assert len(err_files) == 1


@generate_folders
def test_process_incoming_flight_files_err2() -> None:
    """Тестирование обработки невалидного входящего файла"""

    in_folder = Path(BASE_DIR) / "files" / "In"
    test_folder = Path(BASE_DIR) / "incoming_files"
    file_name = "20231020_1234_INV.csv"
    test_file = test_folder / file_name
    shutil.copyfile(test_file, in_folder / file_name)

    count_of_files, group_uuid = process_incoming_flight_files(str(in_folder))
    wait_subtasks(group_uuid)

    assert count_of_files == 0

    root_folder = in_folder.parent.absolute()
    err_files = os.listdir(path=root_folder / "Err")
    assert len(err_files) == 1
