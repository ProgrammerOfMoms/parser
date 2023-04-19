import logging
import os
from pathlib import Path
import random
import string
from datetime import date
from typing import TypeAlias

from pydantic import ValidationError

from app.common.helpers import get_file_name_with_ext

from app.flights.schemas import FlightFullIn


FlightsFileMap: TypeAlias = tuple[list[FlightFullIn], dict[str, str]]

logger = logging.getLogger(__name__)


def generate_random_date(start_date: date, end_date: date | None = None) -> date:
    """Генерирует случайную дату в диапозоне от start_date до end_date"""
    if end_date is None:
        end_date = date.today()
    return start_date + (end_date - start_date) * random.random()


def generate_flight_file_name() -> str:
    """
    Генерирует случайное название файла по паттерну
    {YYYYMMDD}_{FLIGHT_NUM}_{DEPARTMENT}.csv
    """
    gen_date = generate_random_date(date(1970, 1, 1)).strftime("%Y%m%d")
    gen_flight_number = random.randint(1, 10000)
    letters = random.choices(string.ascii_uppercase, k=random.randint(3, 5))
    gen_department_name = "".join(letters)
    return f"{gen_date}_{gen_flight_number}_{gen_department_name}.csv"


def generate_passenger() -> tuple[str, str, str]:
    """
    Сгенерировать данные случайного пассажира
    На выходе кортеж (ФАМИЛИЯ, ИМЯ, ДАТА РОЖДЕНИЯ)
    """
    gen_date = generate_random_date(date(1970, 1, 1), date(2010, 1, 1))
    return (
        "".join(random.choices(string.ascii_uppercase,
                               k=random.randint(5, 9))),
        "".join(random.choices(string.ascii_uppercase,
                               k=random.randint(5, 9))),
        gen_date.strftime("%d%b%y").upper()
    )


def is_valid_flight_file(flight_file_path: str) -> bool:
    """
    Валидация входящего файла авиаперелета.
    :param flight_file_path: Путь до проверяемого файла.
    """
    _, ext = get_file_name_with_ext(flight_file_path)
    if ext != ".csv":
        return False
    return True


def create_json_files_by_flights(flights: list[FlightFullIn],
                                 folder: str) -> None:
    """
    Записывает объекты авиаперелетов в файлы.
    :param flights: Авиаперелеты.
    :param folder: Директория, в которую сохранятся файлы.
    """
    folder_path = Path(folder)
    for flight in flights:
        file_name_wo_ext, _ = os.path.splitext(flight.file_name)
        output_file_name = f"{file_name_wo_ext}.json"
        output_file_path = folder_path / output_file_name
        with open(output_file_path, "w",
                  encoding="utf-8") as output_file:
            output_file.write(flight.to_json(exclude={"file_name"},
                                             replace={"depdate": "date"}))


def get_flights_from_files(incoming_files: list[str]) -> FlightsFileMap:
    """
    Получить список объектов авиаперелетов из файлов.
    :param incoming_files: Спсиок файлов.
    """
    file_map = {}
    flights: list[FlightFullIn] = []
    for incoming_file in incoming_files:
        root_folder = Path(incoming_file).parent.parent.absolute()
        ok_folder = root_folder / "Ok"
        err_folder = root_folder / "Err"
        _, file_name = os.path.split(incoming_file)
        if not is_valid_flight_file(incoming_file):
            file_map[incoming_file] = str(err_folder / file_name)
            continue
        try:
            flight = FlightFullIn.from_csv_file(incoming_file)
        except ValidationError as ex:
            logger.warning(f"Can't process file {incoming_file}"
                           f"Validation error: {ex.json()}")
            file_map[incoming_file] = str(err_folder / file_name)
            continue
        file_map[incoming_file] = str(ok_folder / file_name)
        flights.append(flight)
    return flights, file_map
