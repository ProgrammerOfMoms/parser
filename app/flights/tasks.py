import csv
import os
import random
from pathlib import Path

from celery import group

from app.common.helpers import move_files_by_map
from app.db import SessionLocal
from app.flights.bl.crud import create_flights_bulk
from app.flights.bl.helpers import (create_json_files_by_flights,
                                    generate_flight_file_name,
                                    generate_passenger, get_flights_from_files)
from app.flights.schemas import FlightFullIn
from app.logging import logged
from app.worker import celery


@celery.task
@logged
def generate_file(root_folder: str) -> str:
    """
    Генерация случайного csv файла.
    :param root_folder: Корневой каталог.
    """
    file_name = generate_flight_file_name()
    file_path = os.path.join(root_folder, f"In/{file_name}")
    header = ("num", "surname", "firstname", "bdate")
    passengers = (generate_passenger()
                  for _ in range(random.randint(10, 1000)))
    with open(file_path, "w") as in_file:
        csv_writer = csv.writer(in_file, quoting=csv.QUOTE_ALL, delimiter=";")
        csv_writer.writerow(header)
        for idx, passenger in enumerate(passengers):
            csv_writer.writerow((idx+1, ) + passenger)
    return file_name


@celery.task
@logged
def save_flights_to_json_files(row_flights: list[str], folder: str) -> None:
    """
    Записывает объекты авиаперелетов в файлы.
    :param row_flights: Авиаперелеты.
    :param folder: Директория, в которую сохранятся файлы.
    """
    flights = [FlightFullIn.parse_raw(flight) for flight in row_flights]
    create_json_files_by_flights(flights, folder)


@celery.task
@logged
def save_flights_to_db(row_flights: list[str]) -> None:
    """
    Сохранить данные о авиаперелетах в БД
    :param flights: Авиаперелеты.
    """
    flights = [FlightFullIn.parse_raw(flight) for flight in row_flights]
    with SessionLocal() as session:
        create_flights_bulk(session, flights)
        session.commit()


@celery.task
@logged
def process_incoming_flight_files(folder: str) -> tuple[int, str | None]:
    """
    Получает входящие файлы о полетах и обрабатывает их.
    :param folder: Путь до директории, которую необходимо слушать.
    :return: Количество обработанных файлов.
    """
    incoming_files = os.listdir(path=folder)
    if not incoming_files:
        return 0, None

    root_folder = Path(folder).parent.absolute()
    in_folder = Path(folder)
    out_folder = root_folder / "Out"

    incoming_file_paths = [str(in_folder / incoming_file)
                           for incoming_file in incoming_files]
    flights, file_map = get_flights_from_files(incoming_file_paths)
    move_files_by_map(file_map)

    result_id = None
    if flights:
        flights_dict = [flight.json() for flight in flights]
        job = group([save_flights_to_db.s(flights_dict),
                    save_flights_to_json_files.s(flights_dict,
                                                 str(out_folder))])
        result = job.apply_async()
        result.save()
        result_id = result.id

    return len(flights), result_id
