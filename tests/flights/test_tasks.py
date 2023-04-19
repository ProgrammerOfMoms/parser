"""Модуль с тестами задач Celery модуля flights"""

from datetime import date
import json
import os
import re
import shutil
from pathlib import Path
from unittest.mock import MagicMock

from pytest import MonkeyPatch, Session
from sqlalchemy import select
from app.flights.bl.helpers import get_flights_from_files
from app.flights.models import Flight

from app.flights.schemas import FILE_NAME_PATTERN
from app.flights.tasks import generate_file, process_incoming_flight_files, save_flights_to_db, \
    save_flights_to_json_files
from tests.helpers import BASE_DIR, generate_folders


class TestFileMove:
    """
    Тестирование переноса файлов из входящей директории
    """

    @generate_folders
    def test_generate_file(self) -> None:
        """Тестирование создания случайного входящего файла"""
        root_folder = Path(BASE_DIR) / "files"
        generate_file(str(root_folder))
        incoming_files = os.listdir(path=root_folder / "In")
        assert len(incoming_files) == 1

        incoming_file = incoming_files[0]
        assert bool(re.match(FILE_NAME_PATTERN, incoming_file)) is True

    @generate_folders
    def test_move_incoming_flight_files_ok(self,
                                           monkeypatch: MonkeyPatch) -> None:
        """
        Тестирование переноса успешного файла в папку "Ok"
        """
        in_folder = Path(BASE_DIR) / "files" / "In"
        test_folder = Path(BASE_DIR) / "incoming_files"
        file_name = "20221020_1234_OK.csv"
        test_file = test_folder / file_name
        shutil.copyfile(test_file, in_folder / file_name)

        monkeypatch.setattr("app.flights.tasks.group", MagicMock())
        count_of_files, _ = process_incoming_flight_files(str(in_folder))

        assert count_of_files == 1

        root_folder = in_folder.parent.absolute()
        ok_files = os.listdir(path=root_folder / "Ok")
        assert len(ok_files) == 1
        ok_file = ok_files[0]
        assert ok_file == file_name

        err_files = os.listdir(path=root_folder / "Err")
        assert len(err_files) == 0

        in_files = os.listdir(path=root_folder / "In")
        assert len(in_files) == 0

    @generate_folders
    def test_move_incoming_flight_file(self,
                                       monkeypatch: MonkeyPatch) -> None:
        """
        Тестирование переноса файла с невалидным названием
        """

        in_folder = Path(BASE_DIR) / "files" / "In"
        test_folder = Path(BASE_DIR) / "incoming_files"
        file_name = "20251020_1234_ERR.csv"
        test_file = test_folder / file_name
        shutil.copyfile(test_file, in_folder / file_name)

        monkeypatch.setattr("app.flights.tasks.group", MagicMock())
        count_of_files, _ = process_incoming_flight_files(str(in_folder))
        assert count_of_files == 0

        root_folder = in_folder.parent.absolute()
        err_files = os.listdir(path=root_folder / "Err")
        assert len(err_files) == 1

        in_files = os.listdir(path=root_folder / "In")
        assert len(in_files) == 0

    @generate_folders
    def test_move_incoming_flight_file_empty(self,
                                             monkeypatch: MonkeyPatch) -> None:
        """
        Тестирование переноса файла с невалидным содержимым
        """

        in_folder = Path(BASE_DIR) / "files" / "In"
        test_folder = Path(BASE_DIR) / "incoming_files"
        file_name = "20231020_1234_INV.csv"
        test_file = test_folder / file_name
        shutil.copyfile(test_file, in_folder / file_name)

        monkeypatch.setattr("app.flights.tasks.group", MagicMock())
        count_of_files, _ = process_incoming_flight_files(str(in_folder))

        assert count_of_files == 0

        root_folder = in_folder.parent.absolute()
        err_files = os.listdir(path=root_folder / "Err")
        assert len(err_files) == 1


class TestFileContent:
    """Тестирование содержимого файлов"""

    @generate_folders
    def test_json_file_content(self) -> None:
        """
        Тестирование содержимого json файла
        """
        in_folder = Path(BASE_DIR) / "files" / "In"
        test_folder = Path(BASE_DIR) / "incoming_files"
        file_name = "20221020_1234_OK.csv"
        test_file = test_folder / file_name
        shutil.copyfile(test_file, in_folder / file_name)

        root_folder = in_folder.parent.absolute()
        out_folder = root_folder / "Out"

        flights, _ = get_flights_from_files([str(in_folder / file_name)])
        flights_dict = [flight.json() for flight in flights]
        save_flights_to_json_files(flights_dict, str(out_folder))

        json_file_name = "20221020_1234_OK.json"

        out_files = os.listdir(path=out_folder)
        assert len(out_files) == 1
        out_file = out_files[0]
        assert out_file == json_file_name

        json_file_path = out_folder / json_file_name
        with open(json_file_path, encoding="utf-8") as json_file:
            row_content = json_file.read()
            content = json.loads(row_content)

        test_data = {
            "flt": 1234,
            "date": "2022-10-20",
            "dep": "OK",
            "prl": [
                {
                    "num": 1,
                    "surname": "IVANOV",
                    "firstname": "IVAN",
                    "bdate": "1973-11-11"
                },
                {
                    "num": 2,
                    "surname": "PETROV",
                    "firstname": "ALEXANDER",
                    "bdate": "1979-07-13"
                },
                {
                    "num": 3,
                    "surname": "BOSHIROV",
                    "firstname": "RUSLAN",
                    "bdate": "1978-04-12"
                }
            ]
        }
        assert test_data == content


class TestFileDbSave:
    """Тестирование сохранения в БД данных о файле"""

    @generate_folders
    def test_save_flights_to_db(self,
                                session: Session,
                                monkeypatch: MonkeyPatch) -> None:
        """Тест сохранения данных в БД"""
        in_folder = Path(BASE_DIR) / "files" / "In"
        test_folder = Path(BASE_DIR) / "incoming_files"
        file_name = "20221020_1234_OK.csv"
        test_file = test_folder / file_name
        shutil.copyfile(test_file, in_folder / file_name)
        monkeypatch.setattr("app.flights.tasks.SessionLocal", lambda: session)

        flights, _ = get_flights_from_files([str(in_folder / file_name)])
        flights_dict = [flight.json() for flight in flights]

        save_flights_to_db(flights_dict)
        db_flights = list(session.execute(select(Flight)).scalars())
        assert len(db_flights) == 1
        db_flight: Flight = db_flights[0]
        assert db_flight.flt == 1234
        assert db_flight.file_name == file_name
        assert db_flight.dep == "OK"
        assert db_flight.depdate == date(2022, 10, 20)
